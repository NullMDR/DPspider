import os
import re
from typing import List, AnyStr
from tqdm import tqdm

from dump.dump_config import DUMP_FILE_SHOPS, DUMP_FILE_SHOP_DETAILS
from dump.dump_utils import decode_json_stacked, shop_idx, encode_json, inject_cookie, try_http_request
from log import getLogger
from settings import HEADERS
from shop import Shop

logger = getLogger(__name__)
RE_REVIEW_TAGS = re.compile(r'^(.*)\((\d+)\)$')


def parse_review_tags(review_tags: List[AnyStr]):
    result = {}
    if review_tags is None:
        return result
    for tag_str in review_tags:
        match = RE_REVIEW_TAGS.search(tag_str)
        if match:
            result[match.group(1)] = match.group(2)
    return result


def dump_details():
    try:
        details_dict = {}
        if os.path.exists(DUMP_FILE_SHOP_DETAILS):
            with open(DUMP_FILE_SHOP_DETAILS, 'r') as f:
                doc_details = f.read()
            for shop_details in decode_json_stacked(doc_details):
                idx = shop_idx(shop_details)
                details_dict[idx] = shop_details

        with open(DUMP_FILE_SHOPS, 'r') as f:
            doc_shops = f.read()

        shop_data_list = list(decode_json_stacked(doc_shops))
        progress_bar = tqdm(range(len(shop_data_list)), unit='shop', position=0, dynamic_ncols=True)

        with open(DUMP_FILE_SHOP_DETAILS, 'a') as f:
            for cur in progress_bar:
                shop_data = shop_data_list[cur]
                idx = shop_data['店铺ID']
                if details_dict.get(idx) is not None:
                    continue
                shop = Shop(shop_idx(shop_data))
                headers = inject_cookie(HEADERS)
                try_http_request(
                    lambda: shop.get(headers=headers),
                    lambda cookies: inject_cookie(headers, cookies))
                shop.get(headers=inject_cookie(HEADERS))
                to_extend = {
                    'comment_kinds': shop.comment_kinds,
                    'review_tags': parse_review_tags(shop.review_tags),
                    'scores': shop.scores,
                }
                shop_data.update(to_extend)
                f.write(encode_json(shop_data))
                f.flush()
        progress_bar.close()
    finally:
        logger.info(f'Data dumped to {DUMP_FILE_SHOP_DETAILS}')
