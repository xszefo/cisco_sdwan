#!/usr/bin/env python

import requests
import tabulate
from creds import username, password


class Connector:
    def __init__(self, username, password, base_url):
        self.username = username
        self.password = password
        self.base_url = base_url

    def connect(self):
        self.get_session_cookie()
        self.get_token()

    def get_session_cookie(self):
        url = self.base_url + "j_security_check"
        payload = {"j_username": self.username, "j_password": self.password}

        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print("Cannot download a cookie")
            return 0
        self.session_cookie = response.headers["Set-cookie"].split(";")[0]
        return 1

    def get_token(self):
        url = self.base_url + "dataservice/client/token"
        header = {"Cookie": self.session_cookie}

        response = requests.get(url, headers=header)
        if response.status_code != 200:
            print("Cannot get a token")
            return 0
        self.token = response.text
        return 1

    def get_devices(self):
        url = self.base_url + "dataservice/device"
        header = {"Cookie": self.session_cookie, "X-XSRF-TOKEN": self.token}
        response = requests.get(url, headers=header)
        devices = []

        if response.status_code != 200:
            print(response.status_code)
            print(response.text)
            print("Cannot get details of the devices")
            return 0

        for device in response.json()["data"]:
            devices.append(
                [
                    device["host-name"],
                    device["system-ip"],
                    device["board-serial"],
                    device["device-model"],
                    device["version"],
                ]
            )
        return devices


if __name__ == "__main__":
    base_url = "https://sandbox-sdwan-2.cisco.com/"

    conn = Connector(username, password, base_url)
    conn.connect()
    devices = conn.get_devices()

    headers = ["Name", "System-IP", "Board-serial", "Model", "Software version"]
    print(tabulate.tabulate(devices, headers, tablefmt="fancy_grid"))
