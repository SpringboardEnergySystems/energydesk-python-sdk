import logging
import pandas as pd

logger = logging.getLogger(__name__)

class LatexApi:

    @staticmethod
    def upload_pdf_download(api_connection, pdf_file):
        payload = {"tex_file": "tex_file"}
        print(payload)
        response = api_connection.exec_post_url(
            '/api/latex2pdf-download/', payload)
        if response:
            return response
        return None

    @staticmethod
    def upload_pdf_email(api_connection, pdf_file):
        payload = {"tex_file": "tex_file",
                   "email_receipients": "string"}
        response = api_connection.exec_post_url(
            '/api/latex2pdf-email/', payload)
        if response:
            return response
        return None

    @staticmethod
    def upload_pdf_stream(api_connection, pdf_file):
        payload = {"tex_file": "tex_file"}
        print(payload)
        response = api_connection.exec_post_url(
            '/api/latex2pdf-stream/', payload)
        if response:
            return response
        return None
