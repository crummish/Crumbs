import pathlib
import bs4
import argparse
import copy

def intersperse(lst, item):
    result = [copy.deepcopy(item) for _ in range(len(lst) * 2 - 1)]
    result[::2] = lst
    return result

def sort_mods(mods: bs4.Tag):
    return intersperse(
        sorted(
            mods.ul.find_all('li'),
            key=lambda x: x.text.lower()
        ),
        bs4.NavigableString('\n')
    )

def main():
    args = argument_parser().parse_args()
    
    with pathlib.Path(args.file).open('r') as fp:
        soup = bs4.BeautifulSoup(fp, 'html.parser')
        soup.ul.contents = [bs4.NavigableString('\n')] + sort_mods(soup) + [bs4.NavigableString('\n')]

    with pathlib.Path(args.output or args.file).open('w') as file:
        file.write(str(soup))

def argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Sort a standard Curse modpack mod list file by mod name.')
    parser.add_argument(
        'file',
        help='The mod list file to be sorted.'
    )
    parser.add_argument(
        '-o',
        '--output',
        help='The file to write output to.'
    )
    return parser

if __name__ == '__main__':
    main()
