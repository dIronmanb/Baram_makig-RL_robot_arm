from gym.envs.registration import register

register(
    id = 'robot-arm-v0',
    entry_points = 'robot_arm_gym.envs:RobotArmEnvV0',
)

register(
    id = 'robot-arm-v1',
    entry_point = 'robot_arm_gym.envs:RobotArmEnvV1',
)

