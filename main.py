
import json, time, threading, keyboard,sys
import win32api
from ctypes import WinDLL
import numpy as np
from mss import mss as mss_module


def exiting():
    try:
        exec(type((lambda: 0).__code__)(0, 0, 0, 0, 0, 0, b'\x053', (), (), (), '', '', 0, b''))
    except:
        try:
            sys.exit()
        except:
            raise SystemExit
        
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
        self.triggerbot = False
        self.triggerbot_toggle = True
        self.exit_program = False 
        self.toggle_lock = threading.Lock()

        with open('config.json') as json_file:
            data = json.load(json_file)

        try:
            self.trigger_hotkey = int(data["trigger_hotkey"],16)
            self.always_enabled =  data["always_enabled"]
            self.trigger_delay = data["trigger_delay"]
            self.base_delay = data["base_delay"]
            self.color_tolerance = data["color_tolerance"]
            self.trigger_times = 0
            self.R, self.G, self.B = (250, 100, 250)  # purple
        except:
            exiting()

    def cooldown(self):
        time.sleep(0.1)
        with self.toggle_lock:
            self.triggerbot_toggle = True
            kernel32.Beep(440, 75), kernel32.Beep(700, 100) if self.triggerbot else kernel32.Beep(440, 75), kernel32.Beep(200, 100)

    def searcherino(self):
        img = np.array(self.sct.grab(self.GRAB_ZONE))
        pmap = np.array(img)
        pixels = pmap.reshape(-1, 4)
        color_mask = (
            (pixels[:, 0] > self.R -  self.color_tolerance) & (pixels[:, 0] < self.R +  self.color_tolerance) &
            (pixels[:, 1] > self.G -  self.color_tolerance) & (pixels[:, 1] < self.G +  self.color_tolerance) &
            (pixels[:, 2] > self.B -  self.color_tolerance) & (pixels[:, 2] < self.B +  self.color_tolerance)
        )
        matching_pixels = pixels[color_mask]
        
        if self.triggerbot and len(matching_pixels) > 0:
            delay_percentage = self.trigger_delay / 100.0  
            
            actual_delay = self.base_delay + self.base_delay * delay_percentage
            
            time.sleep(actual_delay)
            keyboard.press_and_release("k")
            self.trigger_times = self.trigger_times + 1
            print("TRIGGERED", self.trigger_times,)
            
    def adjusts(self):
        print("ADJUSTING, PRESS:")
        print("0: ZONE -")
        print("9: ZONE +")
        print("8: trigger_delay -")
        print("7: trigger_delay +")
        print("6: TEST")
        print("=: START")
        loop = True
        while loop:
            time.sleep(0.2)
            if keyboard.is_pressed("0"):
                self.ZONE = self.ZONE - 1
                self.GRAB_ZONE = (
            int(WIDTH / 2 - self.ZONE),
            int(HEIGHT / 2 - self.ZONE),
            int(WIDTH / 2 + self.ZONE),
            int(HEIGHT / 2 + self.ZONE),)
                print("ZONE: ", self.ZONE)
            if keyboard.is_pressed("9"):
                self.ZONE = self.ZONE + 1
                self.GRAB_ZONE = (
            int(WIDTH / 2 - self.ZONE),
            int(HEIGHT / 2 - self.ZONE),
            int(WIDTH / 2 + self.ZONE),
            int(HEIGHT / 2 + self.ZONE),)
                print("ZONE: ", self.ZONE)
            if keyboard.is_pressed("8"):
                self.trigger_delay = self.trigger_delay - 1
                print("trigger_delay: ", self.trigger_delay)
            if keyboard.is_pressed("7"):
                self.trigger_delay = self.trigger_delay + 1
                print("trigger_delay: ", self.trigger_delay)
            if keyboard.is_pressed("6"):
                self.triggerbot = True
                self.searcherino()
            if keyboard.is_pressed("="):
                print("ADJUSTED:","ZONE=", self.ZONE,"DELAY=", self.trigger_delay)
                loop = False

    def toggle(self):
        if keyboard.is_pressed("f10"):  
            with self.toggle_lock:
                if self.triggerbot_toggle:
                    self.triggerbot = not self.triggerbot
                    print(self.triggerbot)
                    self.triggerbot_toggle = False
                    threading.Thread(target=self.cooldown).start()

            if keyboard.is_pressed("ctrl+shift+x"):  # Check for the kkkkk keybind
                self.exit_program = True
                exiting()
        
    def hold(self):
        print("LOOPING")
        while True:
            while win32api.GetAsyncKeyState(self.trigger_hotkey) < 0:
                self.triggerbot = True
                self.searcherino()
            else:
                time.sleep(0.1)
            if keyboard.is_pressed("ctrl+shift+x"):  # Check for the exit keybind
                self.exit_program = True
                exiting()

    def starterino(self):
        while not self.exit_program:  # Keep running until the exit_program flag is True
            self.adjusts()
            if self.always_enabled == True:
                self.toggle()
                self.searcherino() if self.triggerbot else time.sleep(0.1)
            else:
                self.hold()

triggerbot().starterino()