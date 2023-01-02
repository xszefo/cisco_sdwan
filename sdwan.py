#!/usr/bin/env python

import requests
import tabulate
import click
import creds

import urllib3
urllib3.disable_warnings()

class Connector:
    def __init__(self, username, password, base_url):
        self.username = username
        self.password = password
        self.base_url = base_url

    def connect(self):
        self.get_session_cookie()
        self.get_token()

    def get_session_cookie(self):
        url = self.base_url + 'j_security_check'
        payload = {'j_username': self.username, 'j_password': self.password}

        response = requests.post(url, data=payload, verify=False)
        if response.status_code != 200:
            print('Cannot download a cookie')
            return 0
        self.session_cookie = response.headers['Set-cookie'].split(';')[0]
        return 1

    def get_token(self):
        url = self.base_url + 'dataservice/client/token'
        headers = {'Cookie': self.session_cookie}

        response = requests.get(url, headers=headers, verify=False)
        if response.status_code != 200:
            print('Cannot get a token')
            return 0
        self.token = response.text
        return 1

    @property
    def headers(self):
        return {'Cookie': self.session_cookie, 'X-XSRF-TOKEN': self.token}
    
    def get_data(self, path, params=None):
        url = self.base_url + path
        
        response = requests.get(url, headers=self.headers, params=params, verify=False)
        if response.status_code != 200:
            print(response.status_code)
            print(response.text)
            exit()

        items = response.json()['data']
        return items

    def get_devices(self):
        devices = []
        items = self.get_data('dataservice/device')

        for item in items:
            devices.append(
                [
                    item['deviceId'],
                    item['host-name'],
                    item['site-id'],
                    item['system-ip'],
                    item['board-serial'],
                    item['device-model'],
                    item['version'],
                    item['uuid'],
                ]
            )
        return devices
    
    def get_templates(self):
        templates = []
        params = {'feature': 'all'}
        items = self.get_data('dataservice/template/device', params)
        
        for item in items:
            templates.append(
                [
                     item['templateId'],
                     item['templateName'],
                     item['deviceType'],
                     item['devicesAttached'],
                     item['templateAttached']
                ]
            )
        return templates

    def get_features(self):
        features = []
        items = self.get_data('dataservice/template/feature')

        for item in items:
            features.append(
                    [
                        item['templateId'],
                        item['templateName'],
                        item['templateType']
                    ]
            )
        return features

    def get_devices_by_template(self, template_id):
        devices = []
        path = f'dataservice/template/device/config/attached/{template_id}'
        items = self.get_data(path)

        for item in items:
            devices.append(
                    [
                        item['uuid'],
                        item['host-name'],
                        item['deviceIP'],
                        item['site-id'],
                    ]
            )
        return devices

    def get_running_config(self, device_id):
        path = f'dataservice/template/config/running/{device_id}'
        items = self.get_data(path)
        return items

@click.group()
def cli():
    pass

@click.command()
def get_devices():
    conn = Connector(creds.username, creds.password, creds.base_url)
    conn.connect()

    devices = conn.get_devices()
    headers = ['Device ID', 'Name', 'Site-ID', 'System-IP', 'Board-serial', 'Model', 'Software version', 'UUID']
    print(tabulate.tabulate(devices, headers, tablefmt='fancy_grid'))

@click.command()
def get_templates():
    conn = Connector(creds.username, creds.password, creds.base_url)
    conn.connect()

    templates = conn.get_templates()
    headers = ['Template ID', 'Template Name', 'Device Type','Attached devices', 'Template version']
    print(tabulate.tabulate(templates, headers, tablefmt='fancy_grid'))

@click.command()
def get_features():
    conn = Connector(creds.username, creds.password, creds.base_url)
    conn.connect()

    features = conn.get_features()
    headers = ['Template ID', 'Template Name', 'Template Type']
    print(tabulate.tabulate(features, headers, tablefmt='fancy_grid'))


@click.command()
@click.option('-t', '--template', type=str, required=True, help='Template ID')
def get_devices_by_template(template):
    conn = Connector(creds.username, creds.password, creds.base_url)
    conn.connect()

    attached_devices = conn.get_devices_by_template(template)
    headers = ['UUID', 'Name', 'IP', 'Site-ID']
    print(tabulate.tabulate(attached_devices, headers, tablefmt='fancy_grid'))

@click.command()
@click.option('-d', '--deviceID', type=str, required=True, help='Device ID')
def get_running_config(deviceid):
    conn = Connector(creds.username, creds.password, creds.base_url)
    conn.connect()

    running_config = conn.get_running_config(deviceid)
    print(running_config)
    

cli.add_command(get_devices)
cli.add_command(get_templates)
cli.add_command(get_features)
cli.add_command(get_devices_by_template)
cli.add_command(get_running_config)

if __name__ == '__main__':
    cli()
