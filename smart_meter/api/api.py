import requests
import json
import os


class APIHandler:
    def __init__(self, api_url, uid):
        self._api_url = api_url
        self._uid = uid

    def send_data(self, data):
        headers = {
            'Content-Type': 'application/json'
        }

        certificate_path = f"/sm/{self._uid}/cert.pem"

        if not os.path.exists(certificate_path):
            return False

        try:
            response = requests.post(self._api_url, data=json.dumps(data), headers=headers, verify=certificate_path)

            if response.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            return False