import gym
import numpy as np
import pygame
import time
import gym
import random
from envs.overcook_pygame.overcook_gym_env_llm import TwoPlayerGameEnv
"""
用于测试环境
"""


env = TwoPlayerGameEnv(map_name="2playerhard", ifrender=False, print_rew_log=False, rew_shaping_horizons=1000000)
obs = env.reset()
# print(observation)
# print(env.action_space.sample())
xx = 0
while (True):
    xx += 1
    clock = pygame.time.Clock()
    # observation, reward, done, info = env.step(env.action_space.sample())
    # obs, reward, done, info = env.multi_step(env.action_space.sample(), env.action_space.sample())
    action = (0, random.randint(0, 5))
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                action = (3, random.randint(0, 5))
            elif event.key == pygame.K_a:
                action = (4, random.randint(0, 5))
            elif event.key == pygame.K_s:
                action = (1, random.randint(0, 5))
            elif event.key == pygame.K_d:
                action = (2, random.randint(0, 5))
            elif event.key == pygame.K_SPACE:
                action = (5, random.randint(0, 5))
            else:
                action = (0, random.randint(0, 5))
    action = np.array(action).reshape(2, 1)
    obs, share_obs, reward, done, info, available_actions = env.step(action)
    if all(done):
        break
    # clock.tick(10)
    # env.render()
print(xx)
env.close()