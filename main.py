from utils import write_strm_files, parse_m3u


def main():
    m3u_file = 'test.m3u'  # Replace with your M3U file path
    output_dir = 'Result'  # Replace with your desired output directory

    movies, series = parse_m3u(m3u_file)

    write_strm_files(movies, output_dir)
    write_strm_files(series, output_dir)


if __name__ == '__main__':
    main()
