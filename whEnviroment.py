import json
import uuid
import numpy as np
import os.path
import os
from copy import copy


class whEnviroment:
    """
        This class contains the wrapper for interacting with the warhammer game.
        It is written similar to a openAIgym enviroment
    """
    def __init__(self, PlayerAI: bool):
        self.threshold =  0.8

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
        self.ordersfileName = "C:\Program Files (x86)\Steam\steamapps\common\Total War WARHAMMER II\orders.json"
        self.interconnectfileGame = "C:\Program Files (x86)\Steam\steamapps\common\Total War WARHAMMER II\interconnectGame.json"
        self.interconnectfileEnv = "C:\Program Files (x86)\Steam\steamapps\common\Total War WARHAMMER II\interconnectEnv.json"

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
        self.rawObservation= {}
        self.previousObservations = {}
        self.UidToUnitTypes = {}
    

    def step(self, action):
        self.__act(action)
        observation = self.__readObservation()
        reward, done = self.__calcReward(self.playerAI)
        return observation, reward, done


    def __act(self, ordersArray):
        alliedOrders = []
        for alliedOrder in ordersArray:
            alliedOrders.append(self.__singleOrder(alliedOrder))
        
        orders = {}
        orders["allies"] = alliedOrders


    def __singleOrder(self, orderArray):
         return { 
            "goto": {
                "x": orderArray[0],
                "y": orderArray[1],
                "moveFast": (orderArray[2] >= self.threshold) 
                },
            "attack": {
                "attack": orderArray[3],
                "unit": (orderArray[4] >= self.threshold)
            }
        }


    def __readObservation(self):
        """reads the most recent observation json gets called when the enveriment takes a step

        Returns:
            numpy array: A numpy array that contains the most recent observation
        """
        #copy observation from previous loop to previousObservation 
        self.previousObservations = copy(self.observations)

        #set all but the ally code to zero in observation for al UiD'sy
        for unit in self.observations:
            self.observations[unit] = self.__resetUnitObservation(self.observations[unit])

        f = open(self.observationfile)
        self.rawObservation = json.load(f)

        self.alliedObs = self.rawObservation[self.allies]
        self.enemyObs = self.rawObservation[self.enemies]
        
        observationArray = np.empty((0 ,self.observation_length), int)

        #populate the dictionary with observation array's
        for ally in self.alliedObs:
            self.observations[ally["UiD"]] = self.__singleObservation(ally,True)
            self.UidToUnitTypes[ally["UiD"]] = ally["type"]
        
        for enemy in self.enemyObs:
            self.observations[enemy["UiD"]]  = self.__singleObservation(enemy,False)
            self.UidToUnitTypes[enemy["UiD"]] = enemy["type"]

        # transfer to 2d array
        for unit in self.observations:
            observationArray = np.append(observationArray, self.observations[unit], axis=0)

        return observationArray


    def __resetUnitObservation(self, unit: np.array):
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


    def __singleObservation(self, unit, ally):
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
        observation = self.__NormalizeObservation(observation)
        return observation    


    def __NormalizeObservation(self, observation):
        """normalizes observation array

        Args:
            observation (ndarray): Single observation numpy array

        Returns:
            [ndarray]: normalized observation
        """
        observation = np.divide(np.add(observation,-self.low),np.add(self.high,-self.low))
        return observation


    def __calcReward(self, ally: bool):
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
                reward += self.__calcRewardSingle(ally["UiD"], -1)
            for enemy in self.enemyObs:
                reward += self.__calcRewardSingle(enemy["UiD"], 1)            
            if (self.rawObservation["win"] == True):
                done = True
                reward += self.unitValues["win"]
            if (self.rawObservation["win"] == False):
                done = True
                reward += self.unitValues["loss"]

        else:
            for ally in self.alliedObs:
                reward += self.__calcRewardSingle(ally["UiD"], 1)
            for enemy in self.enemyObs:
                reward += self.__calcRewardSingle(enemy["UiD"], -1)
            
            if (self.rawObservation["win"] == 'player'):
                done = True
                reward += self.unitValues["loss"]
            if (self.rawObservation["win"] == 'enemy'):
                done = True
                reward += self.unitValues["win"]
        return reward, done


    def __calcRewardSingle(self, unitUiD, sign):
        healthloss = self.previousObservations[unitUiD][0,-1] - self.observations[unitUiD][0,-1]
        rewardAbs = self.unitValues[self.UidToUnitTypes[unitUiD]] * healthloss * sign
        return rewardAbs


    def reset(self):
        self.__battleStarted = False
        observation = self.__readObservation()
        if "win" in self.rawObservation:
            if (self.rawObservation["win"]):
                print("rematch")
            else:
                print("force rematch")
        print("**************************")
        print("***   awaiting reset   ***")
        print("**************************")
        self.__waitForLoad()
        print("ready for battle")
        observation = self.__readObservation()
        return observation


    def __waitForLoad(self):
        try:
            os.remove(self.interconnectfileGame)
        except:
            pass
        while (not os.path.exists(self.interconnectfileGame)):
            pass
        f = open(self.interconnectfileEnv, "w")
        interconnect = {}
        interconnect["aiReady"] = True
        json.dump(interconnect, f)
        return
