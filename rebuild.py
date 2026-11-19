#!/usr/bin/env python3
"""Build the pinned Chinese Web UI without changing an installed application."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent


def run(args, cwd=None, env=None):
    subprocess.run(args, cwd=cwd, env=env, check=True)


def align_assets(dist, embedded_name):
    bundles = list((dist / '_app/immutable').glob('bundle.*.js'))
    if len(bundles) != 1:
        raise RuntimeError('Expected exactly one client bundle')
    source = bundles[0]
    original_name = source.name
    destination = source.with_name(embedded_name)
    if source != destination:
        source.rename(destination)
    for name in ('index.html', 'sw.js'):
        p = dist / name
        p.write_text(p.read_text().replace(original_name, embedded_name))
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    worker = dist / 'sw.js'
    pattern = r'(url:["\'](?:\./)?_app/immutable/' + re.escape(embedded_name) + r'["\'],revision:)null'
    text, count = re.subn(pattern, lambda m: m[1] + json.dumps(digest), worker.read_text())
    if count != 1:
        raise RuntimeError('Unexpected Service Worker manifest format')
    worker.write_text(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists():
        raise FileExistsError('Output directory already exists: ' + str(out))
    meta = json.loads((ROOT / 'build-meta.json').read_text())
    with tempfile.TemporaryDirectory(prefix='llama-zh-build-') as temporary:
        checkout = Path(temporary) / 'llama.cpp'
        run(['git', 'clone', '--depth', '1', '--branch', meta['engineBuild'],
             '--filter=blob:none', '--sparse', 'https://github.com/ggml-org/llama.cpp.git', str(checkout)])
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=checkout, text=True).strip()
        if commit != meta['engineCommit']:
            raise RuntimeError('Upstream commit does not match pinned metadata')
        run(['git', 'sparse-checkout', 'set', 'tools/ui'], cwd=checkout)
        run(['git', 'apply', '--check', str(ROOT / 'llama-ui-zh-b12375.patch')], cwd=checkout)
        run(['git', 'apply', str(ROOT / 'llama-ui-zh-b12375.patch')], cwd=checkout)
        ui = checkout / 'tools/ui'
        env = dict(os.environ, LLAMA_BUILD_NUMBER=meta['engineBuild'], PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD='1')
        run(['npm', 'ci', '--no-audit', '--no-fund'], cwd=ui, env=env)
        run(['npm', 'run', 'check'], cwd=ui, env=env)
        run(['npm', 'run', 'build'], cwd=ui, env=env)
        align_assets(ui / 'dist', meta['embeddedBundle'])
        out.mkdir(parents=True)
        shutil.copytree(ui / 'dist', out / 'dist')
        for name in ('manage.py', '启用中文界面.command', '恢复原界面.command', 'LICENSE',
                     'THIRD_PARTY_NOTICES.txt', 'ATTRIBUTION.md', 'build-meta.json'):
            shutil.copy2(ROOT / name, out / name)
        shutil.copytree(ROOT / 'LICENSES', out / 'LICENSES')
        manifest = {str(p.relative_to(out / 'dist')): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in sorted((out / 'dist').rglob('*')) if p.is_file()}
        (out / 'files.sha256.json').write_text(json.dumps(manifest, indent=2))
    print('Built package: ' + str(out))


if __name__ == '__main__':
    main()
