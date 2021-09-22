from time import time, sleep
from pydirectinput import press
import pyautogui



class whGUI:
    def __init__(self, x = 1208, y = 336):
        pyautogui.PAUSE = 0.2
        self.TopLeft = { "x": x, "y": y }
        
        startBattleOffset = { "x": 512, "y": 99 }
        endBattleOffset = { "x": 512, "y": 54}
        rematchOffset = { "x": 512, "y": 434}
        confirmOffset = { "x": 492, "y": 450}

        self.startbattle = { "x": self.TopLeft["x"] + startBattleOffset["x"], 
                             "y": self.TopLeft["y"] + startBattleOffset["y"]}

        self.endBattle = { "x": self.TopLeft["x"] + endBattleOffset["x"], 
                           "y": self.TopLeft["y"] + endBattleOffset["y"]}

        self.rematch = { "x": self.TopLeft["x"] + rematchOffset["x"], 
                         "y": self.TopLeft["y"] + rematchOffset["y"]}
                
        self.confirm = { "x": self.TopLeft["x"] + confirmOffset["x"], 
                         "y": self.TopLeft["y"] + confirmOffset["y"]}

        self.middle = { "x": 1720, "y":720}

    def focus(self):
        pyautogui.click(x=self.middle["x"], y=self.middle["y"])

    def forceRematch(self):
        self.focus()
        press('esc')
        pyautogui.click(self.rematch["x"], self.rematch["y"])
        pyautogui.click(self.confirm["x"], self.confirm["y"])
    
    def startBattle(self):
        self.focus()
        pyautogui.click(self.startbattle["x"], self.startbattle["y"])

    def Rematch(self):
        self.focus
        pyautogui.click(self.endBattle["x"], self.endBattle["y"])
        pyautogui.click(self.rematch["x"], self.rematch["y"])


        