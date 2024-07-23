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
                if 'Series' in title or re.search(r'\bS\d{1,2} E\d{1,2}\b', name):
                    series.append(current_entry)
                else:
                    movies.append(current_entry)

    return movies, series


def write_strm_files(entries, base_dir):
    for entry in entries:
        if 'name' in entry and 'url' in entry:
            name = entry['name']
            title = entry.get('title', '')

            # Determine if it is a series based on the name format
            is_series = re.search(r'\bS\d{1,2} E\d{1,2}\b', name)

            if is_series or 'Series' in title:
                # Create directory structure for series
                # Extract show name, season, and episode information
                match = re.search(r'^(.*) S(\d{1,2}) E(\d{1,2})$', name)
                if match:
                    show_name, season, episode = match.groups()
                    season_dir = f"Season {int(season):02d}"
                    safe_show_name = show_name.replace(':', '').replace('/', '_').replace('\\', '_').replace('?', '').replace('*', '')
                    dir_path = os.path.join(base_dir, 'series', safe_show_name, season_dir)
                    os.makedirs(dir_path, exist_ok=True)
                    safe_name = f"{safe_show_name} S{season} E{episode}".replace(':', '').replace('/', '_').replace('\\', '_').replace('?', '').replace('*', '')
                else:
                    # Handle cases where season and episode are not correctly formatted
                    print(f"Warning: Could not parse series info for: {name}")
                    continue
            else:
                # Create directory structure for movies
                safe_name = name.replace(':', '').replace('/', '_').replace('\\', '_').replace('?', '').replace('*', '')
                dir_path = os.path.join(base_dir, 'movies', safe_name)
                os.makedirs(dir_path, exist_ok=True)
                safe_name = safe_name

            # Generate a valid filename
            file_name = safe_name + '.strm'
            file_path = os.path.join(dir_path, file_name)

            # Write the URL to the STRM file
            with open(file_path, 'w', encoding='utf-8') as strm_file:
                strm_file.write(entry['url'])
