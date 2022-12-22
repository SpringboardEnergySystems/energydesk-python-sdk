import logging
import pandas as pd
import requests
logger = logging.getLogger(__name__)

class LatexApi:
    @staticmethod
    def exec_post(server_url, payload):
        server_url = "https://test-latex.hafslund.energydesk.no" + server_url
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
