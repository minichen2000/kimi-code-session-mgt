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

## 构建单文件 Windows 可执行版（本地）

```bash
uv run python scripts/build_exe.py
```

生成的可执行文件位于 `dist/kimi-session-manager.exe`。这是一个单文件绿色版，双击即可运行，不会弹出命令行窗口。

## 发布 Release（云端构建）

打 `v*` 开头的 tag 并推送后，GitHub Actions（`.github/workflows/release.yml`）会在 `windows-latest` runner 上自动安装依赖、跑 `scripts/build_exe.py`（内含 ruff/mypy/pytest 检查）构建 exe，并自动创建 GitHub Release、上传产物、生成 Release Notes：

```bash
git tag -a vX.Y.Z -m "vX.Y.Z"
git push origin master --tags   # 同时推送到 GitHub 仓库
```

Gitee 没有免费 CI，Gitee 的 Release 页面需要手动把 GitHub 构建产物上传一次。

### 应用图标

exe 文件图标和运行时的窗口图标共用同一个文件：`assets/icon.ico`（已提交到仓库）。如需重新生成（依赖开发依赖 Pillow）：

```bash
uv run python scripts/generate_icon.py
```

配色、圆角半径、文字大小都是该脚本顶部的常量。构建时通过 `--icon`（文件图标）和 `--add-data`（运行时窗口图标）嵌入图标。

也可以直接在 [GitHub Releases](https://github.com/minichen2000/kimi-code-session-mgt/releases) 页面下载预编译版本。

