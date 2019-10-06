import xlsxwriter

from dump.dump_config import DUMP_FILE_OUTPUT


def gen_output():
    workbook = xlsxwriter.Workbook(DUMP_FILE_OUTPUT)


