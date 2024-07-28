import os
from utils import write_strm_files, parse_m3u


def main():
    m3u_files = ['tv_channels_Ahmedmahbob_plus.m3u']
    for m3u_file in m3u_files:
        output_dir = 'Result_' + str('cpu_experiment').split('.')[0]
        movies, series = parse_m3u(m3u_file)
        print("Processing m3u File: " + m3u_file)
        max_workers = max(1, os.cpu_count() - 2)
        write_strm_files(movies, output_dir, 'movies', max_workers)
        write_strm_files(series, output_dir, 'series', max_workers)


if __name__ == '__main__':
    main()
