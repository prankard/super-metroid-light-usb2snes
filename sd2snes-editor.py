DEBUG = True

import py2snes
import asyncio
import datetime
from tuya_bulb_control import Bulb
import json
import colorsys
from pynput.keyboard import Key, Listener
from random import randrange
from YeeBulb import YeeBulb
from TuyaBulb import TuyaBulb
import math

with open("config.json") as json_data_file:
    config = json.load(json_data_file)

with open("colors.json") as json_data_file:
    colors_json = json.load(json_data_file)

if DEBUG:
    with open("colors.json") as json_data_file:
        colors_json_debug = json.load(json_data_file)

fireflea_rooms = set()
fireflea_rooms.add('9C5E')
fireflea_rooms.add('A293')
fireflea_rooms.add('B6EE')

wreckedship_rooms = set()
wreckedship_rooms.add('CC6F')
wreckedship_rooms.add('CAF6')
wreckedship_rooms.add('CDA8')
wreckedship_rooms.add('CDF1')
wreckedship_rooms.add('CD5C')
wreckedship_rooms.add('CB8B')
wreckedship_rooms.add('CBD5')
wreckedship_rooms.add('CC27')
wreckedship_rooms.add('CA08')
wreckedship_rooms.add('CA52')

colors = colors_json['colors']
rooms = colors_json['rooms']

CLIENT_ID = config['CLIENT_ID']
SECRET_KEY = config['SECRET_KEY']
DEVICE_ID = config['DEVICE_ID']
REGION_KEY = config['REGION_KEY']
commands_when_off = True
rgb_tint_brightness = False

if config['BULB_TYPE'] == 'yeelight':
    bulb = YeeBulb(config)
    commands_when_off = False
elif config['BULB_TYPE'] == 'tuya':
    bulb = TuyaBulb(config)
    rgb_tint_brightness = True
else:
    print("Bulb in config.json not supported")
    exit(-1)

#bulb = Bulb(
#    client_id=CLIENT_ID,
#    secret_key=SECRET_KEY,
#    device_id=DEVICE_ID,
#    region_key=REGION_KEY
#)
current_on = True
current_color = '000000'
current_brightness = 100
current_room = "0000"
load_colors = True


def get_bulb_color():
    print("no longer suppported on the AbstactBulb types")
    pass
    #print(bulb.state())
    hsv = json.loads(bulb.current_value('colour_data_v2'))
    #print(hsv)
    h = float(hsv['h']) / 360
    s = float(hsv['s']) / 1000
    v = float(hsv['v']) / 1000
    #print(h, s, v)
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    rgb = int(r * 255) << 16 | int(g * 255) << 8 | int(b * 255) 
    #print(r, g, b)
    #print(rgb)
    colorHexString = hex(rgb)[2:].zfill(6)
    #print(colorHexString)
    return colorHexString
    #print(bulb.current_value('colour_data_v2'))
    #print(bulb.current_color)

def get_bulb_status():
    try:
        global bulb_on
        val = bulb.current_value("switch_led")
        if val is False:
            bulb_on = False
            print("it was false")
        print(val)
    except:
        print("Error Getting Value")

def convert_add(memory):
    if memory >= 0x7E0000 and memory < 0x800000:
        return memory - 0x7E0000 + 0xF50000
    return memory

def set_bulb_color(colorString, brightness = 100, force_set = False):
    if colorString == None:
        return
    if brightness == None:
        return
    global current_brightness, current_color, bulb, current_on, commands_when_off
    if force_set or current_color != colorString or current_brightness != brightness:
        value = int(colorString, 16)
        R = (value >> 16) & 0xFF
        G = (value >> 8) & 0xFF
        B = value & 0xFF
        #print("changing color")
        #print(colorName)
        #print(colorValue)
        current_color = colorString
        brightness = round(math.tan (brightness/72.8)*20)
        current_brightness = brightness
        if rgb_tint_brightness:
            brightness_percent = brightness * 0.01
        else:
            brightness_percent = 1 
        print(current_color + " : " + str(brightness) + "%")
        if brightness == 0:
            if current_on:
                bulb.set_power(False)
                current_on = False
        else:
            if commands_when_off:
                bulb.set_rgb(R * brightness_percent, G * brightness_percent, B * brightness_percent)
                bulb.set_brightness(brightness)
                #bulb.set_colour_v2(rgb=(R * brightness_percent, G * brightness_percent, B * brightness_percent))

            if current_on == False:
                bulb.set_power(True)
                current_on = True
            
            if not commands_when_off:
                bulb.set_rgb(R * brightness_percent, G * brightness_percent, B * brightness_percent)
                bulb.set_brightness(brightness)

def isFirefleaRoom(roomNumberString):
    return roomNumberString in fireflea_rooms

def isWreckshipRoom(roomNumberString):
    return roomNumberString in wreckedship_rooms

def getRoomColor(roomNumberString):
    try:
        if DEBUG:
            colorName = colors_json_debug['rooms'][roomNumberString]
            colorString = colors_json_debug['colors'][colorName]
        else:
            colorName = rooms[roomNumberString]
            colorString = colors[colorName]
            
#        print(colorName)
#        print(colorString)
        return colorString
        
    except:
        return None

async def checkBombTimerRunning(snes):
    bombTimerRunning = await snes.GetAddress(convert_add(0x7E0943), 1)
    return bombTimerRunning[0] > 0

async def isPhantoonAlive(snes):
    bosses = await snes.GetAddress(convert_add(0x7ED82B), 1)
    return bosses[0] & 0x1 == 0

async def main():
    global current_color, bulb_on, current_room, load_colors
    snes = py2snes.snes()
    await snes.connect()
    devices = await snes.DeviceList()
    await snes.Attach(devices[0])
    print(await snes.Info())

    while True:
        await asyncio.sleep(1)
        roomNumberBytes = await snes.GetAddress(convert_add(0x7E079B), 2)
        if roomNumberBytes == None:
            raise Exception("Can't get memory address from snes. Lost Connection")
        
        roomNumber = roomNumberBytes[0] + roomNumberBytes[1] << 16
        roomNumber = roomNumberBytes[1] << 8 | roomNumberBytes[0]
        roomNumberString = str(hex(roomNumber).upper()[2:])

        if roomNumber == 0xDD58 or roomNumber == 0xE0B5: 
            if await checkBombTimerRunning(snes):
                set_bulb_color("FFD300", 100)
                #print("setting escape color")
                continue

        if current_room == roomNumberString:
            if isFirefleaRoom(roomNumberString):
                brightnessBaseIndex = await snes.GetAddress(convert_add(0x7E177E), 1)
                brightnessMultiplier = (10 - brightnessBaseIndex[0]) * 10

                if brightnessMultiplier != current_brightness:
                    set_bulb_color(current_color, brightnessMultiplier)

            continue

        current_room = roomNumberString

        #print(bulb.current_color)

        #print(roomNumberString)
        
        if await checkBombTimerRunning(snes):
            set_bulb_color("FFD300", 100)
            continue

        colorString = getRoomColor(roomNumberString)

        if colorString == None:
            print("can't find current room color")
        
        if load_colors:
            if isWreckshipRoom(roomNumberString):
                if await isPhantoonAlive(snes):
                    set_bulb_color(colorString, 30)
                    continue
            
            set_bulb_color(colorString)
            #print("changing color to " + colorName)
            #print(colorString)


def add_color_json(color):
    global colors_json_debug
    for key in colors_json_debug['colors']:
        val = colors_json_debug['colors'][key]
        if val == color:
            return key

    newName = 'c' + str(randrange(100,999))
    colors_json_debug['colors'][newName] = color
    return newName

def add_room(roomNumberString, color):
    global colors_json_debug
    colors_json_debug['rooms'][roomNumberString] = color

def save_json():
    with open('colors-debug.json', 'w') as outfile:
        json.dump(colors_json_debug, outfile)

def on_press(key):
    #print(key)
    global current_room, load_colors, current_color, key_listener, key_room_listener
    if key == Key.enter:
        # Save Color to Room
        print("Saved color to room: " + current_room)
        color = get_bulb_color()
        colorName = add_color_json(color)
        add_room(current_room, colorName)
        save_json()
        #colors_json_debug['colors']['color_']
    if 'char' in dir(key):
        char = key.char
        if char == 'r':
            # Reload
            print("Reload color from current room: " + current_room)
            try:
                roomColor = colors_json_debug['rooms'][current_room]
                color = colors_json_debug['colors'][roomColor]
                set_bulb_color(color, 100, True)
            except:
                print("no room color found")
        elif char == 'd':
            # Disable color load on new room
            load_colors = False
            current_color = '000000'
            print("Disabled color loading when entered new room")
        elif char == 'e':
            load_colors = True
            # Enable color load on new room
            print("Enabled color loading when entered new room")
        elif char == 'l':
            # Load color from specific room
            print("Enter 4 hex room number")
            startKeyListener(True)
        elif char == 'i':
            # Load color from specific room
            print("Info:")
            print("Current Bulb Color: " + get_bulb_color())
            print("Current Room: " + current_room)
            try:
                roomColor = colors_json_debug['rooms'][current_room]
                color = colors_json_debug['colors'][roomColor]
                print("Room Color: " + roomColor + " - " + color)
            except:
                print("No color found for the room")

def startKeyListener(forRoom = False):
    
    global key_listener, key_room_listener
    
    if key_listener != None:
        key_listener.stop()
    if key_room_listener != None:
        key_room_listener.stop()

    if forRoom:
        key_room_listener = Listener(on_press=on_press_hex_room)
        key_room_listener.start()
    else:
        key_listener = Listener(on_press=on_press)
        key_listener.start()

def on_press_hex_room(key):
    global hex_room_input, key_listener, key_room_listener
    if key == Key.esc:
        print("cancelled room loading")
        startKeyListener(False)
        hex_room_input = ""
    elif key == Key.enter:
        room_input = hex_room_input.upper()
        print("You entered " + room_input)
        hex_room_input = ""
        startKeyListener(False)
        try:
            colorName = colors_json_debug['rooms'][room_input]
            color = colors_json_debug['colors'][colorName]
            set_bulb_color(color, 100, True)
        except:
            print("Room not found, or color not found in room")
    elif key == Key.backspace:
        hex_room_input = hex_room_input[:-1]
        print(hex_room_input)
    elif 'char' in dir(key):
        char = key.char
        hex_room_input += char
        print(hex_room_input)


if DEBUG:
    hex_room_input = ""
    key_listener= key_room_listener = None
    startKeyListener(False)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())