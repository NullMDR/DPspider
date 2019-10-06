import contextlib
import os
import sys
from json import JSONDecoder, JSONDecodeError, dumps
import re
from typing import Dict, AnyStr, List

from tqdm import tqdm

from dump.dump_config import DUMP_COOKIE
from log import getLogger

logger = getLogger(__name__)
NOT_WHITESPACE = re.compile(r'[^\s]')


def decode_json_stacked(document: AnyStr, pos=0, decoder=JSONDecoder()):
    while True:
        match = NOT_WHITESPACE.search(document, pos)
        if not match:
            return
        pos = match.start()

        try:
            obj, pos = decoder.raw_decode(document, pos)
        except JSONDecodeError:
            # do something sensible if there's some error
            raise
        yield obj


def encode_json(elem):
    return dumps(elem, ensure_ascii=False) + '\n'


def shop_idx(elem):
    return elem['店铺ID']


def add_results_to_output(results: List[Dict], output_file):
    elem_dict: Dict[AnyStr] = {}
    elem_no_key: List = []

    def add_elem(el):
        idx = shop_idx(el)
        if idx is None:
            elem_no_key.append(el)
        else:
            elem_dict[idx] = el

    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            document = f.read()
            for elem in decode_json_stacked(document):
                add_elem(elem)

    for elem in results:
        add_elem(elem)

    with open(output_file, 'w') as f:
        f.writelines(map(encode_json, elem_dict.values()))
        f.writelines(map(encode_json, elem_no_key))


_empty_cookie_warned = False


def inject_cookie(headers: Dict):
    headers['Cookie'] = DUMP_COOKIE
    if len(DUMP_COOKIE) == 0:
        global _empty_cookie_warned
        if not _empty_cookie_warned:
            logger.warn('Cookie is empty. Please set DUMP_COOKIE in dump/dump_config.py')
            _empty_cookie_warned = True
        del headers['Cookie']
    return headers


class DummyFile(object):
    file = None

    def __init__(self, file):
        self.file = file

    def write(self, x):
        # Avoid print() second call (useless \n)
        if len(x.rstrip()) > 0:
            tqdm.write(x, file=self.file)


@contextlib.contextmanager
def progressbar_context():
    save_stdout = sys.stdout
    sys.stdout = DummyFile(sys.stdout)
    yield
    sys.stdout = save_stdout


def progressbar_wrapped(func):
    def wrapper(self, *args, **kwargs):
        save_stdout = sys.stdout
        sys.stdout = DummyFile(sys.stdout)
        try:
            return func(self, *args, **kwargs)
        finally:
            sys.stdout = save_stdout

    return wrapper
