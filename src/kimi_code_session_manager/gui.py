"""Tkinter GUI for Kimi Code Session Manager."""

from __future__ import annotations

import shutil
import tkinter as tk
from tkinter import messagebox, ttk

from kimi_code_session_manager.models import AgentWireLog, Session, WorkspaceGroup
from kimi_code_session_manager.scanner import scan_all_sessions
from kimi_code_session_manager.utils import (
    format_size,
    format_timestamp_ms,
    reveal_in_file_manager,
)

PREVIEW_HEAD_LINES = 50
PREVIEW_TAIL_LINES = 10


class SessionManagerApp:
    """Main application window."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Kimi Code Session Manager")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)

        self.groups: list[WorkspaceGroup] = []
        self.session_by_item: dict[str, Session] = {}
        self.wire_by_item: dict[str, AgentWireLog] = {}
        self.selected_session: Session | None = None
        self.selected_wire: AgentWireLog | None = None

        self._build_toolbar()
        self._build_main_layout()
        self._build_status_bar()

        self.refresh()

    def _build_toolbar(self) -> None:
        toolbar = ttk.Frame(self.root, padding=5)
        toolbar.pack(fill=tk.X)

        ttk.Button(toolbar, text="刷新", command=self.refresh).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="在文件夹中显示", command=self._reveal_session).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(toolbar, text="删除 Session", command=self._delete_session).pack(
            side=tk.LEFT, padx=2
        )

    def _build_main_layout(self) -> None:
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left: grouped session tree
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)

        ttk.Label(left_frame, text="工作目录 / Sessions").pack(anchor=tk.W)

        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("updated", "size"),
            show="tree headings",
            selectmode="browse",
        )
        self.tree.heading("#0", text="名称", anchor=tk.W)
        self.tree.heading("updated", text="更新时间", anchor=tk.W)
        self.tree.heading("size", text="大小", anchor=tk.W)
        self.tree.column("#0", width=280)
        self.tree.column("updated", width=140)
        self.tree.column("size", width=80)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # Right: details and wire logs
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=3)

        # Details panel
        details_frame = ttk.LabelFrame(right_frame, text="Session 详情", padding=10)
        details_frame.pack(fill=tk.X, padx=5, pady=5)

        self.detail_labels: dict[str, ttk.Label] = {}
        detail_rows = [
            ("标题", "title"),
            ("ID", "session_id"),
            ("工作目录", "cwd"),
            ("路径", "path"),
            ("创建时间", "created"),
            ("更新时间", "updated"),
            ("总大小", "size"),
            ("Agent 数", "agent_count"),
        ]
        for idx, (label_text, key) in enumerate(detail_rows):
            ttk.Label(details_frame, text=f"{label_text}:").grid(
                row=idx, column=0, sticky=tk.NW, padx=5, pady=2
            )
            lbl = ttk.Label(details_frame, text="-", wraplength=700, justify=tk.LEFT)
            lbl.grid(row=idx, column=1, sticky=tk.NW, padx=5, pady=2)
            self.detail_labels[key] = lbl

        # Wire logs panel
        wire_frame = ttk.LabelFrame(right_frame, text="Agent wire.jsonl 日志", padding=10)
        wire_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        wire_top = ttk.Frame(wire_frame)
        wire_top.pack(fill=tk.X)

        ttk.Button(wire_top, text="在文件夹中显示", command=self._reveal_wire).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(wire_top, text="刷新选中 Session", command=self._refresh_selected_session).pack(
            side=tk.LEFT, padx=2
        )

        wire_paned = ttk.PanedWindow(wire_frame, orient=tk.VERTICAL)
        wire_paned.pack(fill=tk.BOTH, expand=True, pady=5)

        wire_list_frame = ttk.Frame(wire_paned)
        wire_paned.add(wire_list_frame, weight=1)

        self.wire_tree = ttk.Treeview(
            wire_list_frame,
            columns=("size", "lines"),
            show="headings",
            selectmode="browse",
        )
        self.wire_tree.heading("#0", text="Agent")
        self.wire_tree.heading("size", text="大小")
        self.wire_tree.heading("lines", text="行数")
        self.wire_tree.column("#0", width=150)
        self.wire_tree.column("size", width=80)
        self.wire_tree.column("lines", width=80)
        self.wire_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        wire_tree_scroll = ttk.Scrollbar(
            wire_list_frame, orient=tk.VERTICAL, command=self.wire_tree.yview
        )
        self.wire_tree.configure(yscrollcommand=wire_tree_scroll.set)
        wire_tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.wire_tree.bind("<<TreeviewSelect>>", self._on_wire_select)
        self.wire_tree.bind("<Double-1>", lambda _e: self._reveal_wire())

        preview_frame = ttk.Frame(wire_paned)
        wire_paned.add(preview_frame, weight=2)

        ttk.Label(preview_frame, text="文件预览（前 50 行 + 后 10 行）").pack(anchor=tk.W)

        self.preview_text = tk.Text(
            preview_frame,
            wrap=tk.NONE,
            state=tk.DISABLED,
            font=("Consolas", 10),
        )
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        preview_scroll_y = ttk.Scrollbar(
            preview_frame, orient=tk.VERTICAL, command=self.preview_text.yview
        )
        self.preview_text.configure(yscrollcommand=preview_scroll_y.set)
        preview_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        preview_scroll_x = ttk.Scrollbar(
            preview_frame, orient=tk.HORIZONTAL, command=self.preview_text.xview
        )
        self.preview_text.configure(xscrollcommand=preview_scroll_x.set)
        preview_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

    def _build_status_bar(self) -> None:
        self.status = ttk.Label(self.root, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(fill=tk.X, side=tk.BOTTOM)

    def refresh(self) -> None:
        self.tree.delete(*self.tree.get_children())
        self.session_by_item.clear()
        self.wire_by_item.clear()
        self.selected_session = None
        self.selected_wire = None
        self._clear_details()
        self._clear_preview()

        try:
            self.groups = scan_all_sessions()
        except OSError as e:
            messagebox.showerror("扫描失败", f"无法读取 session 目录：{e}")
            return

        total_size = 0
        total_sessions = 0
        for group in self.groups:
            group_size = sum(session.total_size for session in group.sessions)
            group_node = self.tree.insert(
                "",
                tk.END,
                text=group.cwd,
                values=("", format_size(group_size)),
                open=True,
            )
            for session in group.sessions:
                item = self.tree.insert(
                    group_node,
                    tk.END,
                    text=session.title or session.session_id,
                    values=(
                        format_timestamp_ms(session.updated_at),
                        format_size(session.total_size),
                    ),
                )
                self.session_by_item[item] = session
                total_size += session.total_size
                total_sessions += 1

        status_text = (
            f"共 {len(self.groups)} 个工作目录，"
            f"{total_sessions} 个 session，"
            f"总计 {format_size(total_size)}"
        )
        self.status.config(text=status_text)

    def _on_tree_select(self, _event: tk.Event | None = None) -> None:
        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        session = self.session_by_item.get(item)
        if session is None:
            return

        self.selected_session = session
        self._show_session_details(session)
        self._populate_wire_tree(session)

    def _show_session_details(self, session: Session) -> None:
        self.detail_labels["title"].config(text=session.title)
        self.detail_labels["session_id"].config(text=session.session_id)
        self.detail_labels["cwd"].config(text=session.cwd)
        self.detail_labels["path"].config(text=str(session.session_dir))
        self.detail_labels["created"].config(text=format_timestamp_ms(session.created_at))
        self.detail_labels["updated"].config(text=format_timestamp_ms(session.updated_at))
        self.detail_labels["size"].config(text=format_size(session.total_size))
        self.detail_labels["agent_count"].config(text=str(len(session.agents)))

    def _populate_wire_tree(self, session: Session) -> None:
        self.wire_tree.delete(*self.wire_tree.get_children())
        self.wire_by_item.clear()
        self.selected_wire = None
        self._clear_preview()

        for wire in session.agents:
            item = self.wire_tree.insert(
                "",
                tk.END,
                text=wire.agent_name,
                values=(format_size(wire.size), wire.line_count),
            )
            self.wire_by_item[item] = wire

    def _on_wire_select(self, _event: tk.Event | None = None) -> None:
        selection = self.wire_tree.selection()
        if not selection:
            return

        item = selection[0]
        wire = self.wire_by_item.get(item)
        if wire is None:
            return

        self.selected_wire = wire
        self._show_preview(wire)

    def _show_preview(self, wire: AgentWireLog) -> None:
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete("1.0", tk.END)

        try:
            with wire.path.open("r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except OSError as e:
            self.preview_text.insert(tk.END, f"无法读取文件：{e}")
            self.preview_text.config(state=tk.DISABLED)
            return

        total = len(lines)
        if total <= PREVIEW_HEAD_LINES + PREVIEW_TAIL_LINES:
            self.preview_text.insert(tk.END, "".join(lines))
        else:
            head = lines[:PREVIEW_HEAD_LINES]
            tail = lines[-PREVIEW_TAIL_LINES:]
            self.preview_text.insert(tk.END, "".join(head))
            self.preview_text.insert(
                tk.END, f"\n... 省略 {total - PREVIEW_HEAD_LINES - PREVIEW_TAIL_LINES} 行 ...\n\n"
            )
            self.preview_text.insert(tk.END, "".join(tail))

        self.preview_text.config(state=tk.DISABLED)

    def _clear_details(self) -> None:
        for lbl in self.detail_labels.values():
            lbl.config(text="-")

    def _clear_preview(self) -> None:
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.config(state=tk.DISABLED)

    def _reveal_session(self) -> None:
        session = self.selected_session
        if session is None:
            messagebox.showinfo("提示", "请先选择一个 session")
            return
        reveal_in_file_manager(session.session_dir)

    def _reveal_wire(self) -> None:
        wire = self.selected_wire
        if wire is None:
            messagebox.showinfo("提示", "请先选择一个 wire.jsonl 日志")
            return
        reveal_in_file_manager(wire.path)

    def _delete_session(self) -> None:
        session = self.selected_session
        if session is None:
            messagebox.showinfo("提示", "请先选择一个 session")
            return

        if not messagebox.askyesno(
            "确认删除",
            f"确定要永久删除 session 吗？\n\n标题：{session.title}\n路径：{session.session_dir}",
        ):
            return

        try:
            shutil.rmtree(session.session_dir)
        except OSError as e:
            messagebox.showerror("删除失败", f"无法删除：{e}")
            return

        self.refresh()
        messagebox.showinfo("已删除", "session 已删除")

    def _refresh_selected_session(self) -> None:
        if self.selected_session is not None:
            self._populate_wire_tree(self.selected_session)
            self._show_session_details(self.selected_session)


def main() -> None:
    root = tk.Tk()
    SessionManagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
