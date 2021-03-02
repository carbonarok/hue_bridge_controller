import click
import time

import hue_bridge_controller.config as config

from hue_bridge_controller.bridge import BridgeRequests


br = BridgeRequests()


@click.group()
def main():
    pass


@click.option("--config-file", type=str, help="Config File")
@main.command()
def alert(config_file):
    config.load(config_file_name=config_file)
    lights = [1, 3]

    br.set_request_verification(False)

    lights_detail = br.get_lights()
    for light in lights:
        if not lights_detail[str(light)]["state"]["on"]:
            br.set_light(light, {"on": True}, route="state")
        print(br.set_light(light, {"bri": 254}, route="state"))
        br.set_light(light, {"hue": 0}, route="state")
        br.set_light(light, {"alert": "lselect"}, route="state")

    time.sleep(2)

    for light in lights:
        br.set_light(
            light, {"hue": lights_detail[str(light)]["state"]["hue"]}, route="state"
        )
        br.set_light(light, {"alert": "none"}, route="state")
        if not lights_detail[str(light)]["state"]["on"]:
            br.set_light(light, {"on": False}, route="state")
        else:
            br.set_light(
                light, {"bri": lights_detail[str(light)]["state"]["bri"]}, route="state"
            )
