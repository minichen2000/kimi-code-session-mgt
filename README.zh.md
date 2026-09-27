# Kimi Code Session Manager

一个跨平台的 [Kimi Code](https://kimi-code.moonshot.cn/) 会话管理 GUI 工具。

## 功能

- 按工作目录分组浏览所有 Kimi Code session。
- 查看 session 元数据：标题、创建时间、更新时间、总大小。
- 查看某个 session 下每个 Agent 的 `wire.jsonl` 日志。
- 在文件管理器中打开 session 目录或某个 `wire.jsonl` 文件。
- 删除 session 前会弹出确认对话框。
- 运行时零第三方依赖，使用 Python 内置的 `tkinter`。

## 快速开始

```bash
# 从源码运行
python scripts/run.py
```

或者安装包之后：

```bash
kimi-session-manager
```

## 环境要求

- Python 3.10+
- `tkinter`（通常随 Python 一起安装）

## 开发

详见 [BUILD.zh.md](BUILD.zh.md)。

## 许可证

MIT
