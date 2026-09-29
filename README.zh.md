# Kimi Code Session Manager

一个跨平台的 [Kimi Code](https://kimi-code.moonshot.cn/) 会话管理 GUI 工具。

## 功能

- 平铺浏览所有 Kimi Code session。
- 点击列标题按标题、更新时间、wire 大小、Agent 数量排序。
- 查看 session 元数据：标题、创建时间、更新时间、wire 日志大小。
- 查看某个 session 下每个 Agent 的 `wire.jsonl` 日志。
- “查看”按钮用系统默认程序打开选中的 `wire.jsonl` 文件。
- 在文件管理器中打开 session 目录或某个 `wire.jsonl` 文件。
- 删除 session 前会弹出确认对话框。
- 可调节字体大小。
- 奇偶行不同背景色和列分隔线，便于阅读。
- 启动时窗口自动居中。
- 运行时零第三方依赖，使用 Python 内置的 `tkinter`。

## 快速开始

### 从源码运行

```bash
python scripts/run.py
```

或者安装包之后：

```bash
kimi-session-manager
```

### Windows 可执行版

可直接从 [GitHub Releases](https://github.com/minichen2000/kimi-code-session-mgt/releases) 下载 `kimi-session-manager.exe`。这是单文件绿色版，双击即可运行，不会弹出命令行窗口。

如需自行构建，详见 [BUILD.zh.md](BUILD.zh.md)。


## 环境要求

- Python 3.10+
- `tkinter`（通常随 Python 一起安装）

## 开发

详见 [BUILD.zh.md](BUILD.zh.md)。

## 许可证

MIT
