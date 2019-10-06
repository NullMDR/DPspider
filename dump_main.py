import os
import sys
from typing import Dict, Callable

from config import LOG_FILE_SAVE_PATH
from dump.dump_config import DUMP_FOLDER
from dump.dump_shops import dump_shops
from dump.dump_details import dump_details
from dump.gen_output import gen_output

dump_fn: Dict[str, Callable[[], None]] = {
    'dump_shops': dump_shops,
    'dump_details': dump_details,
    'gen_output': gen_output,
}


def usage_and_exit():
    print('Usage:')
    print('\t', sys.argv[0], '[command]')
    print('Allowed commands:')
    print('\t', ' '.join(dump_fn.keys()))
    sys.exit(-1)


def main():
    if len(sys.argv) != 2:
        usage_and_exit()

    command = dump_fn.get(sys.argv[1])
    if command is None:
        usage_and_exit()

    if os.path.exists(LOG_FILE_SAVE_PATH):
        os.unlink(LOG_FILE_SAVE_PATH)

    if not os.path.exists(DUMP_FOLDER):
        os.mkdir(DUMP_FOLDER)

    command()


if __name__ == '__main__':
    main()
