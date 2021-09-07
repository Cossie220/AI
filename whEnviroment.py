import json

class whEnviroment:
    def __init__(self):
        self.allies = "allies"
        self.enemies = "enemies"
        
        self.observationfile = "C:\Program Files (x86)\Steam\steamapps\common\Total War WARHAMMER II\observation.json"
        self.ordersfile = "C:\Program Files (x86)\Steam\steamapps\common\Total War WARHAMMER II\orders.json"
    
    def readObservation(self):
        f = open(self.observationfile)
        self.observation = json.load(f)

        self.allies = self.observation[self.allies]
        self.enemies = self.observation[self.enemies]
        
    
    def NormalizeObservation(self):
        pass

    def calcReward(self):
        pass

    def writeOrders(self, order):
        pass
