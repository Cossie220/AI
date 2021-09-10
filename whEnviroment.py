import json
import numpy as np


class whEnviroment:
    """
        This class contains the wrapper for interacting with the warhammer game.
        It is written similar to a openAIgym enviroment
    """
    def __init__(self):
        # initialize variabels
        self.allies = "allies"  
        self.enemies = "enemies"
        self.position = "position"
        self.observation_length = 12

        # observation high low settings to normalize the observation
        self.low = np.array([0,-500,-500,0,0,0,0,0,0,0,0,0])
        self.high = np.array([1,500,500,360,100,3,1,1,1,1,1,1])

        # initialize where to find the observation and orders file 
        self.observationfile = "C:\Program Files (x86)\Steam\steamapps\common\Total War WARHAMMER II\observation.json"
        self.ordersfile = "C:\Program Files (x86)\Steam\steamapps\common\Total War WARHAMMER II\orders.json"

        # temp value of the diffrent units values to determine reward
        self.unitValues = {
            "wh_main_emp_cha_karl_franz_0": 1250,
            "wh_main_emp_inf_handgunners": 600,
            "wh_main_emp_cav_empire_knights": 850,
            "win": 10000,
            "los": -10000
        }

        # temp wile change to export of database
        self.unitTypes = {
            "wh_main_emp_cha_karl_franz_0": 1,
            "wh_main_emp_inf_handgunners": 2,
            "wh_main_emp_cav_empire_knights": 3
        }
    

    def readObservation(self):
        """reads the most recent observation json gets called when the enveriment takes a step

        Returns:
            numpy array: A numpy array that contains the most recent observation
        """
        f = open(self.observationfile)
        self.observation = json.load(f)

        self.alliedObs = self.observation[self.allies]
        self.enemyObs = self.observation[self.enemies]
        
        observations = np.empty((0 ,self.observation_length), int)

        for ally in self.alliedObs:
            observation = self.singleObservation(ally,True)
            observations = np.append(observations,observation,axis= 0)
        
        for enemy in self.enemyObs:
            observation = self.singleObservation(enemy,False)
            observations = np.append(observations,observation,axis= 0)
        
        return observations

    def singleObservation(self, unit, ally):
        position = unit[self.position]
        type = unit["type"]
        #print(self.unitTypes[type])
        observation = np.array(
            [[
                ally,
                position["x"],
                position["y"],
                position["bearing"],
                position["width"],
                self.unitTypes[unit["type"]],
                # unit["can_fly"],
                # unit["is_flying"],
                unit["is_under_missile_attack"],
                unit["in_melee"],
                unit["is_wavering"],
                unit["is_routing"],
                unit["is_shattered"],
                unit["unary_hitpoints"]     
            ]]
        )
        observation = self.NormalizeObservation(observation)
        return observation    


    def NormalizeObservation(self, observation):
        """normalizes observation array

        Args:
            observation (ndarray): Single observation numpy array

        Returns:
            [ndarray]: normalized observation
        """
        observation = np.divide(np.add(observation,-self.low),np.add(self.high,-self.low))
        return observation

    def calcReward(self):
        pass

    def writeOrders(self, order):
        pass
