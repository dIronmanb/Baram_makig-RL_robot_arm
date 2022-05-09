import gym
import math
# import pygame
import numpy as np
from gym import utils
from gym import error, spaces
from gym.utils import seeding
# from scipy.spatial.distance import euclidean

class RobotArmEnvV0(gym.Env):
    
    def __init__(self):
        pass
    
    def step(self, action):
        '''
        Agrument:
            action
        Returns:
            observation, reward, done, info
        
        (observation)
            an environment-specific object representing your observation of
            the environment.
        
        (reward)
            amount of reward achieved by the previous action. The scale
            varies between environments, but ***goal is always to increase
            your total reward.***
        
        (done)
            whether it's time to reset the environment again. Most (but not
            all) tasks are divided up into well-defined episodes, and done
            being True indicates the episode has terminated. (For example,
            perhaps the pole tipped too far, or you lost your last life.)
        
        (info)
            diagnostic information useful for debugging. It can sometimes
            be useful for learning (for example, it might contain the raw
            probabilities behind the environment's last state change).
            However, official evaluations of your agent are not allowed to
            use this for learning.
            
        '''
        self.take_action(action)
        self.status = self.env.step()
        reward = self.get_reward()
        ob = self.env.get_state()
        done = self.status != hfo_py.IN_GAME
        return ob, reward, done, {} # {}엔 info
    
    def reset(self):
        pass
    
    def take_action(self, action):
        pass
    
    def _get_reward(self):
        pass
    
    def _get_observation_space():
        pass
    
    def _get_action_space():
        pass
    
    def _get_state():
        pass

    # error를 감지하는 코드: 근데 내가 통신을 하는 게 아니니까 2학기 작품에서 계속...
    
class RobotArmEnvV1(RobotArmEnvV0):
    
    def __init__(self):
        super(RobotArmEnvV1, self).__init__()
    


