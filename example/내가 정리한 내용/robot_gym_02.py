#!/usr/bin/env python3
import numpy as np

import gym # gym을 왜 쓰는 걸까??

from typing import Tuple

from robo_gym.utils.exceptions import InvalidStateError, RobotServerError, InvalidActionError
import robo_gym_server_modules.robot_server.client as rs_client
from robo_gym_server_modules.robot_server.grpc_msgs.python import robot_server_pb2
from robo_gym.envs.simulation_wrapper import Simulation


class ExampleEnv(gym.Env):
    """Example environment.
    Args:
        rs_address (str): Robot Server address. Formatted as 'ip:port'. Defaults to None.
  
    Attributes:
        client (:obj:str): Robot Server client.
        real_robot (bool): True if the environment is controlling a real robot.
    """
    # 이렇게 __init__에서 쓰지 않는 것들은 class 내부에서 사용이 가능하다.
    # 실제 환경에서의 로봇이 쓰일 건지의 여부
    real_robot = False
    # 한 에피소드의 최대 스텝
    max_episode_steps = 300


    def __init__(self, rs_address=None, rs_state_to_info=True, **kwargs):
        # rs_address: IP주소:Port번호
        
        # 현재 스텝
        self.elapsed_steps = 0

        # ???
        self.rs_state_to_info = rs_state_to_info

        # observation 차원수
        self.observation_space = self._get_observation_space()
        # action 차원수
        self.action_space = self._get_action_space()

        # ???
        self.rs_state = None
        
        # Connect to Robot Server
        if rs_address:
            self.client = rs_client.Client(rs_address) # 이렇게 하면 ROS server에 연결할 수 있는 듯
        else:
            print("WARNING: No IP and Port passed. Simulation will not be started")
            print("WARNING: Use this only to get environment shape")


    def _set_initial_robot_server_state(self, rs_state): # -> robot_server_pb2.State:
        # 반환 타입이 robot_server_pb2.State이라는 객체인듯
        
        
        string_params = {} # 문자열 변수
        float_params = {}  # 소수점 변수
        state = {}         # ???

        # state_msg에 state, float, string, 그리고 rs_state를 담는다.
        # 딕셔너리 rs_state엔 "pos_x", "pos_y"의 key가 있고 그에 대한 value가 있다.
        # 그럼 state_dict으로 인하여 string_params, float_params, state를 각각 채울 것이다! 
        state_msg = robot_server_pb2.State(state = state, float_params = float_params, 
                                            string_params = string_params, state_dict = rs_state)
        return state_msg

    def reset(self, position = None): # -> np.ndarray:
        # 반환 타입이 np.ndarry 객체
        
        """Environment reset.
        Args:
            position (list[2] or np.array[2]): [x,y] initial robot position.
        (번역) 인자로 list[2]나 np.array[2]를 받는다. 이는 로봇 좌표의 (x,y)를 의미한다. 
               
        Returns:
            np.array: Environment state.
        (번역) 환경의 상태를 리턴 한다 -> state???
        """
        
        # Set Robot starting position
        if position:
            # postion의 차원수가 2가 아니면: 즉, (x,y)말고 (x,y,z,w,..)이라면
            # assert error 발생하기
            assert len(position)==2, "Dimension for position must be 2 but current position length is {}".format(len(position))
            
        else:
            # position의 차원수가 2이면 (0,0)으로 reset하기
            position = [0,0]

        # 현재 step도 0으로!   (elapse: 시간이 경과하다.)    
        self.elapsed_steps = 0

        # Initialize environment state
        state_len = self.observation_space.shape[0] # 상태 변수 길이는 observation_space의 형상의 [0] ...???
        state = np.zeros(state_len) # 상태 변수 개수만큼 np.zeros 만들기 >> 현재 아무것도 안했으므로 모든 state는 영벡터
        rs_state = dict.fromkeys(self.get_robot_server_composition(), 0.0) # Robot Server의 요소들에 대해 0.0으로 설정
        

        # Fill rs_state
        rs_state['pos_x'] = position[0] # 'pos_x'엔 position[0] 즉, x좌표를
        rs_state['pos_y'] = position[1] # 'pos_y'엔 position[1] 즉, y좌표를 넣는다.

        # Set initial state of the Robot Server
        state_msg = self._set_initial_robot_server_state(rs_state) # dict타입의 rs_state를 인자로 넘겨서 state_msg 생성
        
        if not self.client.set_state_msg(state_msg): # Connected Robot server(clinet)의 set_state_msg가 아무것도 없으면 
            raise RobotServerError("set_state") # 에러 발생: "state를 설정해주세요!"

        # Get Robot Server state
        rs_state = self.client.get_state_msg().state_dict # 서버로부터 상태 변수 메시지를 dict상태로 가져온다.

        # Check if the length and keys of the Robot Server state received is correct
        self._check_rs_state_keys(rs_state) # 마치 Chksum, bit error 느낌??

        # Convert the initial state from Robot Server format to environment format
        state = self._robot_server_state_to_env_state(rs_state) # 서버 포맷의 초기 상태를 환경의 포맷으로 변경

        # Check if the environment state is contained in the observation space
        if not self.observation_space.contains(state): # 서버로부터 가져온 state를 environment의 observation에 포함되어 있는지를 판단
            raise InvalidStateError("There is no state in observation space.(def reset(self, position = None):)") # 없다면 에러 발생

        self.rs_state = rs_state # None이었던 rs_state에 서버로부터 받은 state를 담는다.

        return state # 내부적으로 사용되는 건 environment에서의 state이므로 state를 반환


    def reward(self, rs_state, action): # -> Tuple[float, bool, dict]:
        # 인자로는 rs_state, action을 준다. (rs_state는 상태, action은 행동) >> 현재는 example이므로 이를 써야할 필요가 있다!
        # 튜플(실수, 불리언, 딕셔너리)로 반환
        
        # 일단 에피소드가 안 끝났을거니까 False
        done = False
        # info는 empty dict으로
        info = {}

        # 내가 설정한 max_step를 넘기면
        if self.elapsed_steps >= self.max_episode_steps:
            # done는 True로 하여 다음 에피소드로 넘어갈 준비를 진행하기
            done = True
            # empty dict에 'final_status':'max_steps_exceeded'를 추가하기!
            info['final_status'] = 'max_steps_exceeded'
            
        # 그럼ㅎ게 0, done, info를 반환
        '''
         중요!
            아마 여기서 보상 관련 코드를 제작해야 한다.
            내가 어떻게 보상함수를 정의했는지를 여기서 구현한다.
            위 틀을 유지하면서...!
        '''
        return 0, done, info
   

    def step(self, action): # -> Tuple[np.array, float, bool, dict]:
        
        # 인자로 행동을
        # 리턴으로 튜플(np.array, float, bool, dict) ... 왜?
        
        
        # action이 list면, action을 numpy로 바꿔주기!
        if type(action) == list: action = np.array(action)
        
        # 한 step 했으니 elapsed_step을 1증가
        self.elapsed_steps += 1

        # Check if the action is contained in the action space
        if not self.action_space.contains(action): # 현재 내가 만든 environment에 action_space 안에 있는 action인지 파악하기
            raise InvalidActionError("The current action space does not include this action.") # 없으면 Error 발생


        # Send action to Robot Server and get state
        # 현재 action을 numpy로 했으니 list로 다시 바꾸어
        # Robot Server에 전송하고 해당 action을 취한 뒤의 state를 얻는다.
        # state_dict, 즉 dict의 형태로 rs_state(상태변수)에 담는다.
        rs_state = self.client.send_action_get_state(action.tolist()).state_dict
        # 상태변수가 제대로 담겼는지 파악하기
        self._check_rs_state_keys(rs_state)

        # Convert the state from Robot Server format to environment format
        # 서버로부터의 받은 state를 다시 environmnet state에 맞추어 준다.
        state = self._robot_server_state_to_env_state(rs_state)

        # Check if the environment state is contained in the observation space
        if not self.observation_space.contains(state): # 현재 바꾼 environmnet state가 obervation_space에 잘 담겼는지 파악하기.
            raise InvalidStateError("There is no state in observation space.(def step(self, action):)")

        # self.state엔 action을 취한 next state을 담는다.
        self.rs_state = rs_state

        # Assign reward
        '''
            내가 보상을 어떻게 주었는지,
            max_step을 넘어가는 것 이외에 에피소드가 끝나는 조건엔 무엇이 있는지는
            내가 만들어야 한다!
        '''
        reward = 0      # ㅇㅋ?
        done = False    # ㅇㅋ?
        reward, done, info = self.reward(rs_state=rs_state, action=action) # 여기있네, reward를 어떻게 주어야 하는지 ㅋㅋㄹㅃㅃ
        # 만약에 __init__에서 rs_state_to_info를 True로 했다면,
        # info에 'rs_state':현재 상태 값들 을 넣는다.
        # info는 정말로 걍 정보만 나타내는 애일 것이다.
        if self.rs_state_to_info: info['rs_state'] = self.rs_state 

        # 그렇게 state, reward, done, info를 반환
        return state, reward, done, info

    
    def get_rs_state(self):
        # 현재 상태를 알고 싶다면??
        # self.rs_state를 반환!
        return self.rs_state

    def render():
        # render()라....
        # render(): 어떤 상태가 되게 만들다.
        pass
    
    def get_robot_server_composition(self):# -> list:
        # 리스트로 반환
        # robot server Compsition 함수를 두어
        # rs_state, 즉 상태 변수에
        # x좌표, y좌표, 선속도, 각속도 정보를 리턴함
        rs_state_keys = [
            'pos_x',
            'pos_y',
            'lin_vel',
            'ang_vel',
        ]
        return rs_state_keys


    def _get_robot_server_state_len(self):#  -> int:
        # int형을 반환: 상태 변수 개수 반환
        """Get length of the Robot Server state.
        Describes the composition of the Robot Server state and returns
        its length.
        """
        # 내가 정의한 상태 변수들(x,y,vel,ang_vel)의 개수를 리턴
        # robot server state를 묘사함.
        return len(self.get_robot_server_composition())

    def _check_rs_state_keys(self, rs_state): # -> None:
        # 아무것도 반환하지 않음
        
        keys = self.get_robot_server_composition() # 상태변수들을 리스트로 가져옴
        
        if not len(keys) == len(rs_state.keys()): # rs_state에서의 정의한 상태변수 개수와 사맛디 아니하면
            raise InvalidStateError("Robot Server state keys to not match. Different lengths.") # 길이 다르다고 에러 띄우기
        
        for key in keys: #
            if key not in rs_state.keys(): # rs_state의 keys에 get_robot_server_composition의 key들과 다르면
                raise InvalidStateError("Robot Server state keys to not match") # key들이 서로 맞지 않다고 에러 띄우기


    def _robot_server_state_to_env_state(self, rs_state):# -> np.ndarray:
        # 결국, environment 내에서는 np.array의 형태로 RL를 처리할 것이기 때문에
        """Transform state from Robot Server to environment format.
        Args:
            rs_state (list): State in Robot Server format.
        Returns:
            numpy.array: State in environment format.
            
        """

        pos_x = rs_state['pos_x']
        pos_y = rs_state['pos_y']
        lin_vel = rs_state['lin_vel']
        ang_vel = rs_state['ang_vel']

        # Compose environment state
        state = np.array([pos_x, pos_y, lin_vel, ang_vel])

        return state


    def _get_observation_space(self): # -> gym.spaces.Box:
        # gym.space.Box()를 반환
        """Get environment observation space.
        Returns:
            gym.spaces: Gym observation space object.
        """
        
        """
        A (possibly unbounded) box in R^n. Specifically, a Box represents the
        Cartesian product of n ***closed intervals***. Each interval has the form of one
        of [a, b], (-oo, b], [a, oo), or (-oo, oo).
        
        There are two common use cases:
            * Identical bound for each dimension::
            >>> Box(low=-1.0, high=2.0, shape=(3, 4), dtype=np.float32) 
                Box(3, 4)
            
            * Independent bound for each dimension::
            >>> Box(low=np.array([-1.0, -2.0]), high=np.array([2.0, 4.0]), dtype=np.float32)
            Box(2,)
        """
        
        # Definition of environment observation_space
        # 여기서는 max와 min을 (-inf, inf)로 두었으나,
        # 실제 환경에서는 로봇의 제약으로 인하여 이 부분을 건드릴 필요는 있다...!
        max_obs = np.array([np.inf] * 4)
        min_obs = -np.array([np.inf] * 4)


        return gym.spaces.Box(low=min_obs, high=max_obs, dtype=np.float32) # 다음과 같이 만들면 Box(4,)가 만들어짐

    
    def _get_action_space(self): #-> gym.spaces.Box:
        # gym.space.Box()를 반환
        
        """Get environment action space.
        Returns:
            gym.spaces: Gym action space object.
        """
        # np.full(2, -1.0) >> array([-1, -1])
        # np.full(2,  1.0) >> array([ 1,  1])
        return gym.spaces.Box(low=np.full(2, -1.0), high=np.full(2, 1.0), dtype=np.float32)


class ExampleEnvSim(ExampleEnv, Simulation):
    # 내가 만든 Exmaple Environmnet과 Simluation을 연동하기!
    
    # roslaunch example_robot_server robot_server.launch를 ubuntu terminal에서 실행 
    cmd = "roslaunch example_robot_server robot_server.launch"
    
    
    def __init__(self, ip=None, lower_bound_port=None, upper_bound_port=None, gui=False, **kwargs):
        # launch 파일, 창 위치, GUI toolkit, ...
        Simulation.__init__(self, self.cmd, ip, lower_bound_port, upper_bound_port, gui, **kwargs)
        # 내가 만든 환경도 __init__에 포함!
        ExampleEnv.__init__(self, rs_address=self.robot_server_ip, **kwargs)

class ExampleEnvRob(ExampleEnv):
    real_robot = True

# unbuntu에 아래와 같이 terminal에 치면 rviz?가 실행될 것이다.
# roslaunch example_robot_server robot_server.launch  gui:=true real_robot:=true