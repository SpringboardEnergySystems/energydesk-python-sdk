import logging
import pandas as pd
import requests
import environ

logger = logging.getLogger(__name__)

class LatexApi:
    @staticmethod
    def exec_post(server_url, payload):
        env = environ.Env()
        base_url = None if 'ENERGYDESK_LATEX_URL' not in env else env.str('ENERGYDESK_LATEX_URL')
        server_url = base_url + server_url
        logger.info("Calling URL " + str(server_url))
        print(payload)
        logger.debug("...with payload " + str(payload) )
        return requests.post(server_url, json=payload)

    @staticmethod
    def download_pdf_attachment(api_connection, tex_file):
        payload = {"tex_file":tex_file}
        print(payload)
        response = LatexApi.exec_post(
            '/api/pdflatex/latex2pdf-download/', payload)
        fb = open("./loc2.pdf", "wb")
        fb.write(response.content)
        fb.close()
        return None

    @staticmethod
    def convert_and_email(api_connection, tex_file):
        payload = {"tex_file": tex_file,
                   "email_receipients": "string"}
        response = LatexApi.exec_post(
            '/api/pdflatex/latex2pdf-email/', payload)
        if response:
            return response
        return None

    @staticmethod
    def download_pdf_stream(api_connection, tex_file):
        payload = {"tex_file": tex_file}
        print(payload)
        response = LatexApi.exec_post(
            '/api/pdflatex/latex2pdf-stream/', payload)
        # fb=open("./loc.pdf", "wb")
        # fb.write(response.content)
        # fb.close()

        return response.content
