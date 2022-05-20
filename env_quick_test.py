import gym
import tkinter
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
    
    # 액션이 1,2,3이므로 이를 -1,0,1로 맞추어 주어야 한다
    action = env.action_space.sample()    
    print("Action >>", action)
    
    next_state = env.step(action)
    print("Next Observation >>", next_state)
    