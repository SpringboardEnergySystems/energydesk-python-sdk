from energydeskapi.assetdata.formats.fileformats import get_parser, FileFormatEnum
import os
if __name__ == '__main__':
    parser=get_parser(FileFormatEnum.POWERSITE)
    file="BH-2022-003_40min.csv"
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    #pd.set_option('display.max_rows', None)
    fil = os.path.join(__location__, file)
    parser(open(fil).read())