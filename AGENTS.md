# Agent 约定

## 项目简介

Kimi Code Session Manager 是一个跨平台的 Kimi Code 会话管理 GUI 工具。使用 Python 3 标准库中的 `tkinter` 开发，运行时零第三方依赖。

## 架构决策

- **GUI 框架**：使用 `tkinter`。不引入 PyQt、Electron 或 Web 技术栈，保持轻量，只要有 Python 就能运行。
- **Session 发现**：扫描 Kimi Code 会话根目录（`~/.kimi-code/sessions` 或 `%USERPROFILE%/.kimi-code/sessions`）。解析每个 `session_<uuid>/state.json` 获取元数据，扫描 `agents/<agent_name>/wire.jsonl` 获取日志列表。
- **分组方式**：按 `state.json` 中的 `cwd`（工作目录）分组。如果 `cwd` 缺失，则回退到父级工作区目录名 `wd_<名称>_<hash>`。
- **大小计算**：session 总大小包含整个 `session_<uuid>` 目录（日志、媒体、file-history、agent 数据等），不只是 `wire.jsonl`。
- **在文件夹中显示**：按平台调用不同命令：
  - Windows: `explorer /select,"<路径>"`
  - macOS: `open -R "<路径>"`
  - Linux: `xdg-open "<目录>"`

## 编码约定

- 使用 `ruff` 统一代码风格和 import 排序。
- 公共函数和类必须加类型提示，并通过 `mypy --strict` 检查。
- GUI 代码与扫描/模型逻辑分离。
- GUI 中所有面向用户的文本使用中文。

## 已知坑点

- `state.json` 可能因会话异常中断而缺失或损坏，扫描器必须容错并继续。
- `wire.jsonl` 可能非常大，GUI 不应自动加载完整文件内容；目前只列出文件，提供“在文件夹中显示”功能，由外部编辑器/查看器打开。
- 删除 session 不可逆。必须弹出确认对话框，且只允许删除 `session_<uuid>` 目录，禁止删除父级 `wd_*` 工作区目录。
- `ttk.Treeview` 单元格不支持自动换行，长标题通过加宽列宽 + 鼠标悬停 tooltip + 右侧详情面板完整展示。

## 外部依赖

- 运行时：无第三方依赖，仅 Python 标准库。
- 开发时：`pytest`、`ruff`、`mypy`。

## Agent 交接清单

1. 阅读本文件 `AGENTS.md`。
2. 阅读 `PROGRESS.md` 了解当前状态和待办。
3. 阅读 `README.md` / `BUILD.md` 了解使用方式和构建方法。
