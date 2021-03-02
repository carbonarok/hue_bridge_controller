import json
import requests

import hue_bridge_controller.config as config

from hue_bridge_controller.exceptions import HueBridgeControllerException


class BridgeRequests:
    def __init__(self):
        config.load()
        self.verify = True

    def set_request_verification(self, value):
        self.verify = value

    def request(self, verb, url, protocol="https", body=None):
        if body:
            body = json.dumps(body)
        complete_url = f"{protocol}://{config.SETTINGS.bridge_host}/api/{config.SETTINGS.username}/{url}"
        response = requests.request(verb, complete_url, data=body, verify=self.verify)
        if 199 < response.status_code < 300:
            return response.json()
        else:
            print(response.status_code)
            raise HueBridgeControllerException

    def get_lights(self):
        return self.request("GET", "lights")

    def set_light(self, id, configuration, route=None):
        if not route:
            route = ""
        return self.request("PUT", f"lights/{id}/{route}", body=configuration)

    def get_groups(self):
        return self.request("GET", "groups")
