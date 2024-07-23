import os
import re

def parse_m3u(file_path):
    media_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mpg')

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    movies = []
    series = []

    current_entry = {}
    for line in lines:
        line = line.strip()
        if line.startswith('#EXTINF'):
            current_entry = {}
            line = line[len('#EXTINF:-1 '):]  # Remove the "#EXTINF:-1 " part
            parts = line.split('",', 1)
            attribute_string = parts[0] + '"'  # Add back the ending quote
            name = parts[1].strip()

            # Use regex to correctly split key-value pairs considering spaces and quotes
            attributes = re.findall(r'(\w+)=["\']([^"\']+)["\']', attribute_string)
            for key, value in attributes:
                current_entry[key.strip()] = value.strip()

            current_entry['name'] = name
        elif line.startswith('http'):
            # Check if the URL has a valid media file extension
            if any(line.lower().endswith(ext) for ext in media_extensions):
                current_entry['url'] = line
                title = current_entry.get('title', '')
                name = current_entry['name']

                # Determine if it's a series or movie based on title and name pattern
                if 'Series' in title or re.search(r'\bS\d{1,3} E\d{1,3}\b', name):
                    series.append(current_entry)
                else:
                    movies.append(current_entry)

    return movies, series

def sanitize_filename(name):
    # Remove or replace characters that are not safe for filenames
    name = re.sub(r'[\\/*?:"<>|]', '', name).strip()
    # Replace ellipses with a safer alternative
    name = name.replace('...', '…').replace('..', '…')
    # Remove any leading or trailing whitespace and dots
    name = name.strip().rstrip('. ')
    return name

def write_strm_files(entries, base_dir):
    for entry in entries:
        if 'name' in entry and 'url' in entry:
            name = entry['name']
            title = entry.get('title', '')

            # Determine if it is a series based on the name format
            is_series = re.search(r'\bS\d{1,3} E\d{1,3}\b', name)

            if is_series or 'Series' in title:
                # Create directory structure for series
                # Extract show name, season, and episode information
                match = re.search(r'^(.*) S(\d{1,3}) E(\d{1,3})$', name)
                if match:
                    show_name, season, episode = match.groups()
                    season_dir = f"Season {int(season):03d}"
                    safe_show_name = sanitize_filename(show_name)
                    dir_path = os.path.join(base_dir, 'series', safe_show_name, season_dir)
                    os.makedirs(dir_path, exist_ok=True)
                    safe_name = sanitize_filename(f"{safe_show_name} S{season} E{episode}")
                else:
                    # Handle cases where season and episode are not correctly formatted
                    print(f"Warning: Could not parse series info for: {name}")
                    continue
            else:
                # Create directory structure for movies
                safe_name = sanitize_filename(name)
                dir_path = os.path.join(base_dir, 'movies', safe_name)
                os.makedirs(dir_path, exist_ok=True)
                safe_name = sanitize_filename(safe_name)

            # Generate a valid filename
            file_name = safe_name + '.strm'
            file_path = os.path.join(dir_path, file_name)

            # Write the URL to the STRM file
            with open(file_path, 'w', encoding='utf-8') as strm_file:
                strm_file.write(entry['url'])

            # Debugging information
            print(f"Created STRM file at: {file_path}")
            print(f"Directory structure: {dir_path}")

# Example usage:
# movies, series = parse_m3u('path_to_your_m3u_file.m3u')
# write_strm_files(movies, 'path_to_movies_directory')
# write_strm_files(series, 'path_to_series_directory')
