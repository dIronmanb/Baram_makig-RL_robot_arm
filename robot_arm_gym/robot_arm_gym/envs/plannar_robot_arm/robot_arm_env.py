from tkinter.font import ROMAN
import gym
import math as m
import random
# import pygame
import numpy as np
from gym import utils
from gym import error, spaces
from gym.utils import seeding
from gym import spaces

# from scipy.spatial.distance import euclidean

PI = 3.141592653
degree2rad = PI/180
rad2degree = 180/PI

class RobotArmEnvV0(gym.Env):
    
    metadata = {'render.models': ['human']} # visualize robot arm model
    max_episode_steps = 300
    
    def __init__(self):
        super(RobotArmEnvV0, self).__init__()
        
        self.margin = 1.0
        self.goal = self._get_goal() # 내가 입력으로 넣어주는 부분
        self.past_dist = np.inf #맨 처음 past_dist의 경우는 무한대로
        
        self.r1 = 10.5
        self.r2 = 10.5
        self.r3 = 7.5
        self.theta1 = 0
        self.theta2 = 0
        self.theta3 = 0
        
        self.pos_y, self.pos_x = self._theta2position()
        
        self.min = 0
        self.max = self.r1 + self.r2 + self.r3
        
        
        self.elapsed_steps = 0
        
        self.observation_space = self._get_observation_space()
        self.action_space = self._get_action_space()
        
        # ------ #
        self.state = None
        self.observation = None
    
    
    def step(self, action):
        
        # action
        if type(action) == list: action = np.array(action)
        
        # one step elapse
        self.elapsed_steps += 1
        
        # after one step, the state is
        self.theta1 += action[0]
        self.theta2 += action[1]
        self.theta3 += action[2]
        self.pos_y, self.pos_x = self._theta2position()
        
        
        observation = {"theta1": self.theta1,
                       "theta2": self.theta2, 
                       "theta3": self.theta3, 
                       "pos_x": self.pos_x,
                       "pos_y": self.pos_y,
                       "distance": self._get_distance()}
        
        reward, done, info = self._get_reward()
        
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
        
        # return
        return observation, reward, done, info # {}엔 info

    def take_action(self, action):
        # 정말로 행동을 나타내는 부분
        
        a = 1
        pass
    
    # Reset시 상태
    def reset(self, theta_s = None):
        '''
            Environment reset
        arg:
            position(list[3] or np.array[2]): [theta1, theta2, theta3] initial robot position.
            
        return:
            np.array: environment state
        '''
        if theta_s:
            assert len(theta_s) == 3, "Dimension for position must be 2 but current position length is {}".format(len(theta_s))
            if isinstance(theta_s) == list:
                theta_s = np.array(theta_s)
        
        else:
            theta_s = np.zeros(self.observation_space[0])
        
        self.state = theta_s
        self.theta1, self.theta2, self.theta3 = self.state
        self.goal = self._get_goal()
        self.pos_y, self.pos_x = self._theta2position()
        self.past_dist = np.inf
        
        
        observation = {"theta1": self.theta1,
                       "theta2": self.theta2, 
                       "theta3": self.theta3, 
                       "pos_x": self.pos_x,
                       "pos_y": self.pos_y,
                       "distance": self._get_distance()}
        
        return observation
    
    # 보상 구하는 함수
    def _get_reward(self):
        
        done = False    
        # When you need an element to check for learning
        info = {}
    
        
        # elapsed_step이 max_step보다 크면
        if self.elapsed_steps >= self.max_episode_steps:
            done = True
            reward = -10
            info['final_status'] = 'max_steps_exceeded'
            
        
        else:
            
            dist = self._get_distance()
            
            # 또는 목표 지점 거리 내에 존재한다면
            if  dist < self.margin:
                done = True
                reward = +100
                info['final_status'] = 'Mission Clear'         
            
            else:
                # 이전 거리와 비교하여 목표지점에 더 다다랐으면
                if self.past_dist - dist > 0:
                    reward = 0.5
                # 그게 아니라면
                else:
                    reward = 0
                    self.past_dist = dist
                    
        return reward, done, info
    
    # 거리 구하는 함수
    def _get_distance(self):
        
        goal_x, goal_y = self.goal
        current_x, current_y = self.pos_x, self.pos_y
        
        return m.sqrt((goal_x - current_x) ** 2 + (goal_y - current_y) ** 2)
    
    # 세타를 통해 위치 구하기(y,x)
    def _theta2position(self):
        return np.array([    self.r1 * m.sin(self.theta1 * degree2rad) +
                    self.r2 * m.sin((self.theta1 + self.theta2) * degree2rad) + 
                    self.r3 * m.sin((self.theta1 + self.theta2 + self.theta3) * degree2rad) 
                    ,
                    self.r1 * m.cos(self.theta1 * degree2rad) +
                    self.r2 * m.cos((self.theta1 + self.theta2) * degree2rad) +
                    self.r3 * m.cos((self.theta1 + self.theta2 + self.theta3) * degree2rad)] )
        
    # 목표 지점 랜덤하게 생성
    def _get_goal(self):
        
        x = random.uniform(-self.max, self.max)
        y = random.uniform(0, self.max)
        goal = [x, y]
                
        return self._is_in_workspace(goal)     
    
    # 해당 goal이 workspace안에 있는지를 판별
    def _is_in_workspace(goal):
            
        # (x, y)
        
        # 반원 고리 내부안에 있는 값인지를 확인
        try:
            # y값이 음수면
            if goal[1] < 0:
                raise Exception
        except Exception as e:
            print("coordinate of y is minus.")

        # 범위 밖에 있다면 해당 theta는 그대로 유지하면서 workspace 내부의 점으로 위치시키기
        r_max = 25.5
        r_min = 5.8        
        if goal[0] ** 2 + goal[1] ** 2 < r_min ** 2:
            
            theta = m.atan2(goal[0], goal[1])
            
            goal[1] = m.ceil(r_min * m.sin(theta))
            goal[0] = m.ceil(r_min * m.cos(theta))
            
        elif goal[1] ** 2 + goal[0] ** 2 > r_max ** 2:
            
            theta = m.atan2(goal[0], goal[1])

            goal[1] = m.trunc(r_max * m.sin(theta))
            goal[0] = m.trunc(r_max * m.cos(theta))
            
        return goal
    
    def _get_observation_space(self):
        # 관찰 가능한 theta는 0 ~ 270이다.
        max_obs = np.array([0] * 3)
        min_obs = np.array([270] * 3)

        # theta1, theta2, theta3, pos_x, pos_y        
        # max_obs = np.array([0, 0, 0, -self.max, 0])
        # min_obs = np.array([270, 270, 270, self.max, self.max)
        
        return spaces.Box(low = min_obs, high = max_obs, dtype = np.float32)
    
    def _get_action_space():
        # 액션으로 취할 수 있는 건 각 세타마다
        # [-1, 0, 1]이다.
        """
        A discrete space in :math:`\{ 0, 1, \dots, n-1 \}`.
        A start value can be optionally specified to shift the range to :math:`\{ a, a+1, \dots, a+n-1 \}`.
        
        Example::
            >>> Discrete(2)            # {0, 1}
            >>> Discrete(3, start=-1)  # {-1, 0, 1}
        """
        
        """
        The multi-discrete action space consists of a series of discrete action spaces with different number of actions in each. It is useful to represent game controllers or keyboards where each key can be represented as a discrete action space. It is parametrized by passing an array of positive integers specifying number of actions for each discrete action space.
        Note:
            Some environment wrappers assume a value of 0 always represents the NOOP action.
            e.g. Nintendo Game Controller - Can be conceptualized as 3 discrete action spaces:
            1. Arrow Keys: Discrete 5  - NOOP[0], UP[1], RIGHT[2], DOWN[3], LEFT[4]  - params: min: 0, max: 4
            2. Button A:   Discrete 2  - NOOP[0], Pressed[1] - params: min: 0, max: 1
            3. Button B:   Discrete 2  - NOOP[0], Pressed[1] - params: min: 0, max: 1
            It can be initialized as ``MultiDiscrete([ 5, 2, 2 ])``
         """
        # theta1: [1, 2, 3] -> 추후 쓸 때는 [1,2,3] = [-1,0,1]로
        # >>> a = MultiDiscrete([3, 3, 3])
        # >>> a[0]
        # Discrete(3)
        
        return spaces.MultiDiscrete([3,3,3])
    
    def _get_state(self):
        return self.state
    
    def render(self):
        pass

    # error를 감지하는 코드: 근데 내가 통신을 하는 게 아니니까 2학기 작품에서 계속...
    
class RobotArmEnvV1(RobotArmEnvV0):
    
    def __init__(self):
        super(RobotArmEnvV1, self).__init__()
    


