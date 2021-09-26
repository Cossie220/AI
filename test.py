from whEnviroment import whEnviroment
from time import sleep
env = whEnviroment(True)
obs = env.reset()
sleep(2)
env.startBattle()
print("succes!!")