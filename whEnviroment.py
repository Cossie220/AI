import json
import numpy as np


class whEnviroment:
    """
        This class contains the wrapper for interacting with the warhammer game.
        It is written similar to a openAIgym enviroment
    """
    def __init__(self, PlayerAI: bool, enemyAI: bool):
        # initialize variabels
        self.allies = "allies"  
        self.enemies = "enemies"
        self.position = "position"
        self.observation_length = 12

        self.playerAI = PlayerAI
        self.enemyAI = enemyAI

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
            "loss": -10000
        }

        # temp wile change to export of database
        self.unitTypes = {
            "wh_main_emp_cha_karl_franz_0": 1,
            "wh_main_emp_inf_handgunners": 2,
            "wh_main_emp_cav_empire_knights": 3
        }

        self.observations = {}
        self.previousObservation = {}
    

    def readObservation(self):
        """reads the most recent observation json gets called when the enveriment takes a step

        Returns:
            numpy array: A numpy array that contains the most recent observation
        """
        #copy observation from previous loop to previousObservation 
        self.previousObservation = self.observations

        #set all but the ally code to zero in observation for al UiD'sy
        for unit in self.observations:
            self.observations[unit] = self.resetUnitObservation(self.observations[unit])

        f = open(self.observationfile)
        self.observation = json.load(f)

        self.alliedObs = self.observation[self.allies]
        self.enemyObs = self.observation[self.enemies]
        
        observationArray = np.empty((0 ,self.observation_length), int)

        #populate the dictionary with observation array's
        for ally in self.alliedObs:
            self.observations[ally["UiD"]] = self.singleObservation(ally,True)
        
        for enemy in self.enemyObs:
            self.observations[enemy["UiD"]]  = self.singleObservation(enemy,False)

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

        if ally:
            reward = 0
        reward = 0
        done = False        
        return reward, done

    def act(self, action):
        pass

    def step(self, action):
        self.act(action)
        observation = self.readObservation()
        reward, done = self.calcReward()
        return observation, reward, done


    def reset():
        print("**************************")
        print("***   awaiting reset   ***")
        print("**************************")
        observation = None
        return observation
        

    def writeOrders(self, order):
        pass
