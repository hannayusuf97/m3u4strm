# app.py
import tkinter as tk
from tkinter import filedialog
from m3u_parser import parse_m3u
from m3u_gui import M3UGUI

def main():
    root = tk.Tk()
    app = M3UGUI(root)

    # Open file dialog to select M3U file
    file_path = filedialog.askopenfilename(
        filetypes=[("M3U Files", "*.m3u"), ("All Files", "*.*")]
    )
    if file_path:
        movies, series = parse_m3u(file_path)
        app.load_data(movies, series)

    root.mainloop()

if __name__ == "__main__":
    main()
