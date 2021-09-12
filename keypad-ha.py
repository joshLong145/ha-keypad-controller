#!/usr/bin/python3

import asyncio
from evdev import InputDevice, categorize, ecodes
import threading
import websocket
import json

DEV_PATH = "/dev/input/event1"
AUTH_TOKEN = "<YOUR-TOKEN>"
id_stamp = [0]
BRIGHTNESS = [101]
ALL_ON = [True]

def on_message(ws, message):
    print('recieved channel message')
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("socket closed", close_msg)

def on_open(ws):
    print("socket established entering auth...")
    ws.send(json.dumps({'type': 'auth', 'access_token': AUTH_TOKEN}))
 
 '''
 Definition Generators
 '''
def init_socket_conn():
    try:
        websocket.enableTrace(False)
        global ws
        ws = websocket.WebSocketApp(
            "ws://localhost:8123/api/websocket", 
            on_open=on_open,
            on_error=on_error,
            on_close=on_close,
            on_message=on_message)
        
        ws.run_forever()
    except:
        print("Error while attempting to establish websocket....")


def roku_change_source(id_stamp, source):
    id_stamp[0] = id_stamp[0] + 1
    return json.dumps({
            "type":"call_service",
            "domain":"media_player",
            "service":"select_source",
            "service_data":{
                "entity_id":"media_player.48_tcl_roku_tv",
                "source": source
            },
            "id":str(id_stamp[0])
        })

def roku_remote_nav(id_stamp, action):
    id_stamp[0] = id_stamp[0] + 1
    return json.dumps({
            "type":"call_service",
            "domain":"remote",
            "service":"send_command",
            "service_data":{
                "entity_id":"remote.48_tcl_roku_tv",
                "command": action
            },
            "target": {
                "entity_id": "remote.48_tcl_roku_tv"
            },
            "id":str(id_stamp[0])
        })

def hue_command_on_generator(
    id_stamp,
    name,
    action):
    
    id_stamp[0] = id_stamp[0] + 1
    return json.dumps({
                "id": str(id_stamp[0]),
                "type": "call_service",
                "domain": "light",
                "service": action,
                "service_data": {
                    "color_name": "beige",
                    "brightness": "101"
                },
                "target": {
                    "entity_id": name
                }
            })
def hue_command_ramp_generator(
    id_stamp,
    name,
    brightness,
    action):
    
    id_stamp[0] = id_stamp[0] + 1
    return json.dumps({
                "id": str(id_stamp[0]),
                "type": "call_service",
                "domain": "light",
                "service": action,
                "service_data": {
                    "color_name": "beige",
                    "brightness": str(brightness[0])
                },
                "target": {
                    "entity_id": name
                }
            })

def hue_command_color_transition_generator(
    id_stamp,
    name,
    brightness,
    color,
    action):
    
    id_stamp[0] = id_stamp[0] + 1
    return json.dumps({
                "id": str(id_stamp[0]),
                "type": "call_service",
                "domain": "light",
                "service": action,
                "service_data": {
                    "color_name": color,
                    "brightness": str(brightness[0])
                },
                "target": {
                    "entity_id": name
                }
            })

def hue_command_off_generator(id_stamp, name, action):
    id_stamp[0] = id_stamp[0] + 1
    return json.dumps({
                "id": str(id_stamp[0]),
                "type": "call_service",
                "domain": "light",
                "service": action,
                "target": {
                    "entity_id": name
                }
            })

'''
Controllers
'''
async def tv_change_source(future, source):
    ws.send(roku_change_source(id_stamp, source))
    future.set_result(True)

async def tv_navigate(future, commands):
    ws.send(roku_remote_nav(id_stamp, commands))
    future.set_result(True)

async def fan_change_color(future, brightness, color):
    ws.send(hue_command_color_transition_generator(id_stamp, "light.hue_color_candle_1", brightness, color, "turn_on"))
    ws.send(hue_command_color_transition_generator(id_stamp, "light.hue_color_candle_2", brightness, color, "turn_on"))
    future.set_result(color)

async def fan_ramp_up_all(future, all_on):
    BRIGHTNESS[0] = BRIGHTNESS[0] + 10
    ws.send(hue_command_ramp_generator(id_stamp, "light.hue_color_candle_1", BRIGHTNESS, "turn_on"))
    ws.send(hue_command_ramp_generator(id_stamp, "light.hue_color_candle_2", BRIGHTNESS, "turn_on"))
    ws.send(hue_command_ramp_generator(id_stamp, "light.hue_ambiance_candle_1", BRIGHTNESS, "turn_on"))
    all_on[0] = True
    future.set_result(True)

async def fan_ramp_down_all(future, all_on):
    BRIGHTNESS[0] = BRIGHTNESS[0] - 10
    ws.send(hue_command_ramp_generator(id_stamp, "light.hue_color_candle_1", BRIGHTNESS, "turn_on"))
    ws.send(hue_command_ramp_generator(id_stamp, "light.hue_color_candle_2", BRIGHTNESS, "turn_on"))
    ws.send(hue_command_ramp_generator(id_stamp, "light.hue_ambiance_candle_1", BRIGHTNESS, "turn_on"))
    all_on[0] = True
    future.set_result(True)

async def fan_all_on(future, all_on):
    ws.send(hue_command_off_generator(id_stamp, "light.hue_color_candle_1", "turn_on"))
    ws.send(hue_command_off_generator(id_stamp, "light.hue_color_candle_2", "turn_on"))
    ws.send(hue_command_off_generator(id_stamp, "light.hue_ambiance_candle_1", "turn_on"))
    all_on[0] = False
    future.set_result(True)

async def fan_all_off(future, all_on):
    ws.send(hue_command_off_generator(id_stamp, "light.hue_color_candle_1", "turn_off"))
    ws.send(hue_command_off_generator(id_stamp, "light.hue_color_candle_2", "turn_off"))
    ws.send(hue_command_off_generator(id_stamp, "light.hue_ambiance_candle_1", "turn_off"))
    all_on[0] = True
    future.set_result(True)

async def fan_all_toggle(future, all_on):
    if (ALL_ON[0] == True):
        await fan_all_on(future, all_on)
    elif(ALL_ON[0] == False):
        await fan_all_off(future, all_on)

class DeviceAction:
    def __init__(self, action, params, cond):
        self.params = params
        self.action = action
        self.condition = cond

    def shouldExecute(self, ev, key):
        res = self.condition(key, ev)
        return res
    
    def action(self):
        return self.action
    
    def params(self):
        return self.params

class DeviceListener:

    def __init__(self, key_mappings, path):
        self.key_mappings = key_mappings
        self.path = path
        self.device = None
    
    def load(self):
        try:
            self.device = InputDevice(self.path)

        except:
            print("Problem creating input device")

    async def listen(self, TASK_LOOP):
        print("entering locking")
        for event in self.device.read_loop():
            if event.type == ecodes.EV_KEY:
                ev =  categorize(event)
                key = ecodes.KEY[event.code][4:]
                action = self.key_mappings[key]
                if action != None and action.shouldExecute(ev, key):
                    future = [TASK_LOOP.create_future()]
                    args = future + action.params
                    TASK_LOOP.create_task(action.action(*args))
                    await args[0]

def main():
    KEY_MAPPINGS = {
        'KPPLUS': DeviceAction(fan_ramp_up_all, [ALL_ON], lambda key, event: key == 'KPPLUS' and event.keystate == 1),
        'KPMINUS': DeviceAction(fan_ramp_down_all, [ALL_ON], lambda key, event: key == 'KPMINUS' and event.keystate == 1),
        'KPENTER': DeviceAction(fan_all_toggle, [ALL_ON], lambda key, event: key == 'KPENTER' and event.keystate== 1),
        'KP0': DeviceAction(fan_change_color, [BRIGHTNESS, "red"], lambda key, event: key == 'KP0' and event.keystate== 1),
        'KP6': DeviceAction(tv_navigate, ["right"], lambda key, event: key == 'KP6' and event.keystate == 1),
        'KP4': DeviceAction(tv_navigate, ["left"], lambda key, event: key == 'KP4' and event.keystate == 1),
        'KP8': DeviceAction(tv_navigate, ["up"], lambda key, event: key == 'KP8' and event.keystate == 1),
        'KP2': DeviceAction(tv_navigate, ["down"], lambda key, event: key == 'KP2' and event.keystate == 1),
        'KP5': DeviceAction(tv_navigate, ["select"], lambda key, event: key == 'KP5' and event.keystate == 1),
        'KP9': DeviceAction(tv_navigate, ["back"], lambda key, event: key == 'KP9' and event.keystate == 1),
        'KP1': DeviceAction(tv_navigate, ["play"], lambda key, event: key == 'KP1' and event.keystate == 1),
        'KP3': DeviceAction(tv_navigate, ["volume_mute"], lambda key, event: key == 'KP3' and event.keystate == 1),
        'KP7': DeviceAction(tv_change_source, ["Spotify Music"], lambda key, event: key == 'KP7' and event.keystate == 1),
    }
    
    try:
        w = threading.Thread(target = init_socket_conn)
        w.daemon = True
        w.start()

        TASK_LOOP = asyncio.get_event_loop()

        dev = DeviceListener(KEY_MAPPINGS, DEV_PATH)
        dev.load()
        TASK_LOOP.run_until_complete(dev.listen(TASK_LOOP))
        TASK_LOOP.run_forever()
    except:
        print("Press Control to ")


if __name__ == "__main__":
    main()
