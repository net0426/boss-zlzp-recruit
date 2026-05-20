import requests


class AiPage:
    @staticmethod
    def text_open(address):
        with open(address, 'r', encoding='utf-8') as f:
            im = f.read()
        return im