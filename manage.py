#!/usr/bin/env python3
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time

PACKAGE = Path(__file__).resolve().parent
SUPPORT = Path.home() / 'Library/Application Support/Llama/ChineseWebUI'
TARGET = SUPPORT / 'b12375'
BACKUP = SUPPORT / 'original-webui.json'
DOMAIN = 'app.llama.Llama'
KEY = 'customWebUIDirectory'
APP = '/Applications/Llama.app'


def run(*args, **kwargs):
    return subprocess.run(args, text=True, capture_output=True, **kwargs)


def current_path():
    result = run('/usr/bin/defaults', 'read', DOMAIN, KEY)
    return result.stdout.strip() if result.returncode == 0 else None


def write_path(value):
    if value is None:
        run('/usr/bin/defaults', 'delete', DOMAIN, KEY)
    else:
        result = run('/usr/bin/defaults', 'write', DOMAIN, KEY, '-string', value)
        if result.returncode:
            raise RuntimeError('无法保存 Llama 的界面设置。')


def restart():
    result = run('/usr/bin/pgrep', '-f', '^/Applications/Llama.app/Contents/MacOS/Llama$')
    for pid in result.stdout.split():
        os.kill(int(pid), signal.SIGTERM)
        for _ in range(50):
            try:
                os.kill(int(pid), 0)
            except ProcessLookupError:
                break
            time.sleep(0.1)
        else:
            raise RuntimeError('Llama 尚未退出，请手动退出后重新打开。')
    result = run('/usr/bin/open', APP)
    if result.returncode:
        raise RuntimeError('请从“应用程序”中手动打开 Llama。')


def install():
    engine = Path.home() / '.llama-app/llama'
    if not engine.is_file():
        raise RuntimeError('未找到 Llama 自带的模型引擎。请先启动官方应用。')
    version = run(str(engine), '--version')
    if not re.search(r'build 12375, commit 9d25e0014', version.stdout + version.stderr):
        raise RuntimeError('引擎版本与此补丁不符。此补丁仅适用于 b12375，请先重新适配。')
    manifest = json.loads((PACKAGE / 'files.sha256.json').read_text())
    for name, digest in manifest.items():
        file = PACKAGE / 'dist' / name
        if not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest() != digest:
            raise RuntimeError('补丁文件校验失败，请使用完整补丁包。')
    SUPPORT.mkdir(parents=True, exist_ok=True)
    if not BACKUP.exists():
        BACKUP.write_text(json.dumps({'previousPath': current_path()}, ensure_ascii=False))
    matches = TARGET.is_dir() and all(
        (TARGET / name).is_file() and
        hashlib.sha256((TARGET / name).read_bytes()).hexdigest() == digest
        for name, digest in manifest.items()
    )
    if not matches:
        if TARGET.exists():
            existing = TARGET.with_name('b12375-previous-' + str(time.time_ns()))
            TARGET.rename(existing)
        shutil.copytree(PACKAGE / 'dist', TARGET)
    write_path(str(TARGET))
    restart()
    print('中文界面已启用。请刷新聊天页面。')
    print('官方应用和引擎仍可正常更新；更新后请重新适配此补丁。')


def restore():
    now = current_path()
    if now is None:
        print('当前已使用官方界面。')
        return
    if not Path(now).is_relative_to(SUPPORT):
        raise RuntimeError('当前使用的是其他自定义界面，已保留该设置。')
    if not BACKUP.exists():
        raise RuntimeError('缺少原界面设置备份，已保留当前设置。')
    previous = json.loads(BACKUP.read_text())['previousPath']
    write_path(previous)
    restart()
    print('已恢复安装补丁前的界面。请刷新聊天页面。')


if __name__ == '__main__':
    try:
        action = sys.argv[1] if len(sys.argv) > 1 else ''
        if action == 'install':
            install()
        elif action == 'restore':
            restore()
        else:
            raise RuntimeError('请选择“启用中文界面”或“恢复原界面”。')
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
