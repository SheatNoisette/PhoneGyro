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

# Message queue used
message_queue = []
MAX_MESSAGES_WAITING = 30


# -------------------------
# Message queue

def message_queue_push(queue, element):
    if len(message_queue) == MAX_MESSAGES_WAITING:
        queue.pop()
    queue.append(element)


def message_queue_empty(queue):
    return len(queue) == 0
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

    return out


def format_data_debug(message):
    """
        Print raw data from the client
    """
    content = parse_data_raw(message)

    print("Absolute: ", content["absolute"])
    print("Alpha: ", content["alpha"])
    print("Beta: ", content["beta"])
    print("Omega: ", content["omega"])



def move_mouse(parsed_data):
    new_height = (
        1 - normalize(parsed_data["beta"], up_min, up_max)) * screenHeight
    new_width = (
        1 - normalize(parsed_data["alpha"], width_min, width_max)) * screenWidth
    mouse.position = (clamp(new_width, 0, screenWidth - 1),
                      clamp(new_height, 0, screenHeight - 1))


def main_loop():
    while True:
        while not message_queue_empty():
            move_mouse(parse_data_raw(message_queue.pop()))

async def main_loop_async(websocket, path):
    async for message in websocket:
        format_data_debug(message)
        # message_queue.append(message)
        move_mouse(parse_data_raw(message))

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

