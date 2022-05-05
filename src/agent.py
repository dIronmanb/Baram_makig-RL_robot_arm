from re import X
from tkinter import E
import numpy as np

import math as m
import numpy as np

PI = 3.141592653
degree2rad = PI/180
rad2degree = 180/PI

class Agent():
    
    def __init__(self, config, goal = [10, 10]):       
        
        # agent link length >> 추후 다시 측정하기
        self.r1 = 10.5
        self.r2 = 10.5
        self.r3 = 7.5
        
        # agent angle info >> 초기 상태는 servo motor값 받고 추정 -> 일단은 값 넣기
        self.theta1 = 0
        self.theta2 = 0
        self.theta3 = 0
        
        # xy평면에서 본 pos (y, x) 각각에는 실수값들이 있음.
        self.pos = self.theta2postion()
        
        # 목표지점
        self.goal = goal
        self.in_workspace() # 목표지점을 내부에 있도록 위치시킴
        
        # 상태 변수
        self.state = [self.theta1, self.theta2, self.theta3] + \
                     [self.pos[1], self.pos[0]] + \
                     [goal[1], goal[0]]
        self.state_dim = len(self.state)
        
        # 행동 변수
        self.action = [[-1,0,1] for _ in range(3)]
        ''' self.action dimension도 다시 고려해보기'''
        self.action_dim = len(self.action) # action이 세가지로 갈라져서 DQN 모델을 어떻게 만들어야 할까....
        
        
        # DQN
        self.dqn = DQN(self.state_dim, self.action_dim)
        
        
        # 강화학습 관련 파라미터들
        self.gamma = config['gamma']
        self.epsilon_decay = config['epsilon_decay']
        
    def in_workspace(self):
        
        # (y,x)
        
        # 반원 고리 내부안에 있는 값인지를 확인
        try:
            # y값이 음수면
            if self.goal[1] < 0:
                raise Exception
        except Exception as e:
            print("coordinate of y is minus.")

        # 범위 밖에 있다면 해당 theta는 그대로 유지하면서 workspace 내부의 점으로 위치시키기
        r_max = 25.5
        r_min = 5.8        
        if self.goal[0] ** 2 + self.goal[1] ** 2 < r_min ** 2:
            
            theta = m.atan2(self.goal[1], self.goal[0])
            
            self.goal[0] = m.ceil(r_min * m.sin(theta))
            self.goal[1] = m.ceil(r_min * m.cos(theta))
            
        elif self.goal[0] ** 2 + self.goal[1] ** 2 > r_max ** 2:
            
            theta = m.atan2(self.goal[1], self.goal[0])

            self.goal[0] = m.trunc(r_max * m.sin(theta))
            self.goal[1] = m.trunc(r_max * m.cos(theta))

        
        
    def reset(self):
        self.theta1 = 0
        self.theta2 = 0 
        self.theta3 = 0
        
    def get_action(self):
        # epsilon greedy
        pass
        
    
    def get_pos(self):
        return self.pos

    
    # theta의 정보로부터 end-effector의 좌표를 구함. >> kinematics
    def theta2postion(self):
        return [    self.r1 * m.sin(self.theta1 * degree2rad) +
                    self.r2 * m.sin((self.theta1 + self.theta2) * degree2rad) + 
                    self.r3 * m.sin((self.theta1 + self.theta2 + self.theta3) * degree2rad) 
                    ,
                    self.r1 * m.cos(self.theta1 * degree2rad) +
                    self.r2 * m.cos((self.theta1 + self.theta2) * degree2rad) +
                    self.r3 * m.cos((self.theta1 + self.theta2 + self.theta3) * degree2rad) ]
        
    
    
    def trans_to_ros(self):
        # 추후 python ros 파일을 따로 만드는 게 좋을 듯
        theta_list = [self.theta1, self.theta2, self.theta3]
        return theta_list
    
    
        
        
        
        