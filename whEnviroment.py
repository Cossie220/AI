import json
import numpy as np
import os.path
from whGUI import whGUI
from copy import copy


class whEnviroment:
    """
        This class contains the wrapper for interacting with the warhammer game.
        It is written similar to a openAIgym enviroment
    """
    def __init__(self, PlayerAI: bool):
        # initialize variabels
        self.allies = "allies"  
        self.enemies = "enemies"
        self.position = "position"
        self.observation_length = 12

        self.playerAI = PlayerAI

        # observation high low settings to normalize the observation
        self.low = np.array([0,-500,-500,0,0,0,0,0,0,0,0,0])
        self.high = np.array([1,500,500,360,100,3,1,1,1,1,1,1])

        # initialize where to find the observation and orders file 
        self.observationfile = "C:\Program Files (x86)\Steam\steamapps\common\Total War WARHAMMER II\observation.json"
        self.ordersfile = "C:\Program Files (x86)\Steam\steamapps\common\Total War WARHAMMER II\orders.json"
        self.interconnectfile = "C:\Program Files (x86)\Steam\steamapps\common\Total War WARHAMMER II\interconnect.json"

        # temp value of the diffrent units values to determine reward
        self.unitValues = {
            "wh_main_emp_cha_karl_franz_0": 1250,
            "wh_main_emp_inf_handgunners": 600,
            "wh_main_emp_cav_empire_knights": 850,
            "win": 10000,
            "loss": -10000
        }

        # temp wile change to export of database
        self.unitTypes = {
            "wh_main_emp_cha_karl_franz_0": 1,
            "wh_main_emp_inf_handgunners": 2,
            "wh_main_emp_cav_empire_knights": 3
        }

        self.observations = {}
        self.previousObservations = {}
        self.UidToUnitTypes = {}
    

    def readObservation(self):
        """reads the most recent observation json gets called when the enveriment takes a step

        Returns:
            numpy array: A numpy array that contains the most recent observation
        """
        #copy observation from previous loop to previousObservation 
        self.previousObservations = copy(self.observations)

        #set all but the ally code to zero in observation for al UiD'sy
        for unit in self.observations:
            self.observations[unit] = self.resetUnitObservation(self.observations[unit])

        f = open(self.observationfile)
        self.rawObservation = json.load(f)

        self.alliedObs = self.rawObservation[self.allies]
        self.enemyObs = self.rawObservation[self.enemies]
        
        observationArray = np.empty((0 ,self.observation_length), int)

        #populate the dictionary with observation array's
        for ally in self.alliedObs:
            self.observations[ally["UiD"]] = self.singleObservation(ally,True)
            self.UidToUnitTypes[ally["UiD"]] = ally["type"]
        
        for enemy in self.enemyObs:
            self.observations[enemy["UiD"]]  = self.singleObservation(enemy,False)
            self.UidToUnitTypes[enemy["UiD"]] = enemy["type"]

        # transfer to 2d array
        for unit in self.observations:
            observationArray = np.append(observationArray, self.observations[unit], axis=0)

        return observationArray


    def resetUnitObservation(self, unit: np.array):
        """function to reset observation to 0 appart from allience 

        Args:
            unit (np.array): array to reset

        Returns:
            [np.array]: zero observation (only alliance filled in)
        """
        resetArray = np.ones((1,self.observation_length))
        resetArray[0,0] = 0
        resetArray = np.multiply(resetArray,unit)
        resetArray = np.add(unit, -resetArray)
        return resetArray


    def singleObservation(self, unit, ally):
        position = unit[self.position]
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


    def calcReward(self, ally: bool):
        """[summary]

        Args:
            ally (bool): [description]

        Returns:
            [type]: [description]
        """
        reward = 0
        done = False
        if ally:
            for ally in self.alliedObs:
                reward += self.calcRewardSingle(ally["UiD"], -1)
            for enemy in self.enemyObs:
                reward += self.calcRewardSingle(enemy["UiD"], 1)            
            if (self.rawObservation["win"] == True):
                done = True
                reward += self.unitValues["win"]
            if (self.rawObservation["win"] == False):
                done = True
                reward += self.unitValues["loss"]
        else:
            for ally in self.alliedObs:
                reward += self.calcRewardSingle(ally["UiD"], 1)
            for enemy in self.enemyObs:
                reward += self.calcRewardSingle(enemy["UiD"], -1)
            
            if (self.rawObservation["win"] == 'player'):
                done = True
                reward += self.unitValues["loss"]
            if (self.rawObservation["win"] == 'enemy'):
                done = True
                reward += self.unitValues["win"]
        return reward, done


    def calcRewardSingle(self, unitUiD, sign):
        healthloss = self.previousObservations[unitUiD][0,-1] - self.observations[unitUiD][0,-1]
        rewardAbs = self.unitValues[self.UidToUnitTypes[unitUiD]] * healthloss * sign
        return rewardAbs


    def act(self, action):
        pass


    def step(self, action):
        self.act(action)
        observation = self.readObservation()
        reward, done = self.calcReward(self.playerAI)
        return observation, reward, done


    def reset(self):
        if (self.rawObservation["win"]):
            whGUI.Rematch()
        else:
            whGUI.Rematch()
        print("**************************")
        print("***   awaiting reset   ***")
        print("**************************")
        self.waitForLoad()
        observation = self.readObservation()
        return observation
        
    def waitForLoad(self):
        while (not os.path.exists(self.interconnectfile)):
            pass
        return


    def writeOrders(self, order):
        pass
