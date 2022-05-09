import os, subprocess, time, signal
import gym
from gym import error, spaces
from gym import utils
from gym.utils import seeding

try:
    import hfo_py # Half Field Offense 
except ImportError as e:
    raise error.DependencyNotInstalled("{}. (HINT: you can install HFO dependencies with 'pip install gym[soccer].)'".format(e))

import logging
logger = logging.getLogger(__name__)

class SoccerEnv(gym.Env, utils.EzPickle):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        
        # 뷰어
        self.viewer = None
        
        # 서버 처리
        self.server_process = None
        
        # 서버 포트
        self.server_port = None
        
        # hfo_py
        self.hfo_path = hfo_py.get_hfo_path()
        
        # 환경에 대한 config
        self._configure_environment()
        
        # Half Field Offense에 대한 환경을 넘겨줌
        self.env = hfo_py.HFOEnvironment()
        
        # HFOEnvironmnet를 통한 객체로 서버를 연결.
        self.env.connectToServer(config_dir=hfo_py.get_config_path())
        
        # observation space는 Box로처리
        # (-1, 1)까지인데, 형상은 hfo_py에서의 getStateSize를 통해 얻은 형상으로!
        # 원소가 I = (a,b)인 state_size의 벡터이다.
        self.observation_space = spaces.Box(low=-1, high=1,
                                            shape=(self.env.getStateSize()))
        # Action space omits the Tackle/Catch actions, which are useful on defense
        # action space 역시 Box로 만든다.
        # gym.space에서의 Tuple를 사용하여
        # 각각의 action을ㄹ 정의한다.
        # 왜 이렇게 했을까...?????
        self.action_space = spaces.Tuple((spaces.Discrete(3),
                                          spaces.Box(low=0, high=100, shape=1),
                                          spaces.Box(low=-180, high=180, shape=1),
                                          spaces.Box(low=-180, high=180, shape=1),
                                          spaces.Box(low=0, high=100, shape=1),
                                          spaces.Box(low=-180, high=180, shape=1)))
        
        # 상태는 hfo_py의 IN_GAME으로 접근한다.
        self.status = hfo_py.IN_GAME

    def __del__(self):
        # 왜 del하는건지?????
        self.env.act(hfo_py.QUIT)
        self.env.step()
        os.kill(self.server_process.pid, signal.SIGINT)
        if self.viewer is not None:
            os.kill(self.viewer.pid, signal.SIGKILL)

    def _configure_environment(self):
        # 환경에 대한 config를 overriding함.
        """
        Provides a chance for subclasses to override this method and supply
        a different server configuration. By default, we initialize one
        offense agent against no defenders.
        """
        # start_hfo_server로 Half Field Offense 서버를 시작한다.
        self._start_hfo_server()

    # Half Field Offense 서버를 시작
    def _start_hfo_server(self, frames_per_trial=500,
                          untouched_time=100, offense_agents=1,
                          defense_agents=0, offense_npcs=0,
                          defense_npcs=0, sync_mode=True, port=6000,
                          offense_on_ball=0, fullstate=True, seed=-1,
                          ball_x_min=0.0, ball_x_max=0.2,
                          verbose=False, log_game=False,
                          log_dir="log"):
        """
        Starts the Half-Field-Offense server.
        
        frames_per_trial: Episodes end after this many steps.
                          일정 스텝 지나면 에피소드 end
                          
        untouched_time: Episodes end if the ball is untouched for this many steps.
                        볼을 만지지 않을 때 에피소드 end
                        
        offense_agents: Number of user-controlled offensive players.
                        User가 조종하는 공격수의 수
                        
        defense_agents: Number of user-controlled defenders.
                        user가 조종하는 수비수의 수
                        
        offense_npcs: Number of offensive bots.
                      NPC가 다루는 공격수의 수
                      
        defense_npcs: Number of defense bots.
                      NPC가 다루는 수비수의 수
                      
        sync_mode: Disabling sync mode runs server in real time (SLOW!).
                   실시간으로 sync mode가 server를 돌리는 걸 disable
                   
        port: Port to start the server on.
              server가 작동되는 포트 번호
        
        offense_on_ball: Player to give the ball to at beginning of episode.
                         에피소드 시작 시 공을 가지는 공격수
        
        fullstate: Enable noise-free perception.
                   noise-freed preception????
        
        seed: Seed the starting positions of the players and ball.
              선수들의 위치와 공의 위치를 Seed
        
        ball_x_[min/max]: Initialize the ball this far downfield: [0,1]
                          ball의 downfield를 초기화....???
        
        verbose: Verbose server messages.
                 server meessage를 설명한다.
        
        log_game: Enable game logging. Logs can be used for replay + visualization.
                  game log 파일 활성화, replay와 시각화 가능
        
        log_dir: Directory to place game logs (*.rcg).
                 log 파일이 담길 디렉토리 파일 위치
        
        """
        
        self.server_port = port # 포트 번호 설정
        
        # cmd에 다음과 같이 띄우면 된다!
        cmd = self.hfo_path + \
              " --headless --frames-per-trial %i --untouched-time %i --offense-agents %i"\
              " --defense-agents %i --offense-npcs %i --defense-npcs %i"\
              " --port %i --offense-on-ball %i --seed %i --ball-x-min %f"\
              " --ball-x-max %f --log-dir %s"\
              % (frames_per_trial, untouched_time, offense_agents,
                 defense_agents, offense_npcs, defense_npcs, port,
                 offense_on_ball, seed, ball_x_min, ball_x_max,
                 log_dir)
        
        # sync_mode, fullstate, verbose, log_game은 option으로!
        if not sync_mode: cmd += " --no-sync"
        if fullstate:     cmd += " --fullstate"
        if verbose:       cmd += " --verbose"
        if not log_game:  cmd += " --no-logging"
        
        # 위와 같이 설정되었음을 print로 알리기 
        print('Starting server with command: %s' % cmd)
        
        # self.server_process에서 처리
        self.server_process = subprocess.Popen(cmd.split(' '), shell=False)
        time.sleep(10) # Wait for server to startup before connecting a player

    def _start_viewer(self):
        """
        Starts the SoccerWindow visualizer. Note the viewer may also be
        used with a *.rcg logfile to replay a game. See details at
        https://github.com/LARG/HFO/blob/master/doc/manual.pdf.
        """
        
        # self.server_port를 통해 아래와 같은 cmd 명령을 만들고,
        cmd = hfo_py.get_viewer_path() +\
              " --connect --port %d" % (self.server_port)
        # 이를 subprocess를 통해 보이도록(시각화하도록) 한다.
        self.viewer = subprocess.Popen(cmd.split(' '), shell=False)

    def _step(self, action):
        
        # 행동을 취한다.
        self._take_action(action)
        
        # hfo env의 다음 스텝을 밟는다.
        self.status = self.env.step() # 따로 action을 인자로 안넣네??
        
        # 보상을 구한다.
        reward = self._get_reward() # 따로 인자에 next_state와 action을 안 넣네??
        
        # hfo env의 환경의 상태 변수를 get한다.
        ob = self.env.getState()
        
        # episode_over즉, done은 hfo_py.IN_GAME
        # Half Field Offense내의 게임이 진행되지 않고 있다면
        # true를 반환한다.
        episode_over = self.status != hfo_py.IN_GAME
        
        # 그렇게 ob, reward, episode_over, {}를 반환
        # {}엔 info가 담겨질 것이다.
        return ob, reward, episode_over, {}

    def _take_action(self, action):
        
        """ Converts the action space into an HFO action. """
        # Action을 HFO 내에서의 aciton으로 바꿔줄 필요가 있다.
        
        # action이 어떻게 생겼는지는 모르겠지만....
        # action[0]에는 0 ~ 4의 값을 가질 것이다.
        
        action_type = ACTION_LOOKUP[action[0]]
        
        # action[0]에서 0 ~ 4의 값에서 해당되는 hfo_py.xx와 같다면
        # 이하 구문을 실행한다.
        # 현재로서는 DASH, TURN, KICK이 있다.
        # 그에 따라 action[index]의 index도 다르다.
        if action_type == hfo_py.DASH:
            self.env.act(action_type, action[1], action[2])
        
        elif action_type == hfo_py.TURN:
            self.env.act(action_type, action[3])
        
        elif action_type == hfo_py.KICK:
            self.env.act(action_type, action[4], action[5])
        
        else:
            print('Unrecognized action %d' % action_type)
            self.env.act(hfo_py.NOOP)


    def _get_reward(self):
        # 흐음... 걍 GOAL을 넣으면 return 1를 반환
        # 그때까지 아무것도 안함
        """ Reward is given for scoring a goal. """
        if self.status == hfo_py.GOAL:
            return 1
        else:
            return 0

    def _reset(self):
        
        """ Repeats NO-OP action until a new episode begins. """
        # 게임 중이라면
        while self.status == hfo_py.IN_GAME:
            # 아무것도 하지 않게 하여
            self.env.act(hfo_py.NOOP)
            # 매 스텝을 밟게 하여 IN_GAME이 False가 되도록 만들기
            self.status = self.env.step()
        
        # IN_GAME이 False면
        while self.status != hfo_py.IN_GAME:
            
            # 아무것도 하지 않게 하여
            self.env.act(hfo_py.NOOP)
            
            # 매 스텝을 증가시켜 IN_GAME을 True로 만든다.
            # 즉, 위에서 이미 게임 종료에서 다시 시작하는 것이므로
            # while문을 썼으나 사실상 한 step만 밟으면 된다.
            self.status = self.env.step()
            
        # 그렇게 env의 state를 가져온다.
        return self.env.getState()


    def _render(self, mode='human', close=False):
        # render()....????
        
        """ Viewer only supports human mode currently. """
        
        if close: # 창 닫고, 싶으면 close == True이면
            if self.viewer is not None: # viewer에 뭔가 있다면
                os.kill(self.viewer.pid, signal.SIGKILL) # os 꺼버려
        else: # 그게 아니라면
            if self.viewer is None: # viewer에 아무거도 없다면
                self._start_viewer() # viewer 시작하기, 창 끄지 말기

ACTION_LOOKUP = {
    0 : hfo_py.DASH,
    1 : hfo_py.TURN,
    2 : hfo_py.KICK,
    3 : hfo_py.TACKLE, # Used on defense to slide tackle the ball
    4 : hfo_py.CATCH,  # Used only by goalie to catch the ball
}