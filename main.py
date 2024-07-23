# app.py
import tkinter as tk
from m3u_parser import parse_m3u
from m3u_gui import M3UGUI


def main():
    root = tk.Tk()
    app = M3UGUI(root)

    # Load sample data or actual data
    sample_movies = [
        {'name': 'Movie 1', 'url': 'http://example.com/movie1.mp4'},
        {'name': 'Movie 2', 'url': 'http://example.com/movie2.mkv'}
    ]
    sample_series = [
        {'name': 'Series 1 S01 E01', 'url': 'http://example.com/series1s01e01.mp4', 'title': 'Series', 'season': '01',
         'episode': '01'},
        {'name': 'Series 1 S01 E02', 'url': 'http://example.com/series1s01e02.mp4', 'title': 'Series', 'season': '01',
         'episode': '02'}
    ]

    app.load_data(sample_movies, sample_series)

    root.mainloop()


if __name__ == "__main__":
    main()
