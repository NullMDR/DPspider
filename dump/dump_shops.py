from city import City
from dump.dump_config import\
    DUMP_CITY_NAMES, DUMP_KEYWORD, DUMP_FILE_SHOPS
from dump.dump_utils import add_results_to_output, inject_cookie
from log import getLogger

logger = getLogger(__name__)


def dump_shops():
    try:
        for cityName in DUMP_CITY_NAMES:
            city = City(cityName)
            inject_cookie(city.headers)
            inject_cookie(city.map_headers)
            city.get()
            results = city.search(DUMP_KEYWORD)
            add_results_to_output(results, DUMP_FILE_SHOPS)
    finally:
        logger.info(f'Data dumped to {DUMP_FILE_SHOPS}')



