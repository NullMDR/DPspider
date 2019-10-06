import asyncio
import os
import re
from asyncio import sleep
from json import JSONDecoder, JSONDecodeError, dumps
from typing import Dict, AnyStr, List, Callable

from pyppeteer import launch

from dump.dump_config import DUMP_COOKIE
from log import getLogger

NOT_WHITESPACE = re.compile(r'[^\s]')
_last_failed_url: AnyStr or None = None


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


def inject_cookie(headers: Dict, cookie=DUMP_COOKIE):
    headers['Cookie'] = cookie
    if len(cookie) == 0:
        global _empty_cookie_warned
        if not _empty_cookie_warned:
            logger = getLogger(__name__)
            logger.warn('Cookie is empty. Please set DUMP_COOKIE in dump/dump_config.py')
            _empty_cookie_warned = True
        del headers['Cookie']
    return headers


def set_last_failed_url(url: AnyStr or None):
    global _last_failed_url
    _last_failed_url = url


def retry_url_in_browser(url: AnyStr):
    async def refresh():
        browser = await launch(headless=False)
        page = await browser.newPage()
        await asyncio.wait([
            page.goto(url),
            page.waitForNavigation()
        ])
        while True:
            if page.url == url:
                break
            await sleep(0.5)
        cookies = await page.cookies()
        await browser.close()
        return cookies

    return asyncio.get_event_loop().run_until_complete(refresh())


def try_http_request(fn: Callable[[], None], refresh_cookie_fn: Callable[[AnyStr], None]):
    set_last_failed_url(None)
    fn()
    if _last_failed_url is not None:
        cookies = retry_url_in_browser(_last_failed_url)
        refresh_cookie_fn(cookies)
        fn()

