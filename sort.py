import argparse
import concurrent.futures
import logging
from pathlib import Path
from shutil import copyfile, unpack_archive
from threading import Thread
from time import time

parser = argparse.ArgumentParser(description="Sorting folder")

parser.add_argument("-s", "--source", help="тека, яку потрібно обробити", required=True)
parser.add_argument(
    "-d",
    "--destination",
    help="в яку теку необхідно внести результати виконаної програми",
    default="./clean_folder",
)

args = vars(parser.parse_args())
source = Path(args.get('source'))
destination = Path(args.get('destination'))


folders = []


def grabs_folder(path: Path) -> None:
    logging.debug(f'greeting for: {path}')
    for el in path.iterdir():
        if el.is_dir():
            folders.append(el)
            inner_thread = Thread(target=grabs_folder, args=(el,))
            inner_thread.start()


def copy_file(file) -> None:
    ext = file.suffix[1:]
    new_path = destination / ext
    try:
        new_path.mkdir(exist_ok=True, parents=True)
        copyfile(file, new_path / file.name)
    except OSError as msg:
        logging.error(msg)


def archive_unpack(file):
    new_path = destination / file.stem
    try:
        new_path.mkdir(exist_ok=True, parents=True)
        unpack_archive(file, new_path / file.stem)
    except OSError as msg:
        logging.error(msg)


def do_file(path: Path):
    logging.debug(f'greeting for: {path}')
    for el in path.iterdir():
        if el.is_file():
            if el.suffix.lower().endswith(("zip", "tar")):
                archive_unpack(el)
            else:
                copy_file(el)


if '__main__' == __name__:
    start = time()
    logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')
    grabs_folder(source)

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(do_file, folders))

    logging.debug({time() - start})
