import logging
import pandas as pd

logger = logging.getLogger(__name__)

class LatexApi:

    @staticmethod
    def download_pdf_attachment(api_connection, tex_file):
        payload = {"tex_file":tex_file}
        print(payload)
        response = api_connection.exec_post_url(
            '/api/latex2pdf-download/', payload)
        if response:
            return response
        return None

    @staticmethod
    def convert_and_email(api_connection, tex_file):
        payload = {"tex_file": tex_file,
                   "email_receipients": "string"}
        response = api_connection.exec_post_url(
            '/api/latex2pdf-email/', payload)
        if response:
            return response
        return None

    @staticmethod
    def download_pdf_stream(api_connection, tex_file):
        payload = {"tex_file": tex_file}
        print(payload)
        response = api_connection.exec_post_url_binary(
            '/api/latex2pdf-stream/', payload)
        print(response.text)

        return None
