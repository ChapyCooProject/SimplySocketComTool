import threading

def with_watch(master_attr="master"):
    # Tkinter用デコレータ：
    # ・処理中にマウスカーソルを砂時計に変更
    # ・別スレッドで重い処理を実行し、終了後にカーソルを元に戻す
    # master_attr: デコレータをつけるクラスのGUIルート属性名 (デフォルトは 'master')
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            def worker():
                try:
                    func(self, *args, **kwargs)
                except Exception as e:
                    # メインスレッドに例外を返す
                    master = getattr(self, master_attr)
                    master.after(0, lambda e=e: raise_exception(e))
                finally:
                    # メインスレッドでカーソルを戻す
                    master = getattr(self, master_attr)
                    master.after(0, lambda: master.config(cursor=""))
            def raise_exception(e):
                raise e
            # 砂時計表示
            master = getattr(self, master_attr)
            master.config(cursor="watch")
            master.update()

            # 別スレッドで実行
            threading.Thread(target=worker, daemon=True).start()

        return wrapper
    return decorator