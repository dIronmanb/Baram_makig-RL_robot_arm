import gym
import robot_arm_gym.robot_arm_gym 
# from robot_arm_gym.robot_arm_gym.envs.plannar_robot_arm import robot_arm_env


# 이걸로 env 환경 실행
# env = gym.make("RobotArmEnv-v0")












# Quick Test
if __name__ == "__main__":
    env = gym.make("RobotArmEnv-v0")
    print(env)
    
    observation = env.reset()
    print("Observation >>", observation)
    print("First State >>", env.state)
    
    print("\n")
    # 액션이 1,2,3이므로 이를 -1,0,1로 맞추어 주어야 한다.
    action = env.action_space.sample()
    
    
    # 이때 내 workspace에서 범위 밖에 있는 것들은 조절을 취해야 한다.
    for i in range(len(action)):
        if action[i] == 2:
            action[i] = -1
      
    print("Action: {}, Action_type: {}".format(action, type(action)))
        
    next_observation, reward, done, info = env.step(action)
    print("Next Observation >>", next_observation)
    print("Reward >> {}".format(reward))
    print("done >> {}".format(done))
    print("info >> {}".format(info))
    
    
    
    sum = 0
    for iter in range(500  ):
        action = env.action_space.sample()
    
        for i in range(len(action)):
            if action[i] == 2:
                action[i] = -1
                
        
        next_observation, reward, done, info = env.step(action)
        print("Iterate {}".format(iter + 1), end = "\t")
        print("action: {}".format(action))
        print("Next Observation >>", next_observation, end = '\t')
        print("Reward >> {}".format(reward))
        
        sum += reward
        # if done:
        #     observation = env.reset()
        #     print("Iterate {}".format(iter + 2), end = "\t")
        #     print("action: {}".format(action))
        #     print("Next Observation >>", next_observation, end = '\t')
        #     print("Reward >> {}".format(reward))

print("Sum >>", sum)