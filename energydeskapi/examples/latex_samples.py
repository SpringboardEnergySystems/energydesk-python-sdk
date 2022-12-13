import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.pdfgenerator.latex_api import LatexApi
from energydeskapi.types.company_enum_types import CompanyTypeEnum, CompanyRoleEnum

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

def convert_tex2pdf_as_attachment(api_conn):
    textfile = '.'
    pdf = LatexApi.download_pdf_attachment(api_conn, textfile)
    print(pdf)

def convert_tex2pdf_as_stream(api_conn):
    textfile = '.'
    pdf = LatexApi.download_pdf_stream(api_conn, textfile)
    print(pdf)

if __name__ == '__main__':

    api_conn=init_api()
    convert_tex2pdf_as_stream(api_conn)
