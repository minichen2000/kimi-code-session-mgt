# 进度

## 已完成

- 项目骨架初始化（目录结构、Git、配置文件、文档）。
- 实现核心模块：`models.py`、`utils.py`、`scanner.py`。
- 实现 Tkinter GUI：平铺 session 列表、列标题排序、wire 大小显示、字体调节、在文件夹中显示、删除 session。
- 编写并跑通扫描模块单元测试。
- 配置 ruff、mypy、pytest，并生成 `uv.lock`。
- 按最新项目启动规范将 `AGENTS.md` 调整为中文为主。
- 双推代码到 GitHub / Gitee。
- 发布 v0.1.0 release。
- 为 exe 和运行窗口添加 "KW" 图标（`scripts/generate_icon.py` 生成 `assets/icon.ico`，Pillow 仅为开发依赖）。
- 发布 v0.2.0 release。
- wire 日志面板新增“查看”按钮：用系统默认程序打开选中的 wire.jsonl（utils.py 新增 `open_with_default_app`）。
- 发布 v0.3.0 release（GitHub / Gitee 双推，附单文件 exe）。
- 新增 `.github/workflows/release.yml`：push `v*` tag 云端构建 exe 并自动发布 GitHub Release，本地构建上传不再是发版流程。明确 GitHub 为唯一 release 渠道，Gitee 只推代码不发 Release（v0.3.0 及以前的 Gitee Release 页面保留，不再更新）。
- 左侧 session 列表启动时默认按更新时间降序排列（`gui.py` 初始 `_sort_column="updated"`、`_sort_reverse=True`）。
- 发布 v0.4.0 release（默认按更新时间降序 + 云端 CI 构建流程，GitHub 唯一 release 渠道）。

## 待办

- 可选：打包为独立可执行文件（已完成）。

## 已知问题

无。
