from typing import Optional
import requests
from requests.auth import HTTPBasicAuth


class Geoserver:
    def __init__(self, url: str, username: str, password: str) -> None:
        self.url = url
        self.username = username
        self.password = password

    def get_workspaces(self) -> Optional[dict]:
        api_endpoint = "/rest/workspaces/"
        response = requests.get(
            self.url + api_endpoint,
            headers={"Accept": "application/json"},
            auth=HTTPBasicAuth(self.username, self.password),
        )
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print("Error:", response.status_code)
            return None
