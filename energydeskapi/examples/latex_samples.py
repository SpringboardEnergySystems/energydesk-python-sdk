import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.pdfgenerator.latex_api import LatexApi
from energydeskapi.types.company_enum_types import CompanyTypeEnum, CompanyRoleEnum
from os.path import join, dirname
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])
tex_content_old=r"""
\documentclass{article}

\begin{document}
Hello World
\end{document}
"""

def convert_tex2pdf_as_attachment(api_conn):
    current_dir=dirname(__file__)
    docpath = join(current_dir, 'contract_sample.tex')
    tex_content=open(docpath,"r", encoding="ISO-8859-1").read().encode("latin-1").decode("utf-8")
    pdf = LatexApi.download_pdf_attachment(api_conn, tex_content)
    print(pdf)

def convert_tex2pdf_as_stream(api_conn):
    current_dir=dirname(__file__)
    docpath = join(current_dir, 'contract_sample.tex')
    tex_content=open(docpath,"r", encoding="ISO-8859-1").read().encode("latin-1").decode("utf-8")
    pdf = LatexApi.download_pdf_stream(api_conn, tex_content)
    print(pdf)

if __name__ == '__main__':

    api_conn=init_api()
    convert_tex2pdf_as_attachment(api_conn)
