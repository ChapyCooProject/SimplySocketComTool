import tkinter as tk
from tkinter import ttk

class VersionWindow:

    def __init__(self, master):
        self.master = master

    def show(self):
        win = tk.Toplevel(self.master)
        win.title("バージョン情報")
        self._center_window(win, 400, 250)

        # モーダル設定
        win.transient(self.master)
        win.grab_set()

        # メイン情報フレーム（上部）
        frame = tk.Frame(win)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # フォント指定
        title_font = ("BIZ UDゴシック", 12, "bold")
        label_font = ("BIZ UDゴシック", 9)

        # 表示内容
        tk.Label(frame, text="簡易ソケット通信ソフト", font=title_font).pack(pady=(0,10))
        tk.Label(frame, text="Version: 1.1.0", font=label_font).pack(pady=2)
        tk.Label(frame, text="作成者: ChapyCooProject", font=label_font).pack(pady=2)
        tk.Label(frame, text="更新日: 2026-04-15", font=label_font).pack(pady=2)
        tk.Label(frame, text="このツールはTCP/IPソケット通信のテストや\n送受信データの確認用として使用してください。", 
                 font=label_font, justify=tk.LEFT).pack(pady=10)

        # 下部フレーム（閉じるボタン中央）
        bottom_frame = tk.Frame(win)
        bottom_frame.pack(side=tk.BOTTOM, pady=10)
        ttk.Button(bottom_frame, text="閉じる", command=win.destroy).pack()

        self.master.wait_window(win)

    def _center_window(self, window, width, height):
        self.master.update_idletasks()
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_w = self.master.winfo_width()
        parent_h = self.master.winfo_height()
        x = parent_x + (parent_w - width) // 2
        y = parent_y + (parent_h - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")