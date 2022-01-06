import time
import board

# Pin Definition
btnup_pin = board.D5
btnconfirm_pin = board.D6
btndown_pin = board.D9
pixel_pin = board.D4

num_key_pix = 22

BLUE = 0x0000FF
WHITE = 0xFFFFFF
RED = 0xFF0000
MENU_ACTIVE_TIME = 3000

# Display Setup
import displayio
from adafruit_display_text import label
from adafruit_display_shapes import circle, rect, triangle, roundrect
import adafruit_displayio_sh1107
import terminalio
displayio.release_displays()
i2c = board.I2C()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
# SH1107 is vertically oriented 64x128
DSP_WIDTH = 128
DSP_HEIGHT = 64
display = adafruit_displayio_sh1107.SH1107(
    display_bus, width=DSP_WIDTH, height=DSP_HEIGHT, rotation=0
)
# Display Buttons
from digitalio import DigitalInOut, Direction, Pull
from adafruit_debouncer import Debouncer
btnupdio = DigitalInOut(btnup_pin)
btnupdio.direction = Direction.INPUT
btnupdio.pull = Pull.UP
btnup = Debouncer(btnupdio)
btnconfirmdio = DigitalInOut(btnconfirm_pin)
btnconfirmdio.direction = Direction.INPUT
btnconfirmdio.pull = Pull.UP
btnconfirm = Debouncer(btnconfirmdio)
btndowndio = DigitalInOut(btndown_pin)
btndowndio.direction = Direction.INPUT
btndowndio.pull = Pull.UP
btndown = Debouncer(btndowndio)

# Neopixel Setup
# from rainbowio import colorwheel
import neopixel
board_pix = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.1)
board_pix[0] = BLUE
key_pix = neopixel.NeoPixel(pixel_pin, num_key_pix, brightness=0.3, auto_write=False)
# Clear LED
board_pix.show()
key_pix.show()



# Keyboard Setup
import keypad
keys = keypad.KeyMatrix(
    row_pins=(board.A0, board.A1, board.A2, board.A3, board.D24),
    column_pins=(board.D13, board.D12, board.D11, board.D10, board.D25),
    columns_to_anodes=False,
    max_events=100
)
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
kbd = Keyboard(usb_hid.devices)

# create a keycode dictionary including modifier state and keycodes
keymap = {
            (0): {"key":"00", "pixel": 21},
            (1): {"key":(0, Keycode.KEYPAD_ZERO), "pixel": 20},
            (3): {"key":(0, Keycode.KEYPAD_PERIOD), "pixel": 19},
            (4): {"key":(0, Keycode.KEYPAD_EQUALS), "pixel": 18},

            (5): {"key":"code", "pixel": 17},
            (6): {"key":(0, Keycode.KEYPAD_ONE), "pixel": 16},
            (7): {"key":(0, Keycode.KEYPAD_TWO), "pixel": 15},
            (8): {"key":(0, Keycode.KEYPAD_THREE), "pixel": 14},

            (10): {"key":(0, Keycode.PAGE_UP), "pixel": 9},
            (11): {"key":(0, Keycode.KEYPAD_SEVEN), "pixel": 8},
            (12): {"key":(0, Keycode.KEYPAD_EIGHT), "pixel": 7},
            (13): {"key":(0, Keycode.KEYPAD_NINE), "pixel": 6},
            (14): {"key":(0, Keycode.KEYPAD_PLUS), "pixel": 5},

            (15): {"key":(0, Keycode.PAGE_DOWN), "pixel": 10},
            (16): {"key":(0, Keycode.KEYPAD_FOUR), "pixel": 11},
            (17): {"key":(0, Keycode.KEYPAD_FIVE), "pixel": 12},
            (18): {"key":(0, Keycode.KEYPAD_SIX), "pixel": 13},
            (19): {"key":(0, Keycode.KEYPAD_PLUS), "pixel": 5},

            (20): {"key":(0, Keycode.KEYPAD_NUMLOCK), "pixel": 0},
            (21): {"key":(0, Keycode.BACKSPACE), "pixel": 1},
            (22): {"key":(0, Keycode.FORWARD_SLASH), "pixel": 2},
            (23): {"key":(0, Keycode.KEYPAD_ASTERISK), "pixel": 3},
            (24): {"key":(0, Keycode.KEYPAD_MINUS), "pixel": 4},
}

## Menu Setup
MainMenu = (
    "Exit",
    "Calculator",
    "-Bluetooth-"
)
BluetoothMenu = (
    "Exit",
    "Connect",
    "Pair",
    "Clear Pairings"
)

MenuIndex = 0
MenuActive = MENU_ACTIVE_TIME
CurrentMenu = MainMenu

MenuGroup = displayio.Group()
display.show(MenuGroup)
MenuUpArrow = triangle.Triangle(x0=0, y0=16, x1=4, y1=9, x2=8, y2=16, fill=0xFFFFFF)
MenuCircle = circle.Circle(x0=4,y0=31,r=4, fill=0xFFFFFF)
MenuDownArrow = triangle.Triangle(x0=0, y0=47, x1=4, y1=54, x2=8, y2=47, fill=0xFFFFFF)
MenuUpNextText = label.Label(font=terminalio.FONT, color=0xFFFFFF, text="", x=17, y=12)
MenuSelectedTextRect = rect.Rect(x=15, y=23, width=110, height=16, fill=0xFFFFFF)
MenuSelectedText = label.Label(font=terminalio.FONT, color=0x0, text="", x=17, y=31)
MenuDownNextText = label.Label(font=terminalio.FONT, color=0xFFFFFF, text="", x=17, y=48) 
MenuGroup.append(MenuUpArrow)
MenuGroup.append(MenuDownArrow)
MenuGroup.append(MenuCircle)
MenuGroup.append(MenuUpNextText)
MenuGroup.append(MenuSelectedTextRect)
MenuGroup.append(MenuSelectedText)
MenuGroup.append(MenuDownNextText)

MenuSelectedText.text = CurrentMenu[MenuIndex]
if MenuIndex+1 >= len(CurrentMenu): 
    MenuUpNextText.text = CurrentMenu[0]
else:
    MenuUpNextText.text = CurrentMenu[MenuIndex+1]
if MenuIndex-1 < 0:
    MenuDownNextText.text = CurrentMenu[len(CurrentMenu)-1]
else:
    MenuDownNextText.text = CurrentMenu[MenuIndex-1]

## Calculator Setup
CalculatorActive = False
CalculatorGroup = displayio.Group()
CalculatorExitTextRect = roundrect.RoundRect(x=0,y=5,height=54,width=8,r=3,fill=0xFFFFFF)
CalculatorExitTextRectFill = rect.Rect(x=0,y=5,height=54,width=2, fill=0xFFFFFF)
CalculatorExitText = label.Label(font=terminalio.FONT,color=0x0,x=1,y=17,fill=0xFFFFFF,text="E\nx\ni\nt",line_spacing=0.7)
CalculatorCalculationText = label.Label(font=terminalio.FONT,color=0xFFFFFF,x=12,y=15,fill=0xFFFFFF,text="__ ? __ = ",scale=2)
CalculatorResultText = label.Label(font=terminalio.FONT,color=0xFFFFFF,x=12,y=40,fill=0xFFFFFF,text="____",line_spacing=0.7, scale=2)
CalculatorGroup.append(CalculatorExitTextRect)
CalculatorGroup.append(CalculatorExitTextRectFill)
CalculatorGroup.append(CalculatorExitText)
CalculatorGroup.append(CalculatorCalculationText)
CalculatorGroup.append(CalculatorResultText)

## BongoCat Setup
BongoGroup = displayio.Group()

def RefreshMenu():
    MenuSelectedText.text = CurrentMenu[MenuIndex]
    if MenuIndex+1 >= len(CurrentMenu): 
        MenuUpNextText.text = CurrentMenu[0]
    else:
        MenuUpNextText.text = CurrentMenu[MenuIndex+1]
    if MenuIndex-1 < 0:
        MenuDownNextText.text = CurrentMenu[len(CurrentMenu)-1]
    else:
        MenuDownNextText.text = CurrentMenu[MenuIndex-1]

tlast = time.monotonic()
while True:
    btnup.update()
    btndown.update()
    btnconfirm.update()
    # Key Board Notification
    key_event = keys.events.get()
    if key_event:
        if key_event.pressed:
            mapval = keymap[key_event.key_number]
            key_pix[mapval["pixel"]] = BLUE
        else:
            key_pix[mapval["pixel"]] = 0x0
        key_pix.show()

    # Menu Code
    if MenuActive > 0:
        refresh = False
        if btndown.fell:
            MenuIndex +=1
            if MenuIndex >= len(CurrentMenu):
                MenuIndex = 0
            MenuActive = MENU_ACTIVE_TIME
            RefreshMenu()
        if btnup.fell:
            MenuIndex -=1
            if MenuIndex < 0:
                MenuIndex = len(CurrentMenu)-1
            MenuActive = MENU_ACTIVE_TIME
            RefreshMenu()
        if btnconfirm.fell:
            MenuActive = MENU_ACTIVE_TIME
            if CurrentMenu[MenuIndex] == "Exit": ## Go up to the Main Menu or turn off the menu
                if CurrentMenu != MainMenu:
                    MenuActive = MENU_ACTIVE_TIME
                    CurrentMenu = MainMenu
                    RefreshMenu()
                else:
                    MenuActive=0
                MenuIndex=0
            elif CurrentMenu[MenuIndex] == MainMenu[1]: # if Calculator is selected Enter That Feature
                MenuActive = 0
                CalculatorActive = True
                display.show(CalculatorGroup)
            elif CurrentMenu[MenuIndex] == MainMenu[2]: # if Bluetooth is selected Enter That Menu
                MenuActive = MENU_ACTIVE_TIME
                MenuIndex=0
                CurrentMenu = BluetoothMenu
                RefreshMenu()
        if tlast-time.monotonic():
            MenuActive -= 1
        tlast=time.monotonic()
    elif CalculatorActive:
        if btnup.fell or btndown.fell or btnconfirm.fell:
            CalculatorActive = False
            MenuActive = 0
            MenuIndex = 0
            RefreshMenu()
            display.show(BongoGroup)
    else:
        display.show(BongoGroup)
        if btnup.fell or btndown.fell or btnconfirm.fell:
            MenuActive = MENU_ACTIVE_TIME
            MenuIndex=0
            CurrentMenu = MainMenu
            RefreshMenu()
            display.show(MenuGroup)
