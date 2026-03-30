import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import threading

from module_SocketComm import SocketComm
from module_Logger import loggingGetLogger
from module_Threading import ThreadCustom
from module_TkUtils import with_watch
from form_Help import HelpWindow
from form_Version import VersionWindow

global logger
logger = loggingGetLogger()

"""
FormCreatorクラス　（tk.Frameを継承）
"""
class FormCreator(tk.Frame):

    # クラス初期化（定型文）
    # tkinterのFrameを継承したGUIクラス
    # 通信設定、データ送受信、ログ表示などのUIを構築
    def __init__(self, master = None):

        # グローバル変数定義
        self.CHARACTOR_CODE = "ascii" # デフォルト文字コード
        self.THREAD_RECEIVE = None     # 自動受信スレッド管理変数
        self.THREAD_ACCEPT = None     # 受付スレッド管理変数
        self.LISTEN_STATE = False     # 状態管理フラグ（Listen）
        self.CONNECT_STATE = False     # 状態管理フラグ（Connect）
        self.SV_SEND_LINE = 0         # 手動送信時の送信データ行番号

        # self.SocketComm作成
        self.SocketComm = SocketComm(self)

        # Window初期設定（定型文）
        super().__init__(master) # 「tk.Frame(master)」と同じ意味
        
        # メインウィンドウのタイトルを設定
        self.master.title("ソケット通信（TCP/IP）")

        # メインウィンドウのサイズを設定
        w = 1024
        h = 768
        self.master.geometry(str(w) + "x" + str(h))

        # メインウィンドウを画面中央に配置
        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()
        self.master.geometry("+" + str(int((sw-w)/2)) + "+" + str(int((sh-h)/2)))
        
        # メニューバーの作成
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        menubar.add_command(label="終了", command=self.form_destroy)
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ヘルプ", menu=help_menu)
        help_menu.add_command(label="このソフトについて", command=lambda: HelpWindow(self.master).show())
        help_menu.add_command(label="バージョン情報", command=lambda: VersionWindow(self.master).show())

        # leftFrameの作成
        self.leftFrame = tk.Frame(self.master)
        
        # PanedWindowの作成
        self.panelWindow = tk.PanedWindow(self.master, orient=tk.VERTICAL, sashpad=2, sashrelief=tk.RAISED)
        #sashrelief:tk.RAISED, tk.GROOVE, tk.SUNKEN, tk.RIDGE, tk.FLAT

        # 入れ子フレームの作成
        self.frame1 = ttk.Labelframe(self.leftFrame, text="通信設定")
        self.frame2 = ttk.Labelframe(self.leftFrame, text="手動送信設定")
        self.frame3 = ttk.Labelframe(self.leftFrame, text="自動送信設定")
        self.frame4 = ttk.Labelframe(self.panelWindow, text="送信データ")
        self.frame5 = ttk.Labelframe(self.panelWindow, text="送受信ログ")

        # PanedWindowにLabelframeを追加
        self.panelWindow.add(self.frame4)
        self.panelWindow.add(self.frame5)
        
        # -----------------
        # frame1: 通信設定
        # -----------------

        # ラベルの作成
        self.label1 = ttk.Label(self.frame1, text="通信モード")
        self.label2 = ttk.Label(self.frame1, text="IPアドレス")
        self.label3 = ttk.Label(self.frame1, text="ポート番号")
        self.label4 = ttk.Label(self.frame1, text="同時接続数")
        self.label5 = ttk.Label(self.frame1, text="接続タイムアウト(秒)")
        self.label6 = ttk.Label(self.frame1, text="文字コード")

        # テキストボックスの作成
        self.tbIpAddress = ttk.Entry(self.frame1, width=15)
        self.tbPortNumber = ttk.Entry(self.frame1, width=5)
        self.tbBackLog = ttk.Entry(self.frame1, width=2)
        self.tbTimeOut = ttk.Entry(self.frame1, width=2)
        self.tbIpAddress.insert(0, "127.0.0.1")
        self.tbPortNumber.insert(0, "9001")
        self.tbBackLog.insert(0, "1")
        self.tbTimeOut.insert(0, "2")

        # コンボボックスにセットするリストの作成
        socketMode = ["TCPサーバ","TCPクライアント"]
        charCodeList = ["ascii","shift-jis","utf-8"]

        # コンボボックスの作成
        self.cbSocketMode = ttk.Combobox(self.frame1, values=socketMode, state="readonly")
        self.cbCharCode = ttk.Combobox(self.frame1, values=charCodeList, state="readonly")
        #self.cbSocketMode.set(socketMode[0])
        self.cbCharCode.set(charCodeList[1])

        # イベントバインド
        self.cbSocketMode.bind("<<ComboboxSelected>>", self.on_select)

        # コマンドボタンの作成
        self.btnOpenClose = ttk.Button(self.frame1, text="開始", command=self.SocketStartStop)

        # 進捗メッセージ用ラベル
        self.lblProgress = ttk.Label(self.frame1, text="", foreground="blue", anchor="e")

        # frame1内の配置
        self.label1.grid(        row=0, column=0, columnspan=1, padx=10, pady=2, sticky="w")
        self.label2.grid(        row=1, column=0, columnspan=1, padx=10, pady=2, sticky="w")
        self.label3.grid(        row=2, column=0, columnspan=1, padx=10, pady=2, sticky="w")
        self.label4.grid(        row=3, column=0, columnspan=1, padx=10, pady=2, sticky="w")
        self.label5.grid(        row=4, column=0, columnspan=1, padx=10, pady=2, sticky="w")
        self.label6.grid(        row=5, column=0, columnspan=1, padx=10, pady=2, sticky="w")
        self.cbSocketMode.grid(  row=0, column=1, columnspan=2, padx=10, pady=2, sticky="w")
        self.tbIpAddress.grid(   row=1, column=1, columnspan=2, padx=10, pady=2, sticky="w")
        self.tbPortNumber.grid(  row=2, column=1, columnspan=1, padx=10, pady=2, sticky="w")
        self.tbBackLog.grid(     row=3, column=1, columnspan=1, padx=10, pady=2, sticky="w")
        self.tbTimeOut.grid(     row=4, column=1, columnspan=1, padx=10, pady=2, sticky="w")
        self.cbCharCode.grid(    row=5, column=1, columnspan=2, padx=10, pady=2, sticky="w")
        self.lblProgress.grid(   row=6, column=0, columnspan=2, padx=10, pady=2, sticky="e")
        self.btnOpenClose.grid(  row=6, column=2, columnspan=1, padx=10, pady=2, sticky="ew")

        # 列幅比率設定
        self.frame1.grid_columnconfigure(0, weight=2)
        self.frame1.grid_columnconfigure(1, weight=1)
        self.frame1.grid_columnconfigure(2, weight=1)

        # 初期状態は無効化
        self.tbIpAddress.configure(state=tk.DISABLED)
        self.tbPortNumber.configure(state=tk.DISABLED)
        self.tbBackLog.configure(state=tk.DISABLED)
        self.tbTimeOut.configure(state=tk.DISABLED)
        self.cbCharCode.configure(state=tk.DISABLED)
        self.btnOpenClose.configure(state=tk.DISABLED)

        # -----------------
        # frame2: 手動送信設定
        # -----------------

        # データ送信方法の定義
        optionSendType = ["テキスト内の文字列を一度に送信","テキスト内の文字列を1行ずつ送信"]
        self.valSendType = tk.IntVar()

        # ラジオボタンの作成
        self.rbSendType1 = tk.Radiobutton(self.frame2, text=optionSendType[0], value=0, variable=self.valSendType, command=self.enable_radioButtonManual)
        self.rbSendType2 = tk.Radiobutton(self.frame2, text=optionSendType[1], value=1, variable=self.valSendType, command=self.enable_radioButtonManual)

        # ラジオボタンの初期値を設定
        self.valSendType.set(0)

        # 受信時制御コード指定の定義
        self.valTargetAck = tk.BooleanVar(value=True)
        self.valTargetNak = tk.BooleanVar(value=True)
        self.valTargetEnq = tk.BooleanVar(value=True)
        self.valTargetEot = tk.BooleanVar(value=True)
        self.valTargetCr = tk.BooleanVar(value=True)
        self.valTargetLf = tk.BooleanVar(value=True)
        self.valTargetCrLf = tk.BooleanVar(value=True)

        # チェックボタンの作成
        self.chkTargetAck = tk.Checkbutton(self.frame2, text="ACK", variable=self.valTargetAck)
        self.chkTargetNak = tk.Checkbutton(self.frame2, text="NAK", variable=self.valTargetNak)
        self.chkTargetEnq = tk.Checkbutton(self.frame2, text="ENQ", variable=self.valTargetEnq)
        self.chkTargetEot = tk.Checkbutton(self.frame2, text="EOT", variable=self.valTargetEot)
        self.chkTargetCr = tk.Checkbutton(self.frame2, text="CR", variable=self.valTargetCr)
        self.chkTargetLf = tk.Checkbutton(self.frame2, text="LF", variable=self.valTargetLf)
        self.chkTargetCrLf = tk.Checkbutton(self.frame2, text="CRLF", variable=self.valTargetCrLf)

        # ラベルの作成
        self.lblRecvTimeout = ttk.Label(self.frame2, text="秒毎に受信待機", state=tk.NORMAL)
        self.lblRecvTarget = ttk.Label(self.frame2, text="次の制御コードを受信した時は即時受信", state=tk.NORMAL)

        # テキストボックスの作成
        self.tbRecvTimeout = ttk.Entry(self.frame2, justify=tk.RIGHT)
        self.tbRecvTimeout.insert(0, "1.5")
        self.tbRecvTimeout.configure(state=tk.NORMAL, width=5)

        # frame2内の配置
        self.rbSendType1.grid(   row=0, column=0, padx=10, pady=2, sticky="w", columnspan=4)
        self.rbSendType2.grid(   row=1, column=0, padx=10, pady=2, sticky="w", columnspan=4)
        self.tbRecvTimeout.grid( row=2, column=0, padx=15, pady=2, sticky="w")
        self.lblRecvTimeout.grid(row=2, column=0, padx=55, pady=2, sticky="w", columnspan=4)
        self.lblRecvTarget.grid( row=3, column=0, padx=10, pady=2, sticky="w", columnspan=4)
        self.chkTargetAck.grid(  row=4, column=0, padx=(10, 0), pady=2, sticky="ew")
        self.chkTargetNak.grid(  row=5, column=0, padx=(10, 0), pady=0, sticky="ew")
        self.chkTargetEnq.grid(  row=4, column=1, padx=0, pady=0, sticky="ew")
        self.chkTargetEot.grid(  row=5, column=1, padx=0, pady=0, sticky="ew")
        self.chkTargetCr.grid(   row=4, column=2, padx=0, pady=0, sticky="ew")
        self.chkTargetLf.grid(   row=5, column=2, padx=0, pady=0, sticky="ew")
        self.chkTargetCrLf.grid( row=4, column=3, padx=0, pady=0, sticky="ew")

        # -----------------
        # frame3: 自動送信設定
        # -----------------

        # データ送信方法の定義
        optionNextSend = ["応答メッセージ（ACK/NAK）を利用して送受信","指定時間毎に送受信"]
        self.valNextSend = tk.IntVar()

        # ACK/NAKに対するSTX/ETX付与変数の定義
        self.valStxEtx = tk.BooleanVar(value=False)
        
        # ラジオボタンの作成
        self.rbNextSend1 = tk.Radiobutton(self.frame3, text=optionNextSend[0], value=0, variable=self.valNextSend, command=self.enable_radioButtonNext)
        self.rbNextSend2 = tk.Radiobutton(self.frame3, text=optionNextSend[1], value=1, variable=self.valNextSend, command=self.enable_radioButtonNext)

        # チェックボタンの作成
        self.chkStxEtx = tk.Checkbutton(self.frame3, text="応答メッセージの前後に「STX/ETX」を付与する", variable=self.valStxEtx)

        # ラジオボタンの初期値を設定
        self.valNextSend.set(0)

        # ラベルの作成
        self.lblAutoSend = ttk.Label(self.frame3, text="テキスト内の文字列を1行ずつ送信")
        self.lblAckNak1 = ttk.Label(self.frame3, text="・ACK受信で次の行を送信")
        self.lblAckNak2 = ttk.Label(self.frame3, text="・NAK受信で送信中止")
        self.lblSendTime = ttk.Label(self.frame3, text="秒毎に「送信->受信」を繰り返す")

        # テキストボックスの作成
        self.tbSendTime = ttk.Entry(self.frame3, width=5, justify=tk.RIGHT)
        self.tbSendTime.insert(0, "1.0")
        self.tbSendTime.configure(state=tk.DISABLED)

        # frame3内の配置
        self.lblAutoSend.grid(row=0, column=0, padx=10, pady=2, sticky="w")
        self.rbNextSend1.grid(row=1, column=0, padx=10, pady=2, sticky="w")
        self.lblAckNak1.grid( row=2, column=0, padx=30, pady=2, sticky="w")
        self.lblAckNak2.grid( row=3, column=0, padx=30, pady=2, sticky="w")
        self.chkStxEtx.grid(  row=4, column=0, padx=30, pady=2, sticky="w")
        self.rbNextSend2.grid(row=5, column=0, padx=10, pady=2, sticky="w")
        self.tbSendTime.grid( row=6, column=0, padx=35, pady=2, sticky="w")
        self.lblSendTime.grid(row=6, column=0, padx=75, pady=2, sticky="w")

        # -----------------
        # frame4: 送信データ
        # -----------------

        # スクロールバー付きテキストボックスの作成
        self.txtSendText = tk.Text(self.frame4, width=10, height=10, wrap=tk.NONE, font=("BIZ UDゴシック", 9)) #font="TkDefaultFont"
        self.vscSendText = tk.Scrollbar(self.frame4, orient=tk.VERTICAL, command=self.txtSendText.yview)
        self.hscSendText = tk.Scrollbar(self.frame4, orient=tk.HORIZONTAL, command=self.txtSendText.xview)
        self.txtSendText["yscrollcommand"] = self.vscSendText.set
        self.txtSendText["xscrollcommand"] = self.hscSendText.set

        # テキストボックスの選択行に適用するタグ
        self.txtSendText.tag_configure("selected", background="yellow")  

        # コマンドボタン用フレームの作成
        self.frame4b = tk.Frame(self.frame4)

        # ラベルの作成
        self.lblListenState = ttk.Label(self.frame4b, text="[ Listen：停止 ]")
        self.lblConnectState = ttk.Label(self.frame4b, text="[ Connect：未接続 ]")

        # コマンドボタンの作成
        self.btnSendManual = ttk.Button(self.frame4b, text="手動送信", command=self.SocketSendManual, state=tk.DISABLED)
        self.btnSendAuto = ttk.Button(self.frame4b, text="自動送信", command=self.SocketSendAuto, state=tk.DISABLED)

        # frame4内の配置
        self.txtSendText.grid(row=0, column=0, padx=1, pady=1, sticky="nsew")
        self.hscSendText.grid(row=1, column=0, padx=1, pady=1, sticky="ew")
        self.vscSendText.grid(row=0, column=1, padx=1, pady=1, sticky="nse")
        self.frame4b.grid(    row=2, column=0, padx=1,  pady=1, sticky="nsew")

        # frame4b内の配置
        self.lblListenState.grid( row=0, column=0, padx=5, pady=10)
        self.lblConnectState.grid(row=0, column=1, padx=5, pady=10)
        self.btnSendManual.grid(  row=0, column=2, padx=5, pady=10)
        self.btnSendAuto.grid(    row=0, column=3, padx=5, pady=10)

        self.frame4.grid_columnconfigure(0, weight=1) # 列の調整
        self.frame4.grid_rowconfigure(0, weight=1)    # 行の調整

        # -----------------
        # frame5: 送受信ログ
        # -----------------

        # スクロールバー付きテキストボックスの作成
        self.txtSocketLog = tk.Text(self.frame5, width=10, height=10, wrap=tk.NONE, font=("BIZ UDゴシック", 9)) #font="TkDefaultFont"
        self.vscSocketLog = tk.Scrollbar(self.frame5, orient=tk.VERTICAL, command=self.txtSocketLog.yview)
        self.hscSocketLog = tk.Scrollbar(self.frame5, orient=tk.HORIZONTAL, command=self.txtSocketLog.xview)
        self.txtSocketLog["yscrollcommand"] = self.vscSocketLog.set
        self.txtSocketLog["xscrollcommand"] = self.hscSocketLog.set

        # frame5内の配置
        self.txtSocketLog.grid(row=0, column=0, padx=1, pady=1, sticky="nsew")
        self.hscSocketLog.grid(row=1, column=0, padx=1, pady=1, sticky="ew")
        self.vscSocketLog.grid(row=0, column=1, padx=1, pady=1, sticky="ns")
        self.frame5.grid_columnconfigure(0, weight=1) # 列の調整
        self.frame5.grid_rowconfigure(0, weight=1) # 行の調整

        # -----------------
        # タブ移動コントロール定義
        # -----------------
        # Tab順定義
        self.tab_order = [
            self.cbSocketMode,
            self.tbIpAddress,
            self.tbPortNumber,
            self.tbBackLog,
            self.tbTimeOut,
            self.cbCharCode,
            self.btnOpenClose,
            self.rbSendType1,
            self.rbSendType2,
            self.tbRecvTimeout,
            self.rbNextSend1,
            self.rbNextSend2,
            self.tbSendTime,
            self.btnSendManual,
            self.btnSendAuto
        ]

        # Tabキーイベント設定
        for i, widget in enumerate(self.tab_order):
            widget.bind("<Tab>", lambda e, i=i: self.focus_next(i))
            widget.bind("<Return>", lambda e, i=i: self.focus_next(i))
            widget.bind("<Shift-Tab>", lambda e, i=i: self.focus_prev(i))

        # タブ移動対象外コントロール定義
        # self.txtSendText.bind("<Tab>", lambda e: None)
        # self.txtSendText.bind("<Return>", lambda e: None)
        # self.txtSocketLog.bind("<Tab>", lambda e: None)
        # self.txtSocketLog.bind("<Return>", lambda e: None)

        # -----------------
        # Frame配置全体
        # -----------------

        # 要素の配置
        self.frame1.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.frame2.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.frame3.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        self.leftFrame.grid(row=0, column=0, rowspan=3, padx=10, pady=10, sticky="nsew")
        self.panelWindow.grid(row=0, column=1, rowspan=3, padx=10, pady=10, sticky="nsew")

        # ウィンドウのリサイズに合わせて幅と高さを広げる
        self.leftFrame.grid_rowconfigure(2, weight=1) # 行の調整
        self.master.grid_columnconfigure(1, weight=1) # 列の調整
        self.master.grid_rowconfigure(2, weight=1)    # 行の調整

        # //////////
        # Windowボタン
        # //////////

        # xボタンが押下された時
        self.master.protocol("WM_DELETE_WINDOW", lambda: self.form_destroy())

    def focus_next(self, index):
        next_index = (index + 1) % len(self.tab_order)
        self.tab_order[next_index].focus_set()
        return "break"

    def focus_prev(self, index):
        prev_index = (index - 1) % len(self.tab_order)
        self.tab_order[prev_index].focus_set()
        return "break"

        # ========================================
    # メソッド：SocketStartStop / ソケット通信・開始と停止
    # ========================================
    @with_watch()
    def SocketStartStop(self):

        try:

            # ボタン無効化
            self.btnOpenClose.configure(state=tk.DISABLED)
            self.btnOpenClose.update()
            self.btnSendManual.configure(state=tk.DISABLED)
            self.btnSendManual.update()
            self.btnSendAuto.configure(state=tk.DISABLED)
            self.btnSendAuto.update()

            if self.CONNECT_STATE:  # 接続中の場合 → 切断
                self.lblProgress.configure(text="切断中...")
                self.lblProgress.update()

            if self.LISTEN_STATE:  # Listen中の場合 → 停止
                self.lblProgress.configure(text="停止中...")
                self.lblProgress.update()

            if self.LISTEN_STATE or self.CONNECT_STATE:
                '''停止'''
                # スレッド停止
                self.threadEnd()
                # 切断・Listen停止
                self.SocketComm.SocketClose()
                # 状態管理フラグ
                self.LISTEN_STATE = False
                self.CONNECT_STATE = False
                # コントロール初期化
                self.cbSocketMode.configure(state="readonly")
                self.on_select(None)
                self.btnOpenClose.configure(text="開始", state=tk.NORMAL)
                self.btnOpenClose.update()
                self.lblProgress.configure(text="")
                self.lblProgress.update()
                # スレッド監視・強制停止
                if hasattr(self, "check_id"):
                    self.after_cancel(self.check_id)
            else:
                '''開始'''
                # ボタン無効化
                self.btnOpenClose.configure(state=tk.DISABLED)
                self.btnOpenClose.update()
                # 通信モード
                socketMode = self.cbSocketMode.current()
                if socketMode == 0:
                    # TCPサーバ
                    self.lblProgress.configure(text="待受起動中...")
                    self.lblProgress.update()
                    # Listen開始
                    ret = self.SocketComm.listen()
                    if ret:
                        self.LISTEN_STATE = True
                        self.CONNECT_STATE = False
                        self.threadStart()
                else:
                    # TCPクライアント
                    self.lblProgress.configure(text="接続確立中...")
                    self.lblProgress.update()
                    # Conect開始
                    ret = self.SocketComm.Connect()
                    if ret:
                        self.LISTEN_STATE = False
                        self.CONNECT_STATE = True
                        self.threadStart()

                # 開始成功時
                if self.LISTEN_STATE or self.CONNECT_STATE:
                    # コントロール有効無効化
                    self.btnOpenClose.configure(text="停止")
                    self.btnSendManual.configure(state=tk.NORMAL)
                    self.btnSendAuto.configure(state=tk.NORMAL)
                    self.cbSocketMode.configure(state=tk.DISABLED)
                    self.tbIpAddress.configure(state=tk.DISABLED)
                    self.tbPortNumber.configure(state=tk.DISABLED)
                    self.tbBackLog.configure(state=tk.DISABLED)
                    self.tbTimeOut.configure(state=tk.DISABLED)
                    self.cbCharCode.configure(state=tk.DISABLED)
                    # スレッド監視・開始
                    self.check_thread()

                self.btnOpenClose.configure(state=tk.NORMAL)
                self.btnOpenClose.update()
                self.lblProgress.configure(text="")
                self.lblProgress.update()

        except Exception as e:

            msg = logger.error_exception(e)
            messagebox.showerror("SocketStartStop", msg)

    # ========================================
    # メソッド：threadStart / 自動受信スレッド開始
    # ========================================
    def threadStart(self):

        try:

            # データ受信変数 初期化
            self.SocketComm.ResetData()
            self.SV_SEND_LINE = 0
            self.txtSendText.tag_remove("selected", "1.0", "end")

            # 受付スレッド 開始
            self.THREAD_ACCEPT = None
            self.THREAD_ACCEPT = ThreadCustom(self.SocketComm.AcceptClient, (), "受付スレッド", 0.5)
            self.THREAD_ACCEPT.begin()

            # 自動受信スレッド 開始
            self.THREAD_RECEIVE = None
            self.THREAD_RECEIVE = ThreadCustom(self.SocketComm.Receive, (), "自動受信スレッド", 0.01)
            self.THREAD_RECEIVE.begin()

        except Exception as e:

            msg = logger.error_exception(e)
            messagebox.showerror("threadStart", msg)


    # ========================================
    # メソッド：threadStop / スレッド一時停止
    # ========================================
    def threadStop(self):

        try:
            tcnt = threading.active_count()
            if tcnt > 1:
                self.THREAD_ACCEPT.stop()
                self.THREAD_RECEIVE.stop()

        except Exception as e:

            msg = logger.error_exception(e)
            messagebox.showerror("threadStop", msg)


    # ========================================
    # メソッド：threadStop / スレッド再開
    # ========================================
    def threadRestart(self):

        try:
            tcnt = threading.active_count()
            if tcnt > 1:
                self.THREAD_ACCEPT.restart()
                self.THREAD_RECEIVE.restart()

        except Exception as e:

            msg = logger.error_exception(e)
            messagebox.showerror("threadRestart", msg)


    # ========================================
    # メソッド：threadStop / スレッド停止
    # ========================================
    def threadEnd(self):

        try:
            # データ受信変数 初期化
            self.SocketComm.ResetData()
            self.SV_SEND_LINE = 0
            self.txtSendText.tag_remove("selected", "1.0", "end")

            # 受付スレッド 停止
            if self.THREAD_ACCEPT:
                self.THREAD_ACCEPT.end()
                self.THREAD_ACCEPT = None

            # 自動受信スレッド 停止
            if self.THREAD_RECEIVE:
                self.THREAD_RECEIVE.end()
                self.THREAD_RECEIVE = None

        except Exception as e:

            msg = logger.error_exception(e)
            messagebox.showerror("threadEnd", msg)


    # ========================================
    # メソッド：SocketSendManual / 手動送信
    # ========================================
    @with_watch()
    def SocketSendManual(self):
        # 手動送信ボタンのクリック時の処理

        if self.valSendType.get() == 0:
            # テキスト内の文字列を一度に送信
    
            # 送信データの各行を配列で取得
            records = self.txtSendText.get("1.0", "end").splitlines()
    
            # 送信データを連結
            sendStr = ""
            for rec in records:
                if rec.strip():  # 空行を無視
                    sendStr += rec
    
            # データ送信
            if sendStr:
                self.SocketComm.SendManual(sendStr)

        else:
            # テキスト内の文字列を1行ずつ送信
     
            # 行数の取得
            lineCount = self.txtSendText.index("end-1c").split(".")[0]

            if int(lineCount) > self.SV_SEND_LINE:
    
                # 対象行の表示
                self.txtSendText.tag_remove("selected", "1.0", "end")
                lineStart = f"{self.SV_SEND_LINE + 1}.0"
                lineEnd = f"{self.SV_SEND_LINE + 2}.0"
                self.txtSendText.tag_add("selected", lineStart, lineEnd)
                self.txtSendText.see(lineStart)
    
                # 対象行の文字列を取得
                sendStr = self.txtSendText.get(lineStart, lineEnd)
                sendStr = sendStr.rstrip("\r\n")
    
                # データ送信
                ret = self.SocketComm.SendManual(sendStr)
                if not ret:
                    self.SV_SEND_LINE = 0
                    self.txtSendText.tag_remove("selected", "1.0", "end")
                    return
    
                # 次の行へ
                self.SV_SEND_LINE += 1
    
                if int(lineCount) == self.SV_SEND_LINE:
                    messagebox.showinfo("ソケット通信","最後の行までデータを送信しました。")
                    self.SV_SEND_LINE = 0
                    self.txtSendText.tag_remove("selected", "1.0", "end")
    
            else:
                self.SV_SEND_LINE = 0
                self.txtSendText.tag_remove("selected", "1.0", "end")

    # ========================================
    # メソッド：SocketSendAuto / 自動送信
    # ========================================
    @with_watch()
    def SocketSendAuto(self):
        # 自動送信ボタンのクリック時の処理

        # スレッド監視・強制停止
        if hasattr(self, "check_id"):
            self.after_cancel(self.check_id)

        # 自動受信スレッド 停止
        if self.THREAD_RECEIVE:
            if self.THREAD_RECEIVE.running:
                self.THREAD_RECEIVE.stop()
                print("THREAD_RECEIVE停止")

        # テキスト内の文字列を1行ずつ送信
        ret = self.SocketComm.SendAuto(self.valNextSend.get(), self.tbSendTime.get())
        if ret:
            messagebox.showinfo("ソケット通信","データ送信が終了しました。")
        else:
            self.SocketStartStop()
            return

        # 自動受信スレッド 再開
        if self.THREAD_RECEIVE:
            if not self.THREAD_RECEIVE.running:
                self.THREAD_RECEIVE.restart()
                print("THREAD_RECEIVE再開")

        # スレッド監視・開始
        self.check_thread()

    # ========================================
    # メソッド：check_thread / スレッド監視
    # ========================================
    def check_thread(self):
        checkAccept = False
        checkReceive = False
        if self.THREAD_ACCEPT:
            if self.THREAD_ACCEPT.running == False:
                print("THREAD_ACCEPT停止")
                checkAccept = True
        if self.THREAD_RECEIVE:
            if self.THREAD_RECEIVE.running == False:
                print("THREAD_RECEIVE停止")
                checkReceive = True
        if checkAccept and checkReceive:
            self.SocketStartStop()
            return
        elif checkReceive:
            self.THREAD_RECEIVE.restart()
        self.check_id = self.after(100, self.check_thread)

    # ========================================
    # メソッド：form_destroy / 終了処理
    # ========================================
    def form_destroy(self):
        # プログラム終了

        if self.LISTEN_STATE or self.CONNECT_STATE:
            messagebox.showerror("終了確認", "接続中のため終了できません。先に切断してください。")
            return

        if messagebox.askokcancel("終了前の確認","終了しますか？"):
            # スレッド停止
            self.threadEnd()
            self.THREAD_ACCEPT = None
            self.THREAD_RECEIVE = None
            # プログラム終了
            #self.master.destroy()
            sys.exit()

    # ========================================
    # メソッド：enable_radioButtonManual / ラジオボタン切替（手動送信設定）
    # ========================================
    def enable_radioButtonManual(self):
        self.SV_SEND_LINE = 0
        self.txtSendText.tag_remove("selected", "1.0", "end")

    # ========================================
    # メソッド：enable_radioButtonNext / ラジオボタン切替（自動送信設定）
    # ========================================
    def enable_radioButtonNext(self):
        if self.valNextSend.get() == 0:
            self.tbSendTime.configure(state=tk.DISABLED)
            self.lblSendTime.configure(state=tk.DISABLED)
        else:
            self.tbSendTime.configure(state=tk.NORMAL)
            self.lblSendTime.configure(state=tk.NORMAL)

    # ========================================
    # メソッド：on_select / コンボ選択時（通信モード）
    # ========================================
    def on_select(self, event):
        if self.cbSocketMode.current() == 0:
            self.tbIpAddress.configure(state=tk.DISABLED)
            self.tbPortNumber.configure(state=tk.NORMAL)
            self.tbBackLog.configure(state=tk.DISABLED)
            self.tbTimeOut.configure(state=tk.DISABLED)
            self.cbCharCode.configure(state="readonly")
            self.btnOpenClose.configure(state=tk.NORMAL)
        else:
            self.tbIpAddress.configure(state=tk.NORMAL)
            self.tbPortNumber.configure(state=tk.NORMAL)
            self.tbBackLog.configure(state=tk.DISABLED)
            self.tbTimeOut.configure(state=tk.NORMAL)
            self.cbCharCode.configure(state="readonly")
            self.btnOpenClose.configure(state=tk.NORMAL)
