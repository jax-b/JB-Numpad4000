import time
import board

# Pin Definition
btnup_pin = board.D5
btnconfirm_pin = board.D6
btndown_pin = board.D9
pixel_pin = board.D4

num_key_pix = 22

MENU_ACTIVE_TIME = 3
SCREEN_ACTIVE_TIME = 80
ENABLE_BT = False
ENABLE_BAT = False

# Display Setup
import displayio
from adafruit_display_text import label
from adafruit_display_shapes import circle, rect, triangle, roundrect, Line
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
ScreenActive = SCREEN_ACTIVE_TIME
ScreenState = True
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
board_pix[0] = 0xFF0000
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
    (0): {"hidkey":"00", "pixel": 21, "calc": "00"},
    (1): {"hidkey":Keycode.KEYPAD_ZERO, "pixel": 20, "calc": 0},
    (3): {"hidkey":Keycode.KEYPAD_PERIOD, "pixel": 19, "calc": "."},
    (4): {"hidkey":Keycode.KEYPAD_ENTER, "pixel": 18, "calc": "="},

    (5): {"hidkey":"code", "pixel": 17, "calc": "cp"},
    (6): {"hidkey":Keycode.KEYPAD_ONE, "pixel": 16, "calc": 1},
    (7): {"hidkey":Keycode.KEYPAD_TWO, "pixel": 15, "calc": 2},
    (8): {"hidkey":Keycode.KEYPAD_THREE, "pixel": 14, "calc": 3},

    (10): {"hidkey":Keycode.PAGE_UP, "pixel": 9, "calc": "nxt"},
    (11): {"hidkey":Keycode.KEYPAD_SEVEN, "pixel": 8, "calc": 7},
    (12): {"hidkey":Keycode.KEYPAD_EIGHT, "pixel": 7, "calc": 8},
    (13): {"hidkey":Keycode.KEYPAD_NINE, "pixel": 6, "calc": 9},
    (14): {"hidkey":Keycode.KEYPAD_PLUS, "pixel": 5, "calc": "+"},

    (15): {"hidkey":Keycode.PAGE_DOWN, "pixel": 10, "calc": "bak"},
    (16): {"hidkey":Keycode.KEYPAD_FOUR, "pixel": 11, "calc": 4},
    (17): {"hidkey":Keycode.KEYPAD_FIVE, "pixel": 12, "calc": 5},
    (18): {"hidkey":Keycode.KEYPAD_SIX, "pixel": 13, "calc": 6},

    (20): {"hidkey":Keycode.KEYPAD_NUMLOCK, "pixel": 0, "calc": "nl"},
    (21): {"hidkey":Keycode.BACKSPACE, "pixel": 1, "calc": "del"},
    (22): {"hidkey":Keycode.FORWARD_SLASH, "pixel": 2, "calc": "/"},
    (23): {"hidkey":Keycode.KEYPAD_ASTERISK, "pixel": 3, "calc": "X"},
    (24): {"hidkey":Keycode.KEYPAD_MINUS, "pixel": 4, "calc": "-"}
}

## Menu Setup
MainMenu = [
    "Exit",
    "Calculator",    
    "LED Effects"
]
if ENABLE_BT:
    MainMenu.append("-Bluetooth-")
    global BluetoothMenu
    BluetoothMenu = (
        "Exit",
        "Connect",
        "Pair",
        "Clear Pairings"
    )
LEDEffectsMenu = (
    "Exit",
    "Rainbow Puke"
)


MenuIndex = 0
MenuActive = 0
CurrentMenu = MainMenu
CurrentMenuName = "MainMenu"

MenuGroup = displayio.Group()
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
CalculatorPos1 = "__"
CalculatorSymbol = '?'
CalculatorPos2 = "__"
CalculatorAns = "__"
CalculatorCurrent = 1
CalculatorExitTextRect = roundrect.RoundRect(x=0,y=5,height=54,width=8,r=3,fill=0xFFFFFF)
CalculatorExitTextRectFill = rect.Rect(x=0,y=5,height=54,width=2, fill=0xFFFFFF)
CalculatorExitText = label.Label(font=terminalio.FONT,color=0x0,x=1,y=17,fill=0xFFFFFF,text="E\nx\ni\nt",line_spacing=0.7)
CalculatorCalculationText = label.Label(font=terminalio.FONT,color=0xFFFFFF,x=12,y=15,fill=0xFFFFFF,text=CalculatorPos1+" "+CalculatorSymbol+" "+CalculatorPos2,scale=2)
CalculatorResultText = label.Label(font=terminalio.FONT,color=0xFFFFFF,x=12,y=40,fill=0xFFFFFF,text=CalculatorAns,line_spacing=0.7, scale=2)
CalculatorPosition1IND = circle.Circle(x0=15,y0=1,r=1, fill=0xFFFFFF)
CalculatorPosition2IND = circle.Circle(x0=125,y0=1,r=1, fill=0x0)
CalculatorGroup.append(CalculatorExitTextRect)
CalculatorGroup.append(CalculatorExitTextRectFill)
CalculatorGroup.append(CalculatorExitText)
CalculatorGroup.append(CalculatorCalculationText)
CalculatorGroup.append(CalculatorResultText)
CalculatorGroup.append(CalculatorPosition1IND)
CalculatorGroup.append(CalculatorPosition2IND)


## BongoCat Setup
#https://github.com/christanaka/circuitpython-bongo
from bongo.bongo import Bongo
bongo = Bongo()
BongoGroup = displayio.Group()
bongo.x = 40
bongo.y = 20
BongoMenuTextRect = roundrect.RoundRect(x=0,y=5,height=54,width=8,r=3,fill=0xFFFFFF)
BongoMenuTextRectFill = rect.Rect(x=0,y=5,height=54,width=2, fill=0xFFFFFF)
BongoMenuText = label.Label(font=terminalio.FONT,color=0x0,x=1,y=17,fill=0xFFFFFF,text="M\ne\nn\nu",line_spacing=0.7)
BongoGroup.append(bongo.group)
BongoGroup.append(BongoMenuTextRect)
BongoGroup.append(BongoMenuTextRectFill)
BongoGroup.append(BongoMenuText)
import adafruit_imageload
if ENABLE_BT:
    bluetoothbmp, palette = adafruit_imageload.load(
            "bluetooth.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette
        )
    global BongoBluetooth
    BongoBluetooth = displayio.TileGrid(
            bluetoothbmp,
            pixel_shader=palette,
            width=1,
            x=122,
            y=53,
            height=1,
            tile_width=6,
            tile_height=11,
        )
    BongoGroup.append(BongoBluetooth)
if ENABLE_BAT:
    batbmp, palette = adafruit_imageload.load(
            "bat.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette
        )
    global BongoBat
    BongoBat = displayio.TileGrid(
            batbmp,
            pixel_shader=palette,
            width=1,
            height=1,
            x=114,
            y=0,
            tile_width=14,
            tile_height=12,
        )
    BongoGroup.append(BongoBat)



display.show(BongoGroup)

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

tlast =int(time.monotonic())
while True:
    btnup.update()
    btndown.update()
    btnconfirm.update()
    # Key Board Notification
    key_event = keys.events.get()
    if key_event:
        bongo.update(key_event)
        ScreenActive = SCREEN_ACTIVE_TIME
        mapval = keymap[key_event.key_number]
        if key_event.pressed:
            print(mapval)
            if CalculatorActive:
                if type(mapval["calc"]) == int:
                    if CalculatorCurrent == 1:
                        if CalculatorPos1 == "__":
                            CalculatorPos1 = ""
                        CalculatorPos1 += str(mapval["calc"])
                    else:
                        if CalculatorPos2 == "__":
                            CalculatorPos2 = ""
                        CalculatorPos2 += str(mapval["calc"])
                    if CalculatorAns != "__":
                            CalculatorAns = "__"
                elif type(mapval["calc"]) == str:
                    if mapval["calc"] in ("+","-","X","/"):
                        CalculatorSymbol = mapval["calc"]
                        CalculatorCurrent = 2
                    elif mapval["calc"] in (".","00"):
                        if CalculatorCurrent == 1:
                            if CalculatorPos1 == "__":
                                CalculatorPos1 = ""
                            CalculatorPos1 += str(mapval["calc"])
                        else:
                            if CalculatorPos2 == "__":
                                CalculatorPos2 = ""
                            CalculatorPos2 += str(mapval["calc"])
                        if CalculatorAns != "__":
                            CalculatorAns = "__"
                    elif mapval["calc"] == "nl":
                        if CalculatorCurrent == 1:
                            if CalculatorPos1 == "__":
                                CalculatorPos1 = ""
                            CalculatorPos1 +="-"
                        else:
                            if CalculatorPos2 == "__":
                                CalculatorPos2 = ""
                            CalculatorPos2 += "-"
                        if CalculatorAns != "__":
                            CalculatorAns = "__"
                    elif mapval["calc"] == "cp":
                        CalculatorPos1 = CalculatorAns
                        CalculatorAns = "__"
                        CalculatorCurrent = 2
                    elif mapval["calc"] == "nxt":
                        CalculatorCurrent = 2
                    elif mapval["calc"] == "bak":
                        CalculatorCurrent = 1
                    elif mapval["calc"] == "del":
                        if CalculatorCurrent == 1:
                            if CalculatorPos1 != "__":
                                CalculatorPos1 = CalculatorPos1[:-1]
                                if CalculatorPos1 == "":
                                    CalculatorPos1 = "__"
                        else:
                            if CalculatorPos2 != "__":
                                CalculatorPos2 = CalculatorPos2[:-1]
                                if CalculatorPos2 == "":
                                    CalculatorPos2 = "__"
                    elif mapval["calc"] == "=":
                        ans = 0.0
                        if CalculatorSymbol == "+":
                            ans = float(CalculatorPos1)+float(CalculatorPos2)
                        elif CalculatorSymbol == "-":
                            ans = float(CalculatorPos1)-float(CalculatorPos2)
                        elif CalculatorSymbol == "X":
                            ans = float(CalculatorPos1)*float(CalculatorPos2)
                        elif CalculatorSymbol == "/":
                            ans = float(CalculatorPos1)/float(CalculatorPos2)
                        if ans % 1 != 0:
                            CalculatorAns = str(ans)
                        else:
                            CalculatorAns = str(int(ans))

                        CalculatorPos1 = "__"
                        CalculatorPos2 = "__"
                        CalculatorSymbol = '?'
                        CalculatorCurrent = 1
                CalculatorCalculationText.text = CalculatorPos1+" "+CalculatorSymbol+" "+CalculatorPos2
                CalculatorResultText.text = CalculatorAns
                print(CalculatorPos1+" "+CalculatorSymbol+" "+CalculatorPos2)
            else:
                if type(mapval["hidkey"]) == str:
                    if mapval["hidkey"] ==  "00":
                        kbd.press(Keycode.KEYPAD_ZERO)
                        kbd.release(Keycode.KEYPAD_ZERO)
                        kbd.press(Keycode.KEYPAD_ZERO)
                        kbd.release(Keycode.KEYPAD_ZERO)
                elif type(mapval["hidkey"]) == int:
                    kbd.press(mapval["hidkey"])

            key_pix[mapval["pixel"]] = 0x0000FF
        elif key_event.released:
            if not CalculatorActive:
                if type(mapval["hidkey"]) == int:
                    kbd.release(mapval["hidkey"])
            key_pix[mapval["pixel"]] = 0x0
        key_pix.show()

    # Menu Code
    if ScreenActive > 0:
        if ScreenState == False:
            ScreenState = True
            display.wake()
        if MenuActive > 0:
            display.wake()
            refresh = False
            if btndown.fell:
                MenuIndex +=1
                if MenuIndex >= len(CurrentMenu):
                    MenuIndex = 0
                MenuActive = MENU_ACTIVE_TIME
                ScreenActive = SCREEN_ACTIVE_TIME
                RefreshMenu()
            if btnup.fell:
                MenuIndex -=1
                if MenuIndex < 0:
                    MenuIndex = len(CurrentMenu)-1
                MenuActive = MENU_ACTIVE_TIME
                ScreenActive = SCREEN_ACTIVE_TIME
                RefreshMenu()
            if btnconfirm.fell:
                MenuActive = MENU_ACTIVE_TIME
                ScreenActive = SCREEN_ACTIVE_TIME
                if CurrentMenu[MenuIndex] == "Exit": ## Go up to the Main Menu or turn off the menu
                    if CurrentMenuName != "MainMenu":
                        CurrentMenu = MainMenu
                        CurrentMenuName = "MainMenu"
                        RefreshMenu()
                    else:
                        MenuActive=0
                    MenuIndex=0
                elif CurrentMenu[MenuIndex] == MainMenu[1]: # if Calculator is selected Enter That Feature
                    ScreenActive = SCREEN_ACTIVE_TIME
                    MenuActive = 0
                    MenuIndex=0
                    CalculatorActive = True
                    display.show(CalculatorGroup)
                    RefreshMenu()
                elif ENABLE_BT and CurrentMenu[MenuIndex] == MainMenu[3]: # if Bluetooth is selected Enter That Menu
                    MenuActive = MENU_ACTIVE_TIME
                    ScreenActive = SCREEN_ACTIVE_TIME
                    MenuIndex=0
                    CurrentMenu = BluetoothMenu
                    CurrentMenuName = "BluetoothMenu"
                    RefreshMenu()
                elif CurrentMenu[MenuIndex] == MainMenu[2]: # if LED Effects is selected Enter That Menu
                    MenuActive = MENU_ACTIVE_TIME
                    ScreenActive = SCREEN_ACTIVE_TIME
                    MenuIndex=0
                    CurrentMenu = LEDEffectsMenu
                    CurrentMenuName = "LEDEffectsMenu"
                    RefreshMenu()
            if tlast-int(time.monotonic()):
                MenuActive -= 1
        elif CalculatorActive:
            if CalculatorCurrent == 1:
                CalculatorPosition1IND.fill =0xFFFFFF
                CalculatorPosition2IND.fill =0x0
            else:
                CalculatorPosition2IND.fill =0xFFFFFF
                CalculatorPosition1IND.fill =0x0
            if btnup.fell or btndown.fell or btnconfirm.fell: # Exit Calculator
                CalculatorActive = False
                ScreenActive = SCREEN_ACTIVE_TIME
                display.show(BongoGroup)
            
        else:
            display.show(BongoGroup)
            if btnup.fell or btndown.fell or btnconfirm.fell:
                MenuActive = MENU_ACTIVE_TIME
                ScreenActive = SCREEN_ACTIVE_TIME
                MenuIndex=0
                CurrentMenu = MainMenu
                CurrentMenuName = "MainMenu"
                RefreshMenu()
                display.show(MenuGroup)
        if tlast-int(time.monotonic()):
            ScreenActive -= 1
        tlast=int(time.monotonic())
    else:
        if ScreenState == True:
            ScreenState = False
            display.sleep()
        if btnup.fell or btndown.fell or btnconfirm.fell:
            ScreenActive = SCREEN_ACTIVE_TIME


# def color_chase(color, wait):
#     for i in range(num_key_pix):
#         key_pix[i] = color
#         time.sleep(wait)
#         key_pix.show()
#     time.sleep(0.5)


# def rainbow_cycle(wait, durration):
#     for j in range(durration):
#         for i in range(num_key_pix):
#             rc_index = (i * 256 // num_key_pix) + j
#             key_pix[i] = colorwheel(rc_index & 255)
#         key_pix.show()
#         time.sleep(wait)


# RED = (255, 0, 0)
# YELLOW = (255, 150, 0)
# GREEN = (0, 255, 0)
# CYAN = (0, 255, 255)
# BLUE = (0, 0, 255)
# PURPLE = (180, 0, 255)

# while True:
#     key_pix.fill(RED)
#     key_pix.show()
#     # Increase or decrease to change the speed of the solid color change.
#     time.sleep(1)
#     key_pix.fill(GREEN)
#     key_pix.show()
#     time.sleep(1)
#     key_pix.fill(BLUE)
#     key_pix.show()
#     time.sleep(1)

#     color_chase(RED, 0.1)  # Increase the number to slow down the color chase
#     color_chase(YELLOW, 0.1)
#     color_chase(GREEN, 0.1)
#     color_chase(CYAN, 0.1)
#     color_chase(BLUE, 0.1)
#     color_chase(PURPLE, 0.1)

#     rainbow_cycle(0,10000)  # Increase the number to slow down the rainbow
