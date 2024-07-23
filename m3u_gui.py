import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
import io
import re
from utils import parse_m3u, write_strm_files


class M3UGUI:
    def __init__(self, root):
        self.root = root
        self.root.geometry("800x600")

        # Initialize data storage
        self.movies = []
        self.series = []
        self.selected_items = []  # Track selected items
        self.series_displayed = 0  # Track number of series displayed
        self.series_chunk_size = 10  # Number of series items to display per chunk

        # Set up the tabs
        self.tab_control = ttk.Notebook(root)

        self.movies_tab = ttk.Frame(self.tab_control)
        self.series_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.movies_tab, text="Movies")
        self.tab_control.add(self.series_tab, text="Series")
        self.tab_control.pack(expand=1, fill="both")

        # Create search bar and buttons
        self.create_widgets()

        # Initialize scrollbars
        self.setup_scrollbars()

    def create_widgets(self):
        # Search frame
        search_frame = tk.Frame(self.root)
        search_frame.pack(fill="x")

        tk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.search_button = tk.Button(search_frame, text="Search", command=self.search)
        self.search_button.pack(side="left", padx=5)

        # Buttons for actions
        action_frame = tk.Frame(self.root)
        action_frame.pack(fill="x")

        self.add_button = tk.Button(action_frame, text="Add to List", command=self.add_to_list)
        self.add_button.pack(side="left", padx=5)

        self.remove_button = tk.Button(action_frame, text="Remove from List", command=self.remove_from_list)
        self.remove_button.pack(side="left", padx=5)

        self.generate_button = tk.Button(action_frame, text="Generate STRM", command=self.generate_strm)
        self.generate_button.pack(side="left", padx=5)

    def setup_scrollbars(self):
        self.movies_canvas = tk.Canvas(self.movies_tab)
        self.movies_scrollbar = tk.Scrollbar(self.movies_tab, orient="vertical", command=self.movies_canvas.yview)
        self.movies_canvas.configure(yscrollcommand=self.movies_scrollbar.set)

        self.movies_scrollbar.pack(side="right", fill="y")
        self.movies_canvas.pack(side="left", fill="both", expand=True)

        self.series_canvas = tk.Canvas(self.series_tab)
        self.series_scrollbar = tk.Scrollbar(self.series_tab, orient="vertical", command=self.series_canvas.yview)
        self.series_canvas.configure(yscrollcommand=self.series_scrollbar.set)

        self.series_scrollbar.pack(side="right", fill="y")
        self.series_canvas.pack(side="left", fill="both", expand=True)

        self.movies_canvas_frame = tk.Frame(self.movies_canvas)
        self.movies_canvas.create_window((0, 0), window=self.movies_canvas_frame, anchor="nw")
        self.movies_canvas_frame.bind("<Configure>", lambda e: self.movies_canvas.configure(
            scrollregion=self.movies_canvas.bbox("all")))

        self.series_canvas_frame = tk.Frame(self.series_canvas)
        self.series_canvas.create_window((0, 0), window=self.series_canvas_frame, anchor="nw")
        self.series_canvas_frame.bind("<Configure>", lambda e: self.series_canvas.configure(
            scrollregion=self.series_canvas.bbox("all")))

        self.series_canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

    def load_data(self, movies, series):
        self.movies = [m for m in movies if self.is_valid_media_url(m.get('url'))]
        self.series = [s for s in series if self.is_valid_series_name(s['name'])]

        # Use threading to update tabs asynchronously
        threading.Thread(target=self.update_tabs).start()

    def update_tabs(self):
        self.update_movies_tab()
        self.load_more_series()

    def update_movies_tab(self):
        # Clear existing widgets
        for widget in self.movies_canvas_frame.winfo_children():
            widget.destroy()

        for movie in self.movies:
            name = movie['name']
            url = movie['url']
            image_url = movie.get('logo', '')

            # Display movie title and image (if available)
            movie_frame = tk.Frame(self.movies_canvas_frame)
            movie_frame.pack(fill="x", pady=5)

            title_label = tk.Label(movie_frame, text=name)
            title_label.pack(side="left", padx=5)

            if image_url:
                # Create a label for the image
                image_label = tk.Label(movie_frame)
                image_label.pack(side="left", padx=5)
                # Load the image asynchronously
                self.load_image_async(image_url, image_label)

            # Create a variable for the Checkbutton
            var = tk.BooleanVar()
            checkbutton = tk.Checkbutton(movie_frame, text="Select", variable=var)
            checkbutton.var = var  # Store the variable for later use
            checkbutton.pack(side="right", padx=5)

    def load_more_series(self):
        # Display a chunk of series items
        start = self.series_displayed
        end = min(start + self.series_chunk_size, len(self.series))

        # Create a dictionary to group series by show name and season
        series_groups = {}
        for i in range(start, end):
            series_item = self.series[i]
            name = series_item['name']
            show_name, season_episode = self.parse_series_name(name)
            url = series_item['url']

            if show_name  not in series_groups:
                series_groups[show_name] = {}
            if season_episode[0] not in series_groups[show_name]:
                series_groups[show_name][season_episode[0]] = []
            series_groups[show_name][season_episode[0]].append((season_episode[1], url))

        # Create UI for each show and its seasons
        for show_name, seasons in series_groups.items():
            show_frame = tk.Frame(self.series_canvas_frame)
            show_frame.pack(fill="x", pady=5)

            tk.Label(show_frame, text=show_name, font=("Helvetica", 16, "bold")).pack(pady=5)

            for season, episodes in seasons.items():
                season_frame = tk.Frame(show_frame)
                season_frame.pack(fill="x", pady=5)

                tk.Label(season_frame, text=f"Season {season}", font=("Helvetica", 14, "bold")).pack(pady=5)

                episode_frame = tk.Frame(season_frame)
                episode_frame.pack(fill="x", pady=2)

                for episode, url in episodes:
                    episode_frame = tk.Frame(season_frame)
                    episode_frame.pack(fill="x", pady=2)

                    tk.Label(episode_frame, text=f"Episode {episode}").pack(side="left", padx=5)
                    tk.Checkbutton(episode_frame, text="Select", variable=tk.BooleanVar()).pack(side="right", padx=5)

        self.series_displayed = end

        # If there are more series items, bind the event to load more on scroll
        if end < len(self.series):
            self.series_canvas.bind("<Configure>", self.on_series_scroll)

    def parse_series_name(self, name):
        """Parse the series name to extract show name, season, and episode."""
        match = re.search(r'^(.*) S(\d{1,2}) E(\d{1,2})$', name)
        if match:
            show_name, season, episode = match.groups()
            return show_name, (season, episode)
        return name, ("Unknown", "Unknown")

    def is_valid_media_url(self, url):
        """Check if the URL is a valid media URL."""
        return url and url.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.flv', '.webm'))

    def is_valid_series_name(self, name):
        """Check if the name matches the series naming pattern."""
        return re.search(r' S\d{1,2} E\d{1,2}$', name) is not None

    def search(self):
        query = self.search_entry.get().lower()
        if query:
            # Update tabs based on search query
            self.update_tabs(filtered=True, query=query)

    def load_image_async(self, image_url, image_label):
        """Load image in a separate thread."""

        def load_image():
            try:
                response = requests.get(image_url)
                image_data = io.BytesIO(response.content)
                image = Image.open(image_data)
                image.thumbnail((100, 100))  # Resize image
                photo = ImageTk.PhotoImage(image)
                # Update the label with the loaded image
                image_label.config(image=photo)
                image_label.image = photo  # Keep reference to avoid garbage collection
            except Exception as e:
                print(f"Error loading image: {e}")

        threading.Thread(target=load_image).start()

    def add_to_list(self):
        # Add selected items to a list to be converted to STRM files
        selected_items = self.get_selected_items()
        self.selected_items.extend(selected_items)

    def remove_from_list(self):
        # Remove selected items from the list
        selected_items = self.get_selected_items()
        self.selected_items = [item for item in self.selected_items if item not in selected_items]

    def generate_strm(self):
        # Call the function to generate STRM files
        output_dir = 'path_to_output_directory'  # Replace with your desired output directory
        write_strm_files(self.selected_items, output_dir)
        messagebox.showinfo("Success", "STRM files have been generated.")

    def get_selected_items(self):
        # Gather selected items based on checkboxes
        selected_items = []
        for widget in self.movies_canvas_frame.winfo_children() + self.series_canvas_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Checkbutton) and child.var.get():
                        # Add the item to the selected_items list
                        # Assuming items have a unique identifier or URL
                        selected_items.append(self.find_item_by_checkbox(child))
        return selected_items

    def find_item_by_checkbox(self, checkbutton):
        # Find the corresponding item for the checkbox
        return None  # Replace with your implementation

    def on_series_scroll(self, event=None):
        # Check if scrollbar is at bottom and load more items
        if self.series_canvas.yview()[1] == 1.0:
            self.load_more_series()

    def on_mouse_wheel(self, event):
        # Handle mouse wheel scrolling
        if event.widget == self.series_canvas:
            self.series_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


if __name__ == "__main__":
    root = tk.Tk()
    app = M3UGUI(root)

    movies = [
        {'name': 'Movie 1', 'url': 'http://example.com/movie1', 'logo': 'http://example.com/movie1.jpg'},
        # Add more movie entries as needed
    ]
    series = [
        {'name': 'Black Mirror S01 E01', 'url': 'http://example.com/black_mirror_s01_e01'},
        {'name': 'Black Mirror S01 E02', 'url': 'http://example.com/black_mirror_s01_e02'},
        {'name': 'Black Mirror S02 E01', 'url': 'http://example.com/black_mirror_s02_e01'},
        # Add more series entries as needed
    ]

    # Load example data
    app.load_data(movies, series)

    root.mainloop()
