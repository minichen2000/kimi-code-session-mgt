# 构建与开发指南

## 环境

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) 用于依赖管理

## 安装

```bash
uv sync --group dev
```

## 运行

```bash
python scripts/run.py
```

## 测试

```bash
uv run pytest
```

## 代码检查与格式化

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```

自动格式化：

```bash
uv run ruff format .
```

## 构建 wheel

```bash
uv build
```

## 构建单文件 Windows 可执行版

```bash
uv run python scripts/build_exe.py
```

生成的可执行文件位于 `dist/kimi-session-manager.exe`。这是一个单文件绿色版，双击即可运行，不会弹出命令行窗口。

