import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.pdfgenerator.latex_api import LatexApi
from energydeskapi.types.company_enum_types import CompanyTypeEnum, CompanyRoleEnum

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

def upload_pdf(api_conn):
    pdf_file = 'C:/Users/57884/pycharmprojects/energydesk-python-sdk/sample.pdf'
    pdf = LatexApi.upload_pdf_download(api_conn, pdf_file)
    print(pdf)


if __name__ == '__main__':

    api_conn=init_api()
    upload_pdf(api_conn)
