# form_Help.py
import os
import sys
import re
import tkinter as tk
from tkinter import ttk

class HelpWindow:

    def __init__(self, master):
        self.master = master

    def show(self):
        help_window = tk.Toplevel(self.master)
        help_window.title("操作マニュアル")
        self._center_window(help_window, 960, 640)

        # モーダル設定
        help_window.transient(self.master)
        help_window.grab_set()

        # 上部フレームに閉じるボタン
        top_frame = tk.Frame(help_window)
        top_frame.pack(fill=tk.X, side=tk.TOP, padx=5, pady=5)
        btn_close = ttk.Button(top_frame, text="閉じる", command=help_window.destroy)
        btn_close.pack(side=tk.LEFT)

        # テキストフレーム
        frame_text = tk.Frame(help_window)
        frame_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0,5))

        txt = tk.Text(frame_text, wrap=tk.WORD, font=("BIZ UDゴシック", 10), padx=5, pady=5)
        v_scroll = tk.Scrollbar(frame_text, command=txt.yview)
        txt.configure(yscrollcommand=v_scroll.set)
        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Markdown読み込み
        md_text = self._load_help_file()
        self._render_markdown(txt, md_text)
        txt.configure(state=tk.DISABLED)

        # モーダル待機
        self.master.wait_window(help_window)

    def get_help_md_path(self):
        if getattr(sys, 'frozen', False):
            # exe化された場合
            base_path = sys._MEIPASS
        else:
            # 開発環境の場合
            base_path = os.path.dirname(os.path.abspath(__file__))
    
        return os.path.join(base_path, "help.md")

    # -----------------
    # ヘルプファイル読み込み
    # -----------------
    def _load_help_file(self):
        path = self.get_help_md_path()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return "ヘルプファイルが見つかりません。"

    # -----------------
    # Markdownレンダリング
    # -----------------
    def _render_markdown(self, text_widget, md):
        text_widget.tag_config("h1",   lmargin1=10, lmargin2=10, font=("BIZ UDゴシック", 16, "bold"))
        text_widget.tag_config("h2",   lmargin1=20, lmargin2=20, font=("BIZ UDゴシック", 14, "bold"))
        text_widget.tag_config("h3",   lmargin1=40, lmargin2=40, font=("BIZ UDゴシック", 12, "bold"))
        text_widget.tag_config("list", lmargin1=60, lmargin2=70, spacing1=4, spacing3=2)
        text_widget.tag_config("list2",lmargin1=70, lmargin2=80, spacing1=4, spacing3=2)
        text_widget.tag_config("body", lmargin1=60, lmargin2=60, spacing1=4, spacing3=2)
        text_widget.tag_config("hr", foreground="gray")

        numbered_list_regex = re.compile(r'^(\d+\.)\s+')

        for line in md.split("\n"):
            if line.startswith("# "):
                text_widget.insert("end", line[2:] + "\n", "h1")
            elif line.startswith("## "):
                text_widget.insert("end", line[3:] + "\n", "h2")
            elif line.startswith("### "):
                text_widget.insert("end", line[4:] + "\n", "h3")
            elif line.startswith("- "):
                text_widget.insert("end", "＊" + line[2:] + "\n", "list")
            elif line.startswith("-- "):
                text_widget.insert("end", "・" + line[3:] + "\n", "list2")
            elif numbered_list_regex.match(line):
                match = numbered_list_regex.match(line)
                if match:
                    number = match.group(1)
                    content = line[match.end():]
                    text_widget.insert("end", f"{number}{content}\n", "list")
            elif line.strip() == "---":
                text_width = 64
                text_widget.insert("end", "─" * text_width + "\n", "hr")
            else:
                text_widget.insert("end", line + "\n", "body")

    # -----------------
    # ウィンドウ中央化
    # -----------------
    def _center_window(self, window, width, height):
        self.master.update_idletasks()
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_w = self.master.winfo_width()
        parent_h = self.master.winfo_height()
        x = parent_x + (parent_w - width) // 2
        y = parent_y + (parent_h - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")
        