#!/usr/bin/env python

import asyncio
import sys
import websockets
from pynput.mouse import Button, Controller
from threading import Thread, Event
from math import *

# TMP
up_max = 40
up_min = -5

width_max = 130
width_min = 70

# Screen
screenWidth, screenHeight = 1920, 1080
mouse = Controller()

# -------------------------
# Maths


def clamp(num, min_value, max_value):
    """ Clamp a value between two values """
    return max(min(num, max_value), min_value)


def normalize(value, minval, maxval):
    """ Normalize a value between 0 and 1 """
    return (value - minval) / (maxval - minval)

# -------------------------
# Debugging


def parse_data_raw(message):
    out = {}
    message = message.split(";")
    out["absolute"] = int(message[0])
    out["alpha"] = float(message[1])
    out["beta"] = float(message[2])
    out["omega"] = float(message[3])
    out["calibration"] = int(message[4])

    return out


def format_data_debug(message):
    """
        Print raw data from the client
    """
    print("Absolute: ", message["absolute"])
    print("Alpha: ", message["alpha"])
    print("Beta: ", message["beta"])
    print("Omega: ", message["omega"])
    print("Calibration: ", message["calibration"])


def calibration(message_parsed):
    if message_parsed["calibration"] == 1:
        format_data_debug(message_parsed)
        up_max = message_parsed["alpha"]
        width_min = message_parsed["beta"]
        print("TOP: ", up_max, width_min)
    elif message_parsed["calibration"] == 2:
        format_data_debug(message_parsed)
        up_min = message_parsed["alpha"]
        width_max = message_parsed["beta"]
        print("DOWN: ", up_min, width_max)

def fix_offset(v_min, v_max):

    if v_min < v_max:
        return v_min, v_max

    offset = v_max
    v_max -= offset
    v_min += offset

    print("CORRECTED: ", v_min, v_max)
    return v_min, v_max

def move_mouse(parsed_data):

    up_min_f, up_max_f = fix_offset(up_min, up_max)
    width_min_f, width_max_f = fix_offset(up_min, up_max)

    new_height = (
        1 - normalize(parsed_data["beta"], up_min_f, up_max_f)) * screenHeight
    new_width = (
        1 - normalize(parsed_data["alpha"], width_min_f, width_max_f)) * screenWidth
    mouse.position = (clamp(new_width, 0, screenWidth - 1),
                      clamp(new_height, 0, screenHeight - 1))


async def main_loop_async(websocket, path):
    async for message in websocket:
        data = parse_data_raw(message)
        calibration(data)
        format_data_debug(data)
        move_mouse(data)


def websocket_server(server_ip, server_port):
    start_server = websockets.serve(main_loop_async, server_ip, server_port)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


# Get arguments
if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage: <ip> <port>")
        exit(1)

    server_ip = sys.argv[1]

    try:
        server_port = int(sys.argv[2])
    except Exception:
        print("Invalid port")
        exit(2)

    print("Stating server on " + server_ip + ":" + str(server_port) + "...")

    websocket_server(server_ip, server_port)
