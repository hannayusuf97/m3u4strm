import os
import re
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from log_and_progress import log_message, update_progress

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
            line = line[len('#EXTINF:-1 '):]
            parts = line.split('",', 1)
            attribute_string = parts[0] + '"'
            name = parts[1].strip()

            attributes = re.findall(r'(\w+)=["\']([^"\']+)["\']', attribute_string)
            for key, value in attributes:
                current_entry[key.strip()] = value.strip()

            current_entry['name'] = name
        elif line.startswith('http'):
            if any(line.lower().endswith(ext) for ext in media_extensions):
                current_entry['url'] = line
                title = current_entry.get('title', '')
                name = current_entry['name']

                if 'Series' in title or re.search(r'\b[Ss][._-]?(\d{1,3})[._-]?E(\d{1,4})\b', name):
                    series.append(current_entry)
                else:
                    movies.append(current_entry)

    return movies, series

def sanitize_filename(name):
    name = re.sub(r'[\\/*?:"<>|]', '', name).strip()
    name = name.replace('...', '…').replace('..', '…')
    name = name.replace('\t', '').replace('\n', '').strip().rstrip('. ')
    return name

def remove_season_episode_info(name):
    name = re.sub(r'\b[Ss][._-]?(\d{1,3})[._-]?E(\d{1,4})\b', '', name)
    name = re.sub(r'\b[Ss][._-]?(\d{1,3})\b', '', name)
    return name.strip()

def write_strm_file(entry, base_dir, file_type):
    if 'name' in entry and 'url' in entry:
        name = entry['name']
        title = entry.get('title', '')

        is_series = re.search(r'\b[Ss][._-]?(\d{1,3})[._-]?E(\d{1,4})\b', name)

        if is_series or 'Series' in title:
            match = re.search(r'^(.*?)(?:\s+\[.*\])?\s*[Ss][._-]?(\d{1,3})[._-]?E(\d{1,4})$', name, re.IGNORECASE)
            if match:
                show_name, season, episode = match.groups()
                season = season.zfill(2)
                season_dir = f"Season {season}"
                safe_show_name = sanitize_filename(remove_season_episode_info(show_name))
                dir_path = os.path.join(base_dir, 'series', safe_show_name, season_dir)
                os.makedirs(dir_path, exist_ok=True)
                safe_name = sanitize_filename(f"{safe_show_name} S{season} E{episode}")
            else:
                log_message(f"Warning: Could not parse series info for: {name}", level='warning')
                return
        else:
            safe_name = sanitize_filename(name)
            dir_path = os.path.join(base_dir, 'movies', safe_name)
            os.makedirs(dir_path, exist_ok=True)
            safe_name = sanitize_filename(safe_name)

        file_name = safe_name + '.strm'
        file_path = os.path.join(dir_path, file_name)

        if os.path.exists(file_path):
            return

        with open(file_path, 'w', encoding='utf-8') as strm_file:
            strm_file.write(entry['url'])

def write_strm_files(entries, base_dir, file_type, max_workers):
    total_entries = len(entries)

    with tqdm(total=total_entries, desc=f"Processing {file_type}", unit="file") as pbar:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(write_strm_file, entry, base_dir, file_type) for entry in entries]
            for future in as_completed(futures):
                pbar.update(1)

def main():
    m3u_file_path = 'path_to_your_m3u_file.m3u'
    output_dir = 'path_to_output_directory'

    max_workers = max(1, os.cpu_count() - 2)

    movies, series = parse_m3u(m3u_file_path)

    write_strm_files(movies, output_dir, 'movies', max_workers)
    write_strm_files(series, output_dir, 'series', max_workers)

if __name__ == '__main__':
    main()
