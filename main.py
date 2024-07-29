import os
from log_and_progress import log_message
from utils import write_strm_files, parse_m3u


def main():
    m3u_files = ['tv_channels_Ahmedmahbob_plus.m3u']
    for m3u_file in m3u_files:
        try:
            base_name = os.path.basename(m3u_file).split('.')[0]
            output_dir = f'Result_{base_name}'
            log_message(f"Processing m3u File: {m3u_file}", level='info')

            movies, series = parse_m3u(m3u_file)
            max_workers = max(1, os.cpu_count() - 2)

            write_strm_files(movies, output_dir, 'movies', max_workers)
            write_strm_files(series, output_dir, 'series', max_workers)

            log_message(f"Processing completed for: {m3u_file}", level='info')
        except Exception as e:
            log_message(f"Error processing {m3u_file}: {str(e)}", level='error')


if __name__ == '__main__':
    main()
