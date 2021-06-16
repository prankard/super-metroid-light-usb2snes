import py2snes
import asyncio
import datetime
from tuya_bulb_control import Bulb
import json
import colorsys
from random import randrange
from YeeBulb import YeeBulb
from TuyaBulb import TuyaBulb
import math
import os.path

def error(message):
    print("")
    print(message)
    print("")
    input("--- Press Enter Key to Exit ---")
    exit(-1)

if not os.path.isfile("config.json"):
    error("cannot find config.json")

with open("config.json") as json_data_file:
    config = json.load(json_data_file)

with open("colors.json") as json_data_file:
    colors_json = json.load(json_data_file)

# Extra rooms for detecting lights and colour change
fireflea_rooms = set()
fireflea_rooms.add('9C5E')
fireflea_rooms.add('A293')
fireflea_rooms.add('B6EE')

wreckedship_dim_brightness = 50
wreckedship_boss_room = 'CD13'
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
wreckedship_rooms.add(wreckedship_boss_room)

colors = colors_json['colors']
rooms = colors_json['rooms']

delay = 0
try:
    delay = float(config['DELAY'])
except:
    pass

#if config['DELAY'] != None:
#    delay = float(config['DELAY'])
commands_when_off = True
rgb_tint_brightness = False

if config['BULB_TYPE'] == 'yeelight':
    bulb = YeeBulb(config)
    commands_when_off = False
elif config['BULB_TYPE'] == 'tuya':
    bulb = TuyaBulb(config)
    rgb_tint_brightness = True
else:
    error("Bulb in config.json not supported")

current_on = True
current_color = '000000'
current_brightness = 100
current_room = "0000"
load_colors = True

def convert_add(memory):
    if memory >= 0x7E0000 and memory < 0x800000:
        return memory - 0x7E0000 + 0xF50000
    return memory

def set_bulb_color(colorString, brightness = 100, force_set = False):
    if colorString == None:
        return
    if brightness == None:
        return
    global current_brightness, current_color, bulb, current_on, commands_when_off, current_room
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
        print(current_room + " : " +  current_color + " : " + str(brightness) + "%")

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
    if devices == None or len(devices) == 0:
        error("No SD2Snes Device Found")
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
            elif roomNumberString == wreckedship_boss_room:
                if current_brightness < 100:
                    if not await isPhantoonAlive(snes):
                        set_bulb_color(current_color, 100)
            continue

        current_room = roomNumberString

        #print(bulb.current_color)

        #print(roomNumberString)
        
        if await checkBombTimerRunning(snes):
            set_bulb_color("FFD300", 100)
            continue

        colorString = getRoomColor(roomNumberString)

        if colorString == None:
            print("can't find color for room: " + roomNumberString)
        
        if load_colors:
            if delay != 0:
                await asyncio.sleep(delay)
            
            if isWreckshipRoom(roomNumberString):
                if await isPhantoonAlive(snes):
                    set_bulb_color(colorString, wreckedship_dim_brightness)
                    continue
            
            set_bulb_color(colorString)
            #print("changing color to " + colorName)
            #print(colorString)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())