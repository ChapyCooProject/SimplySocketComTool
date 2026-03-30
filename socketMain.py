import tkinter as tk
from form_Creator import FormCreator

if __name__ == "__main__":

    # Windowを生成
    root = tk.Tk()
    
    # Windowを親要素として、frame　Widget(tk.Frame)を作成。
    app = FormCreator(master = root)

    # Windowを生成
    app.mainloop()

