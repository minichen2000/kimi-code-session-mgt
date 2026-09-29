# Agent 约定

## 项目简介

Kimi Code Session Manager 是一个跨平台的 Kimi Code 会话管理 GUI 工具。使用 Python 3 标准库中的 `tkinter` 开发，运行时零第三方依赖。

## 架构决策

- **GUI 框架**：使用 `tkinter`。不引入 PyQt、Electron 或 Web 技术栈，保持轻量，只要有 Python 就能运行。
- **Session 发现**：扫描 Kimi Code 会话根目录（`~/.kimi-code/sessions` 或 `%USERPROFILE%/.kimi-code/sessions`）。解析每个 `session_<uuid>/state.json` 获取元数据，扫描 `agents/<agent_name>/wire.jsonl` 获取日志列表。
- **列表展示**：左侧以平铺列表展示所有 session，不再按工作目录分组。工作目录信息保留在右侧详情和 tooltip 中。
- **大小计算**：左侧“大小”列显示的是该 session 下所有 Agent 的 `wire.jsonl` 文件大小之和，不是整个 session 目录大小。
- **排序**：点击列标题可按“名称”“更新时间”“大小”“Agent 数”排序，再次点击切换升序/降序，当前排序列标题显示 `↑` / `↓` 箭头。
- **在文件夹中显示**：按平台调用不同命令：
  - Windows: `explorer /select,"<路径>"`
  - macOS: `open -R "<路径>"`
  - Linux: `xdg-open "<目录>"`
- **打包**：使用 PyInstaller 构建单文件 Windows 可执行版（`--onefile --noconsole`），入口为 `scripts/entry.py`。
- **发版**：打 `v*` tag 推送即由 GitHub Actions（`.github/workflows/release.yml`）云端构建 exe 并自动创建 Release 上传产物，不在本地构建后手动上传。GitHub 是唯一 release 渠道，Gitee 只推代码和 tag、不建 Release 页面。
- **应用图标**：exe 文件图标和运行时窗口图标共用 `assets/icon.ico`（"KW" 字样，已入库）。由 `scripts/generate_icon.py`（Pillow）生成；打包时 `--icon` 设置文件图标，`--add-data` 内嵌 ico 供 `gui.py` 的 `iconbitmap` 设置窗口图标。

## 编码约定

- 使用 `ruff` 统一代码风格和 import 排序。
- 公共函数和类必须加类型提示，并通过 `mypy --strict` 检查。
- GUI 代码与扫描/模型逻辑分离。
- GUI 中所有面向用户的文本使用中文。

## 已知坑点

- `state.json` 可能因会话异常中断而缺失或损坏，扫描器必须容错并继续。
- `wire.jsonl` 可能非常大，GUI 不应自动加载完整文件内容；目前只列出文件，提供“在文件夹中显示”和“查看”（调用系统默认程序打开）功能，由外部编辑器/查看器打开。
- 删除 session 不可逆。必须弹出确认对话框，且只允许删除 `session_<uuid>` 目录，禁止删除父级 `wd_*` 工作区目录。
- `ttk.Treeview` 单元格不支持自动换行，长标题通过加宽“名称”列 + 鼠标悬停 tooltip + 右侧详情面板完整展示。
- `ttk.Treeview` 的列标题不支持内嵌复杂控件，排序箭头通过动态修改 heading text 实现，需要给列宽留足空间。

## 外部依赖

- 运行时：无第三方依赖，仅 Python 标准库。
- 开发时：`pytest`、`ruff`、`mypy`、`pillow`（仅用于生成图标）。
- 打包时：`pyinstaller`。

## Agent 交接清单

1. 阅读本文件 `AGENTS.md`。
2. 阅读 `PROGRESS.md` 了解当前状态和待办。
3. 阅读 `README.md` / `BUILD.md` 了解使用方式和构建方法。
