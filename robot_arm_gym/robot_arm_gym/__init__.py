from gym.envs.registration import register

register(
    id = 'RobotArmEnvV0',
    entry_point = "robot_arm_gym.robot_arm_gym.envs.plannar_robot_arm:RobotArmEnvV0",
    
)

# register(
#     id = 'RobotArm-v0',
#     entry_points = 'robot_arm_gym.robot_arm_gym.fqw', #robot_arm_env',
# )

# register(
#     id = 'RobotArm-v1',
#     entry_point = 'robot_arm_gym.robot_arm_gym.d', #:RobotArm',
# )


# 내 class 이름은 RobotArmEnvV0 이고
# *** folder에 그걸 넣기를 원한다.
# robot_arm_gym/robot_arm_gym/envs/plannar_robot_arm



"""
    register()함수는 ID와 dictionary type의 kwargs parameter를 받아 
    EnvRegister.register()를 그대로 전달
    
    "
    Register an environment with gym. The `id` parameter corresponds to the name of the environment,
    with the syntax as follows:
    `(namespace)/(env_name)-v(version)`
    where `namespace` is optional.
    It takes arbitrary keyword arguments, which are passed to the `EnvSpec` constructor.
    "
    
    
    * register() 함수는 id와 dictionary type의 kwargs parameter를 받아 EnvRegistry.register()로 그대로 전달함.
     https://github.com/openai/gym/blob/master/gym/envs/registration.py#L157
     
        registry = EnvRegistry()     
        def register(id, **kwargs):
           return registry.register(id, **kwargs)

   * 여기선, 아래 parameter들이 EnvRegistry()로 전달됨
      id='SuperMarioBros-1-1-v0', 
      kwargs={'entry_point':'gym.envs.ppaquette_gym_super_mario:MetaSuperMarioBrosEnv']

   * 이 값들은 그대로 EnvRegistry의 env_specs dictionary로 저장되며, 
     이때, id, kwargs 값으로 EnvSpec()이 생성되어 env_specs에 저장됨
     https://github.com/openai/gym/blob/master/gym/envs/registration.py#L152
        def register(self, id, **kwargs):
           if id in self.env_specs:
              raise error.Error('Cannot re-register id: {}'.format(id))    
           self.env_specs[id] = EnvSpec(id, **kwargs)

   * EnvSpec()은 아래 값들을 parameter로 받음
     https://github.com/openai/gym/blob/master/gym/envs/registration.py#L39
         id (str) : environment id, 여기선 'SuperMarioBros-1-1-v0' 임
         entry_point (str?) : environment class의 entrypoint, module.name:Class 형식임
                                  여기선, gym.envs.ppaquette_gym_super_mario:MetaSuperMarioBrosEnv에 해당함.
         trials (int) : the number of trials to average reward over => default=100
         reward_threshold (int?) : the reward threshold before the task is considered solved, \
                                         => default=None
         local_only (bool) : environment가 local machine인 경우 True => default=False
         kwargs (dict) : the kwargs to pass to the environment class, => default=None
         nondeterministic (bool) : whether this environment is non-deterministic even after seeding \
                                          => default=False
         tag (dict[str:nay]) : ? => default=None
         max_episode_steps (?) : ? => default=None
         max_episode_seconds (?) : ? => default=None
         timestep_limit (?) : ? => default=None


env = gym.make('SuperMarioBros-1-1-v0')

        * print(type(gym)) 한 결과, "<class 'module'> 임
        * python에서 module은 ~.py 파일을 의미함. https://docs.python.org/3/tutorial/modules.html
        * gym.py가 있는가? 있다면, 그 안에 make() 함수가 있는가?
    
"""