# 来源、复用与致谢

本项目是对已有开源工作进行的版本适配。以下分别说明实际复用和参考关系，避免把他人的工作描述为本项目原创。

| 来源 | 固定版本 / 提交 | 使用方式 | 原许可证 |
| --- | --- | --- | --- |
| [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp) | [b12375 / 9d25e0014](https://github.com/ggml-org/llama.cpp/tree/9d25e0014c4b4b316873c01f4938c0e3c687287d) | 网页界面的基础实现、构建配置及源码补丁的适配对象。发行包内含基于这些源码构建的网页资源。 | [MIT](LICENSES/llama.cpp-MIT.txt) |
| [6667084/llama-ui-zh](https://github.com/6667084/llama-ui-zh) | [534dc670](https://github.com/6667084/llama-ui-zh/tree/534dc670e190211f09f6d3a07428b1598d4ca6eb)；其翻译基线为 b10450 | 大量复用已有中文翻译；参考并复用其资源文件名对齐方法。迁移已移动的组件，修订变化的文案，并补充新版功能。 | [MIT](LICENSES/llama-ui-zh-MIT.txt) |
| [wenbofeng/MarioMakeChat](https://github.com/wenbofeng/MarioMakeChat) | [4ec56ba9](https://github.com/wenbofeng/MarioMakeChat/tree/4ec56ba96b1b4420930621e6152cba41b4656228) | 阅读其中文界面和相关源码，作为常见操作名称、提示语表达的参考；未复制其应用实现、后端、模型、人设提示词或图形资产。 | [MIT](LICENSES/MarioMakeChat-MIT.txt) |
| [ggml-org/Llama-macOS](https://github.com/ggml-org/Llama-macOS) | 验收版本 0.48.0 | 使用其已有的 Custom web app 设置加载网页补丁；未修改或重新打包原生应用。 | 原生应用不在本包内分发 |

## 本次适配新增的工作

- 将旧翻译迁移到 b12375 的组件和文件结构，补充新版对话分组、标签页、模型管理、对话压缩等文案。
- 保留界面字段的内部标识、接口字段和持久化设置值；尤其保留用于识别系统消息占位的英文内部标记。
- 兼容中文“访问被拒绝”错误，确保 API 密钥输入入口仍可用。
- 处理中文计数、复数表达和插值顺序，并补齐辅助名称。
- 对齐受保护接口环境下的内嵌资源文件名，并使用内容摘要更新相应 Service Worker 版本。
- 提供版本核对、资源校验、原设置备份及恢复脚本，完成隔离浏览器验收和安装/恢复往返检查。

以上修改不意味着上游已认可、合并或维护此补丁。

## 版权与许可保留

`llama.cpp` 的原版权为 The ggml authors；原中文补丁的版权为 llama-ui-zh contributors；MarioMakeChat 的原版权为 fengwenbo。相应完整许可证均保留在 `LICENSES/` 中。

构建出的网页还包含第三方库、字体等资源。`THIRD_PARTY_NOTICES.txt` 收录固定构建环境中的许可与版权声明（含仅用于构建的工具），并保留相关上游 vendored 库的许可。第三方内容继续受各自原许可证约束。

本仓库新增的内容以 MIT 许可发布，不替换或取消任何上游许可条件。
