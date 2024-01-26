import json, time, threading, keyboard, sys
from os import system, _exit
import win32api
from ctypes import WinDLL
import numpy as np
from mss import mss as mss_module
import os
from keyboard import is_pressed, block_key, unblock_key
import random
import string


user32, kernel32, shcore = (
    WinDLL("user32", use_last_error=True),
    WinDLL("kernel32", use_last_error=True),
    WinDLL("shcore", use_last_error=True),
)

shcore.SetProcessDpiAwareness(2)
WIDTH, HEIGHT = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]


class triggerbot:
    def __init__(self):
        self.ZONE = 5
        self.GRAB_ZONE = (
            int(WIDTH / 2 - self.ZONE),
            int(HEIGHT / 2 - self.ZONE),
            int(WIDTH / 2 + self.ZONE),
            int(HEIGHT / 2 + self.ZONE),
        )
        self.sct = mss_module()
        self.triggeron = False
        self.triggerbot_toggle = True
        self.toggle_lock = threading.Lock()
        self.trigger_times = 0
        self.R, self.G, self.B = (250, 100, 250)  # purple
        self.trigger_delay = 40
        self.color_tolerance = 70
        self.counterstrafe = True
        self.cooldowntime = 5
        self.trigger_hotkey = 0xA0
        self.always_enabled = False
        self.base_delay = 0.01
        self.adjusting =1
        
    def randomgen(self, size=12, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))


    def saveconfig(self):
        config = {
            "trigger_hotkey": hex(self.trigger_hotkey),
            "always_enabled": self.always_enabled,
            "trigger_delay": self.trigger_delay,
            "base_delay": self.base_delay,
            "color_tolerance": self.color_tolerance,
            "counterstrafe": self.counterstrafe,
            "cooldowntime": self.cooldowntime,
        }
        with open("config.json", "w") as outfile:
            json.dump(config, outfile)

        with open("config.json") as json_file:
            data = json.load(json_file)

        try:
            self.trigger_hotkey = int(data["trigger_hotkey"], 16)
            self.always_enabled = data["always_enabled"]
            self.trigger_delay = data["trigger_delay"]
            self.base_delay = data["base_delay"]
            self.color_tolerance = data["color_tolerance"]
            self.counterstrafe = data["counterstrafe"]
            self.cooldowntime = data["cooldowntime"]

        except (self):
            print("ERROR LOADING CONFIG, TRYING TO FIX... PLEASE RESTART")
            self.saveconfig
            time.sleep(5)
            _exit(1)

    def printing(self):
        os.system("cls")
        print("ADJUSTING, PRESS:")
        print("\033[93mF12\033[0m: TEST")
        print("\033[92mF10\033[0m/\033[91mF9\033[0m ZONE: ", self.ZONE)
        print("\033[92mF8\033[0m/\033[91mF7\033[0m DELAY: ", self.trigger_delay)
        print("\033[92mF6\033[0m/\033[91mF5\033[0m COLOR TOLERANCE: ", self.color_tolerance)
        if self.counterstrafe:
            print("\033[92mF4\033[0m COUNTERSTRAFE: ", "\033[92mYes\033[0m")
        else:
            print("\033[91mF4\033[0m COUNTERSTRAFE: ", "\033[91mNo\033[0m")
        print("\033[92mI\033[0m/\033[91mO\033[0m COOLDOWN TIME: ", self.cooldowntime)
        print("\033[93mF3\033[0m: SAVE")
        print("\033[94m=\033[0m: TO START/ADJUST")

    def cooldown(self):
        time.sleep(0.1)
        with self.toggle_lock:
            self.triggerbot_toggle = True
            kernel32.Beep(440, 75), kernel32.Beep(
                700, 100
            ) if self.triggeron else kernel32.Beep(440, 75), kernel32.Beep(200, 100)

    def searcherino(self):
        blocked, held = [], []
        img = np.array(self.sct.grab(self.GRAB_ZONE))
        pmap = np.array(img)
        pixels = pmap.reshape(-1, 4)
        color_mask = (
            (pixels[:, 0] > self.R - self.color_tolerance)
            & (pixels[:, 0] < self.R + self.color_tolerance)
            & (pixels[:, 1] > self.G - self.color_tolerance)
            & (pixels[:, 1] < self.G + self.color_tolerance)
            & (pixels[:, 2] > self.B - self.color_tolerance)
            & (pixels[:, 2] < self.B + self.color_tolerance)
        )
        matching_pixels = pixels[color_mask]

        if self.triggeron and len(matching_pixels) > 0:
            delay_percentage = self.trigger_delay / 100.0

            actual_delay = self.base_delay + self.base_delay * delay_percentage

            time.sleep(actual_delay)
            if (self.counterstrafe == True) and (
                any(user32.GetKeyState(k) > 1 for k in [87, 65, 83, 68])
            ):
                if is_pressed("a"):
                    block_key(30)
                    blocked.append(30)
                    user32.keybd_event(68, 0, 0, 0)
                    held.append(68)
                if is_pressed("d"):
                    block_key(32)
                    blocked.append(32)
                    user32.keybd_event(65, 0, 0, 0)
                    held.append(65)
                if is_pressed("w"):
                    block_key(17)
                    blocked.append(17)
                    user32.keybd_event(83, 0, 0, 0)
                    held.append(83)
                if is_pressed("s"):
                    block_key(31)
                    blocked.append(31)
                    user32.keybd_event(87, 0, 0, 0)
                    held.append(87)
            keyboard.press_and_release("k")
            self.trigger_times = self.trigger_times + 1
            for b in blocked:
                unblock_key(b)
            for h in held:
                user32.keybd_event(h, 0, 2, 0)
            print(
                "TRIGGERED",
                self.trigger_times,
            )
            time.sleep(self.cooldowntime / 10)

    def adjusts(self):
        self.printing()
        time.sleep(0.2)
        while True:
            if keyboard.is_pressed("i"):
                self.cooldowntime = max(0, self.cooldowntime + 1)
                self.printing()
                time.sleep(0.2)
            if keyboard.is_pressed("o"):
                self.cooldowntime = max(0, self.cooldowntime - 1)
                self.printing()
                time.sleep(0.2)
            if keyboard.is_pressed("f12"):
                self.triggeron = True
                self.searcherino()
            if keyboard.is_pressed("f10"):
                if self.ZONE > 1:
                    self.ZONE = self.ZONE + 1
                    self.GRAB_ZONE = (
                        int(WIDTH / 2 - self.ZONE),
                        int(HEIGHT / 2 - self.ZONE),
                        int(WIDTH / 2 + self.ZONE),
                        int(HEIGHT / 2 + self.ZONE),
                    )
                    self.printing()
                    time.sleep(0.2)
                else:
                    self.printing()
            if keyboard.is_pressed("f9"):
                self.ZONE = self.ZONE - 1
                self.GRAB_ZONE = (
                    int(WIDTH / 2 - self.ZONE),
                    int(HEIGHT / 2 - self.ZONE),
                    int(WIDTH / 2 + self.ZONE),
                    int(HEIGHT / 2 + self.ZONE),
                )
                self.printing()
                time.sleep(0.2)
            if keyboard.is_pressed("f8"):
                self.trigger_delay = self.trigger_delay + 1
                self.printing()
                time.sleep(0.2)
            if keyboard.is_pressed("f7"):
                self.trigger_delay = self.trigger_delay - 1
                self.printing()
                time.sleep(0.2)
            if keyboard.is_pressed("f6"):
                self.color_tolerance = self.color_tolerance + 1
                self.printing()
                time.sleep(0.2)
            if keyboard.is_pressed("f5"):
                self.color_tolerance = self.color_tolerance - 1
                self.printing()
                time.sleep(0.2)
            if keyboard.is_pressed("f4"):
                self.counterstrafe = not self.counterstrafe
                self.printing()
                time.sleep(0.2)
            if keyboard.is_pressed("f3"):
                self.saveconfig()
                print("SAVED")
                time.sleep(0.3)
                self.printing()
            if keyboard.is_pressed("="):
                break 

    def toggle(self):
        if keyboard.is_pressed("f1"):
            with self.toggle_lock:
                if self.triggerbot_toggle:
                    self.triggeron = not self.triggeron
                    print(self.triggeron)
                    self.triggerbot_toggle = False
                    threading.Thread(target=self.cooldown).start()

    def hold(self):
        os.system("cls")
        print("ON")
        while True:
            if keyboard.is_pressed("="):
                self.adjusting = 1
                break
            while win32api.GetAsyncKeyState(self.trigger_hotkey) < 0:
                self.triggeron = True
                self.searcherino()

    def starterino(self):
        system(
            "mode 40,18 & title "+ (self.randomgen()) + " & powershell $H=get-host;$W=$H.ui.rawui;$B=$W.buffersize;$B.width=80;$B.height=9999;$W.buffersize=$B;"
        )
        while True:
            if self.adjusting == 1:
                self.adjusts()
                self.adjusting = 0
            time.sleep(0.3)
            if self.always_enabled == True:
                self.toggle()
                self.searcherino() if self.triggeron else time.sleep(0.1)
            else:
                self.hold()


triggerbot().starterino()
