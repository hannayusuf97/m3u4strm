# m3u_parser.py
import os
import re

def parse_m3u(file_path):
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
            current_entry['url'] = line
            url = current_entry['url']
            if not is_playable_url(url):
                continue  # Skip non-playable URLs

            title = current_entry.get('title', '')
            name = current_entry['name']

            # Determine if it's a series or movie based on title and name pattern
            is_series = re.search(r'\bS\d{1,2} E\d{1,2}\b', name)

            if 'Series' in title or is_series:
                series.append(current_entry)
            else:
                movies.append(current_entry)

    return movies, series

def is_playable_url(url):
    return url.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.webm'))
