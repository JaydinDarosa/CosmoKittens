from m5stack import *
from m5ui import *
from uiflow import *
from numbers import Number
import random
import imu
import urequests
import time
import gc
import network
import machine
from esp32 import nvs_getstr, nvs_setstr, nvs_erase

CatX = None
Xmin = None
CatY = None
Xmax = None
Ymin = None
Ymax = None
tick = None

BASE_URL = "http://cosmo-kittens.club/"
API_BASE = BASE_URL + "api/"
SYNC_URL = API_BASE + "sync/?machine_id={machine_id}"
IMG_URL = API_BASE + "sprite/{machine_id}"


def random_string(n):
    random.seed(time.time())
    out = ""
    alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i in range(n):
        out += random.choice(alpha)
    return out

moods = ["crying", "sad", "normal", "happy", "super_happy"]

STATE = {
    "last_update": 0,
    "token": nvs_getstr("quazar:token"),
}

DATA = {
    "name": "",
    "appearance": "{}",
    "water": 0,
    "food": 0,
    "health": 0,
    "steps": 0,
    "mood": 0,
    "power": power.getBatteryLevel(),
}

dials = {
    "health": {"X": 3, "Y": 10, "icon": M5Img(24, 49, "res/Heart.png", False)},
    "water": {"X": 3, "Y": 92, "icon": M5Img(25, 131, "res/Water.png", False)},
    "food": {"X": 3, "Y": 174, "icon": M5Img(22, 214, "res/Food.png", False)},
    "power": {"X": 261, "Y": 12, "icon": M5Img(284, 51, "res/Power.png", False)},
    "steps": {"X": 260, "Y": 96, "icon": M5Img(282, 134, "res/Shoe.png", False)},
}


class FrameBuffer:
    def __init__(self, x, y, width, height):
        lcd.sprite_create(width, height, lcd.SPRITE_8BIT)
        self.x = x
        self.y = y

    def __enter__(self):
        lcd.sprite_select()

    def __exit__(self, *args):
        lcd.sprite_show(self.x, self.y)
        lcd.sprite_deselect()
        lcd.sprite_delete()


def cat_move():
    global CatX, Xmin, CatY, Xmax, Ymin, Ymax, tick
    CatX = (CatX if isinstance(CatX, Number) else 0) + random.randint(-5, 5)
    CatY = (CatY if isinstance(CatY, Number) else 0) + random.randint(-5, 5)
    if CatX < Xmin:
        CatX = Xmin
    if CatX > Xmax:
        CatX = Xmax
    if CatY < Ymin:
        CatY = Ymin
    if CatY > Ymax:
        CatY = Ymax
    with FrameBuffer(Xmin, Ymin, 185, 118):
        cat.setPosition(CatX - Xmin, CatY - Ymin)
        cropped.show()
        cat.show()


def sync_data(steps):
    # post request to SYNC_URL with `machine_token` and `steps`
    currentAppearance = DATA["appearance"]
    DATA["power"] = power.getBatteryLevel()

    if STATE["token"] is None:
        metal = M5Img(32, 24, "res/metal.png", True)
        token = random_string(8)
        M5TextBox(66, 58, "Token:".format(BASE_URL), lcd.FONT_Minya, 0x1d2951, rotate=0)
        M5TextBox(66, 78, "{}".format(token), lcd.FONT_Minya, 0x1d2951, rotate=0)
        M5Img(136, 142, "res/refresh.png", True)
    else:
        token = STATE['token']

    for i in range(10):
        resp = urequests.post(SYNC_URL.format(machine_id=token), json={
            'steps': steps,
            'battery': DATA['power']
        })
        gc.collect()
        if resp.status_code == 200:
            break
        else:
            del resp
            gc.collect()
        now = time.time()
        while time.time() - now < 60:
          if btnB.wasPressed():
              break
    else:
        nvs_erase("quazar:token")
        M5TextBox(66, 98, "Net Timeout", lcd.FONT_Minya, 0x1d2951, rotate=0)
        while True:
            pass

    data = resp.json()
    del resp
    gc.collect()
    for k in data:
        if k in DATA:
          DATA[k] = data[k]
    if currentAppearance != data['appearance']:
        resp = urequests.get(IMG_URL.format(machine_id=token))
        gc.collect()
        if resp.status_code != 200:
            del resp
            gc.collect()
            M5TextBox(66, 98, "Net Timeout", lcd.FONT_Minya, 0x1d2951, rotate=0)
            while True:
                pass
        with open('res/cat.png', 'wb+') as file:
            file.write(resp.content)
        del resp
        gc.collect()
    for i in range(10):
        # we wait to allow for other hardware functions to catch up, this function handles a lot of memory
        wait_ms(2)
    if STATE['token'] is None:
        STATE['token'] = token
        nvs_setstr("quazar:token", token)


def render_data(dials, mood, name, animate=False):
    for dial, data in dials.items():
        img = data["img"]
        x = data["X"]
        y = data["Y"]
        value = DATA[dial] // 10
        if value > 9:
            value = 9
        if value < 0:
            value = 0
        with FrameBuffer(x, y, 57, 58):
            img.show()
            M5Img(0, 0, "res/dial{}.png".format(value), True)
        data["icon"].show()
    mood.changeImg("res/{}.png".format(moods[DATA["mood"] % 5]))
    mood.show()
    name.setText("{:^8}".format(DATA["name"]))
    name.show()


MOVE_DIF = 0.5

if __name__ == "__main__":
    setScreenColor(0x181547)
    M5Img(0, 0, 'res/logo.png', True)

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect('Dartmouth Public', '')
    setScreenColor(0x222222)
    background = M5Img(0, 0, "res/space_room.png", True)
    imu0 = imu.IMU()

    # drop shutters here
    shutters = []
    for i in range(9):
        shutters.append(M5Img(0, 0 + (28 * i), "res/shutter.png", True))

    del shutters
    gc.collect()

    # relative images due to framebuffer stuff
    cropped = M5Img(0, 0, "res/cropped.png", False)
    cat = M5Img(0, 0, "res/cat.png", False)

    for dial in dials.values():
        # also framebuffered
        dial["img"] = M5Img(0, 0, "res/Dial.png", False)

    sync_data(0)

    # not framebuffered
    mood = M5Img(255, 174, "res/{}.png".format(moods[2]), False)
    name = M5TextBox(115, 210, "", lcd.FONT_Minya, 0xFFFFFF, rotate=0)

    # clear shutters
    background = M5Img(0, 0, "res/space_room.png", True)
    gc.collect()
    render_data(dials, mood, name, animate=True)

    Xmin = 70
    Xmax = 134
    Ymin = 90
    Ymax = 120
    tick = 0
    steps = 0
    aX, aY, aZ = imu0.acceleration
    lastX, lastY, lastZ = aX, aY, aZ
    while True:
        tick = (tick if isinstance(tick, Number) else 0) + 1
        if tick % 1 == 0:
            cat_move()
        if tick % 25 == 0:
            aX, aY, aZ = imu0.acceleration
            if abs(aX - lastX) > MOVE_DIF or abs(aY - lastY) > MOVE_DIF or abs(aZ - lastZ) > MOVE_DIF:
                steps += 1
            lastX, lastY, lastZ = aX, aY, aZ
        if tick % 300 == 0:
            sync_data(steps)
            render_data(dials, mood, name)
            steps = 0
            tick = 0
        if btnA.wasPressed() and btnC.wasPressed():
            nvs_erase("quazar:token")
            machine.reset()
        wait_ms(2)
