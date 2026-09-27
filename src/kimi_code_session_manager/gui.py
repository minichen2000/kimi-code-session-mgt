"""Tkinter GUI for Kimi Code Session Manager."""

from __future__ import annotations

import shutil
import tkinter as tk
from tkinter import messagebox, ttk

from kimi_code_session_manager.models import AgentWireLog, Session
from kimi_code_session_manager.scanner import scan_all_sessions
from kimi_code_session_manager.utils import (
    format_size,
    format_timestamp_ms,
    reveal_in_file_manager,
)

_FONT_FAMILY = "Microsoft YaHei"
_FONT_SIZES = {"小": 9, "中": 11, "大": 13}
_DEFAULT_FONT_SIZE_LABEL = "中"


class SessionManagerApp:
    """Main application window."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Kimi Code Session Manager")
        self.root.geometry("1400x800")
        self.root.minsize(1000, 650)

        self.sessions: list[Session] = []
        self.session_by_item: dict[str, Session] = {}
        self.wire_by_item: dict[str, AgentWireLog] = {}
        self.selected_session: Session | None = None
        self.selected_wire: AgentWireLog | None = None
        self._hover_item: str | None = None

        self._style = ttk.Style()
        self._text_widgets: list[tk.Text] = []
        self._current_font_label = tk.StringVar(value=_DEFAULT_FONT_SIZE_LABEL)
        self._sash_set = False
        self._sort_column: str | None = None
        self._sort_reverse = False

        self._build_toolbar()
        self._build_main_layout()
        self._build_status_bar()

        self._apply_font_size(_FONT_SIZES[_DEFAULT_FONT_SIZE_LABEL])
        self.refresh()

    def _on_paned_configure(self, _event: tk.Event | None = None) -> None:
        """Set the initial sash position once the PanedWindow has a real size."""
        if self._sash_set:
            return
        width = self._paned.winfo_width()
        if width > 100:
            self._paned.sashpos(0, int(width * 0.7))  # type: ignore[no-untyped-call]
            self._sash_set = True

    def _on_heading_click(self, column: str) -> None:
        """Sort all sessions by the clicked column."""
        if self._sort_column == column:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_column = column
            # Default to descending for numeric/time columns, ascending for name.
            self._sort_reverse = column != "#0"
        self.refresh()

    def _sort_sessions(self, sessions: list[Session]) -> list[Session]:
        column = self._sort_column
        reverse = self._sort_reverse
        if column == "updated":
            return sorted(sessions, key=lambda s: s.updated_at, reverse=reverse)
        if column == "size":
            return sorted(sessions, key=lambda s: s.wire_size, reverse=reverse)
        if column == "agents":
            return sorted(sessions, key=lambda s: len(s.agents), reverse=reverse)
        if column == "#0":
            return sorted(sessions, key=lambda s: s.title or s.session_id, reverse=reverse)
        return sessions

    def _build_toolbar(self) -> None:
        toolbar = ttk.Frame(self.root, padding=5)
        toolbar.pack(fill=tk.X)

        ttk.Button(toolbar, text="刷新", command=self.refresh).pack(side=tk.LEFT, padx=2)
        self.reveal_session_btn = ttk.Button(
            toolbar, text="在文件夹中显示", command=self._reveal_session, state=tk.DISABLED
        )
        self.reveal_session_btn.pack(side=tk.LEFT, padx=2)
        self.delete_session_btn = ttk.Button(
            toolbar, text="删除 Session", command=self._delete_session, state=tk.DISABLED
        )
        self.delete_session_btn.pack(side=tk.LEFT, padx=2)

        font_combo = ttk.Combobox(
            toolbar,
            textvariable=self._current_font_label,
            values=list(_FONT_SIZES.keys()),
            state="readonly",
            width=5,
        )
        font_combo.pack(side=tk.RIGHT, padx=2)
        font_combo.bind("<<ComboboxSelected>>", self._on_font_changed)
        ttk.Label(toolbar, text="字体:").pack(side=tk.RIGHT, padx=(10, 2))

    def _build_main_layout(self) -> None:
        self._paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self._paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self._paned.bind("<Configure>", self._on_paned_configure)

        # Left: session list (main area)
        left_frame = ttk.Frame(self._paned)
        self._paned.add(left_frame, weight=7)

        ttk.Label(left_frame, text="Sessions").pack(anchor=tk.W)

        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("updated", "size", "agents"),
            show="tree headings",
            selectmode="browse",
        )
        self.tree.heading(
            "#0", text="名称", anchor=tk.W, command=lambda: self._on_heading_click("#0")
        )
        self.tree.heading(
            "updated",
            text="更新时间",
            anchor=tk.W,
            command=lambda: self._on_heading_click("updated"),
        )
        self.tree.heading(
            "size", text="大小", anchor=tk.W, command=lambda: self._on_heading_click("size")
        )
        self.tree.heading(
            "agents", text="Agent 数", anchor=tk.W, command=lambda: self._on_heading_click("agents")
        )
        self.tree.column("#0", width=420, minwidth=200, stretch=True)
        self.tree.column("updated", width=150, minwidth=100, stretch=False)
        self.tree.column("size", width=70, minwidth=50, stretch=False)
        self.tree.column("agents", width=80, minwidth=60, stretch=False)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree.tag_configure("even", background="#ffffff")
        self.tree.tag_configure("odd", background="#f0f0f0")

        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.bind("<Motion>", self._on_tree_motion)
        self.tree.bind("<Leave>", self._on_tree_leave)

        # Right: details and wire logs
        right_frame = ttk.Frame(self._paned)
        self._paned.add(right_frame, weight=3)

        # Details panel
        details_frame = ttk.LabelFrame(right_frame, text="Session 详情", padding=10)
        details_frame.pack(fill=tk.X, padx=5, pady=5)

        self.detail_texts: dict[str, tk.Text] = {}
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
            txt = tk.Text(
                details_frame,
                height=1,
                wrap=tk.WORD,
                state=tk.DISABLED,
                relief=tk.FLAT,
                padx=0,
                pady=0,
            )
            txt.grid(row=idx, column=1, sticky=tk.EW, padx=5, pady=2)
            self.detail_texts[key] = txt
            self._text_widgets.append(txt)

        details_frame.columnconfigure(1, weight=1)

        # Wire logs panel
        wire_frame = ttk.LabelFrame(right_frame, text="Agent wire.jsonl 日志", padding=10)
        wire_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        wire_top = ttk.Frame(wire_frame)
        wire_top.pack(fill=tk.X)

        self.reveal_wire_btn = ttk.Button(
            wire_top, text="在文件夹中显示", command=self._reveal_wire, state=tk.DISABLED
        )
        self.reveal_wire_btn.pack(side=tk.LEFT, padx=2)
        ttk.Button(wire_top, text="刷新选中 Session", command=self._refresh_selected_session).pack(
            side=tk.LEFT, padx=2
        )

        wire_list_frame = ttk.Frame(wire_frame)
        wire_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.wire_tree = ttk.Treeview(
            wire_list_frame,
            columns=("size",),
            show="tree headings",
            selectmode="browse",
        )
        self.wire_tree.heading("#0", text="Agent 名称")
        self.wire_tree.heading("size", text="大小")
        self.wire_tree.column("#0", width=150, minwidth=80)
        self.wire_tree.column("size", width=80, minwidth=60)
        self.wire_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        wire_tree_scroll = ttk.Scrollbar(
            wire_list_frame, orient=tk.VERTICAL, command=self.wire_tree.yview
        )
        self.wire_tree.configure(yscrollcommand=wire_tree_scroll.set)
        wire_tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.wire_tree.bind("<<TreeviewSelect>>", self._on_wire_select)
        self.wire_tree.bind("<Double-1>", lambda _e: self._reveal_wire())

        # Tooltip for tree items
        self._tooltip = tk.Toplevel(self.root)
        self._tooltip.withdraw()
        self._tooltip.overrideredirect(True)
        self._tooltip_label = ttk.Label(
            self._tooltip,
            text="",
            background="#ffffcc",
            relief=tk.SOLID,
            borderwidth=1,
            padding=3,
            wraplength=600,
            justify=tk.LEFT,
        )
        self._tooltip_label.pack()

    def _build_status_bar(self) -> None:
        self.status = ttk.Label(self.root, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(fill=tk.X, side=tk.BOTTOM)

    def _on_font_changed(self, _event: tk.Event | None = None) -> None:
        label = self._current_font_label.get()
        size = _FONT_SIZES.get(label, _FONT_SIZES[_DEFAULT_FONT_SIZE_LABEL])
        self._apply_font_size(size)

    def _apply_font_size(self, size: int) -> None:
        font = (_FONT_FAMILY, size)
        heading_font = (_FONT_FAMILY, size, "bold")

        self._style.configure(".", font=font)
        self._style.configure("Treeview", font=font, rowheight=max(30, size * 2 + 8))
        self._style.configure("Treeview.Heading", font=heading_font)

        for txt in self._text_widgets:
            txt.config(font=font)

        # Re-calculate detail text heights after font change.
        if self.selected_session is not None:
            self._show_session_details(self.selected_session)

    def _show_tooltip(self, text: str, x: int, y: int) -> None:
        self._tooltip_label.config(text=text)
        self._tooltip.deiconify()
        self._tooltip.geometry(f"+{x + 15}+{y + 15}")

    def _hide_tooltip(self) -> None:
        self._tooltip.withdraw()

    def _on_tree_motion(self, event: tk.Event) -> None:
        item = self.tree.identify_row(event.y)
        if item == self._hover_item:
            return
        self._hover_item = item

        if not item:
            self._hide_tooltip()
            return

        session = self.session_by_item.get(item)
        if session is not None:
            text = f"{session.title}\n{session.session_id}\n{session.cwd}"
        else:
            text = ""

        self._show_tooltip(text, event.x_root, event.y_root)

    def _on_tree_leave(self, _event: tk.Event | None = None) -> None:
        self._hover_item = None
        self._hide_tooltip()

    def _update_button_states(self) -> None:
        session_selected = self.selected_session is not None
        self.reveal_session_btn.config(state=tk.NORMAL if session_selected else tk.DISABLED)
        self.delete_session_btn.config(state=tk.NORMAL if session_selected else tk.DISABLED)
        wire_selected = self.selected_wire is not None
        self.reveal_wire_btn.config(state=tk.NORMAL if wire_selected else tk.DISABLED)

    def refresh(self) -> None:
        self.tree.delete(*self.tree.get_children())
        self.session_by_item.clear()
        self.wire_by_item.clear()
        self.selected_session = None
        self.selected_wire = None
        self._clear_details()
        self._clear_wire_tree()
        self._update_button_states()

        try:
            groups = scan_all_sessions()
        except OSError as e:
            messagebox.showerror("扫描失败", f"无法读取 session 目录：{e}")
            return

        self.sessions = []
        for group in groups:
            self.sessions.extend(group.sessions)

        total_wire_size = sum(session.wire_size for session in self.sessions)
        total_sessions = len(self.sessions)

        for idx, session in enumerate(self._sort_sessions(self.sessions)):
            tag = "even" if idx % 2 == 0 else "odd"
            item = self.tree.insert(
                "",
                tk.END,
                text=session.title or session.session_id,
                values=(
                    format_timestamp_ms(session.updated_at),
                    format_size(session.wire_size),
                    len(session.agents),
                ),
                tags=(tag,),
            )
            self.session_by_item[item] = session

        status_text = f"共 {total_sessions} 个 session，wire 总计 {format_size(total_wire_size)}"
        self.status.config(text=status_text)

    def _on_tree_select(self, _event: tk.Event | None = None) -> None:
        selection = self.tree.selection()
        if not selection:
            self.selected_session = None
            self._clear_details()
            self._clear_wire_tree()
            self._update_button_states()
            return

        item = selection[0]
        session = self.session_by_item.get(item)
        if session is None:
            self.selected_session = None
            self._clear_details()
            self._clear_wire_tree()
            self._update_button_states()
            return

        self.selected_session = session
        self._show_session_details(session)
        self._populate_wire_tree(session)
        self._update_button_states()

    def _show_session_details(self, session: Session) -> None:
        values = {
            "title": session.title,
            "session_id": session.session_id,
            "cwd": session.cwd,
            "path": str(session.session_dir),
            "created": format_timestamp_ms(session.created_at),
            "updated": format_timestamp_ms(session.updated_at),
            "size": format_size(session.wire_size),
            "agent_count": str(len(session.agents)),
        }
        for key, value in values.items():
            self._set_detail_text(key, value)

    def _set_detail_text(self, key: str, value: str) -> None:
        txt = self.detail_texts[key]
        txt.config(state=tk.NORMAL)
        txt.delete("1.0", tk.END)
        txt.insert(tk.END, value)
        txt.config(state=tk.DISABLED)
        # Adjust height to fit wrapped content.
        count_result = txt.count("1.0", tk.END, "displaylines")
        if isinstance(count_result, tuple):
            display_lines = count_result[0] or 1
        else:
            display_lines = count_result or 1
        txt.config(height=max(1, display_lines))

    def _populate_wire_tree(self, session: Session) -> None:
        self.wire_tree.delete(*self.wire_tree.get_children())
        self.wire_by_item.clear()
        self.selected_wire = None
        self._update_button_states()

        for wire in session.agents:
            item = self.wire_tree.insert(
                "",
                tk.END,
                text=wire.agent_name,
                values=(format_size(wire.size),),
            )
            self.wire_by_item[item] = wire

    def _on_wire_select(self, _event: tk.Event | None = None) -> None:
        selection = self.wire_tree.selection()
        if not selection:
            self.selected_wire = None
            self._update_button_states()
            return

        item = selection[0]
        wire = self.wire_by_item.get(item)
        if wire is None:
            self.selected_wire = None
            self._update_button_states()
            return

        self.selected_wire = wire
        self._update_button_states()

    def _clear_details(self) -> None:
        for txt in self.detail_texts.values():
            txt.config(state=tk.NORMAL)
            txt.delete("1.0", tk.END)
            txt.config(state=tk.DISABLED)
            txt.config(height=1)

    def _clear_wire_tree(self) -> None:
        self.wire_tree.delete(*self.wire_tree.get_children())
        self.wire_by_item.clear()

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
