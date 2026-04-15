import os
import sys
import datetime
import socket
import time

from time import sleep
from tkinter import messagebox

from module_Logger import loggingGetLogger
from controlCodes import STX
from controlCodes import ETX
from controlCodes import ACK
from controlCodes import NAK
from controlCodes import ENQ
from controlCodes import EOT
from controlCodes import CR
from controlCodes import LF
from controlCodes import str2bin_controlCode
from controlCodes import bin2str_controlCode

class SocketComm:

    def __init__(self, gui):

        self.logger = None

        self.gui = gui
        self.listen_socket = None
        self.conn_socket = None

        self.ResetData()

    def ResetData(self):

        self.recv_buffer = b""
        self.last_recv_time = 0
        self.recv_timeout = 3

    def set_charactor_code(self):
        self.charactor_code = self.gui.cbCharCode.get()

    # listen
    def listen(self):

        try:

            self.set_charactor_code()
            self.logger = loggingGetLogger(self.charactor_code)

            ipAddress = "0.0.0.0"
            portNumber = int(self.gui.tbPortNumber.get())
            backLog = int(self.gui.tbBackLog.get())

            self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.listen_socket.bind((ipAddress, portNumber))
            self.listen_socket.listen(backLog)
            self.listen_socket.setblocking(False)
            self.outputSocketLog("TCPサーバ Listen開始", "None")

            return True

        except Exception as e:
            msg = self.logger.error_exception(e)
            msg = "Listen開始時にエラーが発生しました。\r\n" + msg
            messagebox.showerror("SocketComm.listen", msg)
            return False
        
        finally:
            self.StateListenConnect()

    def SocketClose(self):

        # Connect
        self.Disconnect()
    
        # Listen
        if self.listen_socket:
            try:
                self.listen_socket.close()
            except:
                pass

        self.listen_socket = None

        self.outputSocketLog("Listen停止", "None")

        self.StateListenConnect()

    def Disconnect(self):

        # Connect
        if self.conn_socket:
            try:
                self.conn_socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            try:
                self.conn_socket.close()
            except:
                pass

        self.conn_socket = None

        self.outputSocketLog("通信切断", "None")

        self.StateListenConnect()

    # Accept Client
    def AcceptClient(self):

        if self.listen_socket:
            if not self.conn_socket:
                # クライアントからの新規接続受付
                try:
                    conn, addr = self.listen_socket.accept()
                    conn.setblocking(False)
                    self.conn_socket = conn
                    self.ResetData()
                    self.outputSocketLog(f"クライアント新規接続（{addr[0]}:{addr[1]}）", "None")
                except BlockingIOError:
                    #print("新規接続済")
                    pass

        self.StateListenConnect()

    # =============================================================================
    # Listen/Connect 状態表示
    # =============================================================================
    def StateListenConnect(self):

        # Listen
        if self.listen_socket:
            self.gui.lblListenState.configure(text="[ Listen：接続待ち ]")
        else:
            self.gui.lblListenState.configure(text="[ Listen：停止 ]")
        self.gui.lblListenState.update()

        # Connect
        if self.conn_socket:
            self.gui.lblConnectState.configure(text="[ Connect：接続済 ]")
        else:
            self.gui.lblConnectState.configure(text="[ Connect：未接続 ]")
        self.gui.lblConnectState.update()

    # =============================================================================
    # Connect（通信モード：TCPクライアント）
    # =============================================================================
    def Connect(self):

        try:
            self.set_charactor_code()
            self.logger = loggingGetLogger(self.charactor_code)

            ipAddress = self.gui.tbIpAddress.get()
            portNumber = int(self.gui.tbPortNumber.get())
            timeOut = int(self.gui.tbTimeOut.get())

            self.conn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn_socket.settimeout(timeOut)
            self.conn_socket.connect((ipAddress, portNumber))
            self.conn_socket.setblocking(False)
            self.outputSocketLog("TCPクライアント 通信開始", "None")

            return True

        except socket.timeout:
            self.outputSocketLog("接続タイムアウト", "None")
            messagebox.showerror("SocketComm.Connect", "接続を確立する前にタイムアウトしました。")
            return False

        except ConnectionRefusedError:
            self.outputSocketLog("接続拒否（サーバ未起動）", "None")
            messagebox.showerror("SocketComm.Connect", "サーバ側から接続を拒否されました。")
            return False

        except Exception as e:
            msg = self.logger.error_exception(e)
            msg = "接続確立中にエラーが発生しました。\r\n" + msg
            messagebox.showerror("SocketComm.Connect", msg)
            return False

        finally:
            self.StateListenConnect()

    def Receive(self):

        # 受信データ待ち受け処理

        try:

            current_time = time.time()
            RecvTimeout = float(self.gui.tbRecvTimeout.get())
            TargetAck = bool(self.gui.valTargetAck.get())
            TargetNak = bool(self.gui.valTargetNak.get())
            TargetEnq = bool(self.gui.valTargetEnq.get())
            TargetEot = bool(self.gui.valTargetEot.get())
            TargetCr = bool(self.gui.valTargetCr.get())
            TargetLf = bool(self.gui.valTargetLf.get())
            TargetCrLf = bool(self.gui.valTargetCrLf.get())

            sock = self.conn_socket
            if sock is not None:

                try:
                    data = sock.recv(4096)
        
                    if not data:
                        self.outputSocketLog("クライアントが切断しました。（No Data）", "None")
                        self.Disconnect()
                        self.ResetData()
                        return False
        
                    self.recv_buffer += data
                    self.last_recv_time = current_time

                    # バイト列を文字列に変換
                    recvStr = self.recv_buffer.decode(self.charactor_code, errors="replace")
                    print("受信データ：" + bin2str_controlCode(recvStr))

                    # ASTM対応・制御コード
                    recvFin = False
                    if TargetAck:
                        if self.recv_buffer.decode(self.charactor_code, errors="replace").startswith(ACK):
                            recvFin = True
                    if TargetNak:
                        if self.recv_buffer.decode(self.charactor_code, errors="replace").startswith(NAK):
                            recvFin = True
                    if TargetEnq:
                        if self.recv_buffer.decode(self.charactor_code, errors="replace").startswith(ENQ):
                            recvFin = True
                    if TargetEot:
                        if self.recv_buffer.decode(self.charactor_code, errors="replace").startswith(EOT):
                            recvFin = True
                    if TargetCr:
                        if self.recv_buffer.decode(self.charactor_code, errors="replace").endswith(CR):
                            recvFin = True
                    if TargetLf:
                        if self.recv_buffer.decode(self.charactor_code, errors="replace").endswith(LF):
                            recvFin = True
                    if TargetCrLf:
                        if self.recv_buffer.decode(self.charactor_code, errors="replace").endswith(CR + LF):
                            recvFin = True

                    if recvFin and self.recv_buffer:
                        print("終了コード受信")
                        # 送受信ログ出力
                        self.outputSocketLog(bin2str_controlCode(recvStr), "Recv")
                        # 受信変数リセット
                        self.ResetData()
                        return True
        
                except BlockingIOError:
                    #print("受信データなし（recv実行時）")
                    pass
        
                except Exception as e:
                    self.outputSocketLog("ソケットエラー", "None")
                    msg = self.logger.error_exception(e)
                    msg = "データ受信時にエラーが発生しました。\r\n" + msg
                    messagebox.showerror("SocketComm.Receive", msg)

                    self.Disconnect()
                    # 受信変数リセット
                    self.ResetData()
                    return False

                # タイムアウト確定
                if self.recv_buffer:
                    if current_time - self.last_recv_time >= RecvTimeout:
                        print("受信待機終了")
                        # バイト列を文字列に変換
                        recvStr = self.recv_buffer.decode(self.charactor_code, errors="replace")
                        print("受信データ：" + bin2str_controlCode(recvStr))
                        # 送受信ログ出力
                        self.outputSocketLog(bin2str_controlCode(recvStr), "Recv")
                        # 受信変数リセット
                        self.ResetData()

            return True

        except Exception as e:

            msg = self.logger.error_exception(e)
            msg = "データ受信時にエラーが発生しました。\r\n" + msg
            messagebox.showerror("SocketComm.Receive", msg)

            return False

        finally:
            self.StateListenConnect()

    # SendManual
    def SendManual(self, sendData):
    
        sock = self.conn_socket
        if sock is not None:
            if sendData:
                # データ送信（文字列をバイト列に変換）
                try:
                    sock.sendall(str2bin_controlCode(sendData).encode(self.charactor_code, errors="replace"))
                except Exception as e:
                    msg = self.logger.error_exception(e)
                    msg = "データ送信時にエラーが発生しました。\r\n" + msg
                    messagebox.showerror("SocketComm.SendManual", msg)
                    return False

                # 送受信ログ出力
                self.outputSocketLog(sendData, "Send")
    
        return True

    # SendAuto
    def SendAuto(self, nextSend, sendTime):

        sendStatus = True

        # 応答メッセージの前後に「STX/ETX」を付与するか
        ExistStxEtx = bool(self.gui.valStxEtx.get())

        # 各行を配列で取得
        records = self.gui.txtSendText.get("1.0", "end").splitlines()

        for rec in records:

            if rec.strip():  # 空行を無視

                # データ送信（文字列をバイト列に変換）
                try:
                    self.conn_socket.sendall(str2bin_controlCode(rec).encode(self.charactor_code, errors="replace"))
                except Exception as e:
                    msg = self.logger.error_exception(e)
                    msg = "データ送信時にエラーが発生しました。\r\n" + msg
                    messagebox.showerror("SocketComm.SendAuto", msg)
                    return False

                # 送受信ログ出力
                self.outputSocketLog(rec, "Send")
                
                if nextSend == 0:
                    # 応答電文[ACK/NAK]の受信待ち（0.1x30秒でタイムアウト）
                    waitCount = 0
                    recvBin = b""
                    while waitCount < 30:
                        try:
                            data = self.conn_socket.recv(1)
                            if not data:
                                self.outputSocketLog("サーバが切断しました。（No Data）", "None")
                                messagebox.showinfo("自動送信","サーバが切断しました。（No Data）")
                                return False
                            recvBin += data
                            if ExistStxEtx:
                                if recvBin.decode(self.charactor_code, errors="replace").endswith(STX + ACK + ETX):
                                    break
                                if recvBin.decode(self.charactor_code, errors="replace").endswith(STX + NAK + ETX):
                                    sendStatus = False
                                    break
                            else:
                                if recvBin.decode(self.charactor_code, errors="replace").endswith(ACK):
                                    break
                                if recvBin.decode(self.charactor_code, errors="replace").endswith(NAK):
                                    sendStatus = False
                                    break
                        except BlockingIOError: #データ未受信は無視
                            pass
                        except UnicodeDecodeError: #2バイト以上の文字は無視
                            pass
                        except Exception as e:
                            msg = self.logger.error_exception(e)
                            msg = "データ送信時にエラーが発生しました。\r\n" + msg
                            messagebox.showerror("SocketComm.SendAuto", msg)
                            return False
                        sleep(0.1)
                        waitCount += 1

                    if recvBin:
                        # バイト列を文字列に変換
                        recvStr = recvBin.decode(self.charactor_code, errors="replace")
                        # 送受信ログ出力
                        self.outputSocketLog(bin2str_controlCode(recvStr), "Recv")

                else:
                    # 指定秒数待機
                    waitCount = 0
                    recvBin = b""
                    while waitCount < int(float(sendTime) * 10):
                        sleep(0.1)
                        waitCount += 1
                    # 待機後にデータ取得
                    try:
                        data = self.conn_socket.recv(4096)
                        if data:
                            # バイト列を文字列に変換
                            recvStr = data.decode(self.charactor_code, errors="replace")
                            # 送受信ログ出力
                            self.outputSocketLog(bin2str_controlCode(recvStr), "Recv")
                        else:
                            self.outputSocketLog("サーバが切断しました。（No Data）", "None")
                            messagebox.showinfo("自動送信","サーバが切断しました。（No Data）")
                            return False
                    except BlockingIOError: #データ未受信は無視
                        pass
                    except Exception as e:
                        msg = self.logger.error_exception(e)
                        msg = "データ送信時にエラーが発生しました。\r\n" + msg
                        messagebox.showerror("SocketComm.SendAuto", msg)
                        return False

            if not sendStatus:
                break # for

        return True

    def outputSocketLog(self, logStr, logType):
        
        # 日時取得
        dt_now = datetime.datetime.now()

        # スクリプトがあるディレクトリ（PyInstaller EXEにも対応）
        if getattr(sys, 'frozen', False):
            # PyInstaller実行時
            currentPath = os.path.dirname(sys.executable)
        else:
            # pyスクリプト実行時
            currentPath = os.path.dirname(os.path.abspath(__file__))

        # logフォルダのパスを作成
        logDir = os.path.join(currentPath, "log")

        # logフォルダがなければ作成
        os.makedirs(logDir, exist_ok=True)

        # 出力先フルパス
        txtPath = os.path.join(logDir, "socketLog" + dt_now.strftime("%Y%m%d") + "_" + self.charactor_code + ".txt")

        # 送信ログ、受信ログ、それ以外
        logOpt = ""
        if logType == "None":
            logOpt = "\t----\t" # その他ログ
        if logType == "Send":
            logOpt = "\t--->\t" # 送信ログ
        if logType == "Recv":
            logOpt = "\t<---\t" # 受信ログ

        # ファイル書き出し
        f = open(txtPath, "a", encoding=self.charactor_code)
        f.write(dt_now.strftime("%Y/%m/%d %H:%M:%S"))
        f.write(logOpt)
        f.write(logStr)
        f.write("\n")
        f.close()

        self.gui.txtSocketLog.insert("1.0", 
                                     dt_now.strftime("%Y/%m/%d %H:%M:%S") 
                                     + logOpt 
                                     + logStr 
                                     + "\r\n")
        self.gui.txtSocketLog.update()

        print(logStr)
