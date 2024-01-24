from gym.envs.registration import register
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

# register(
#     id='Overcooked_pygame_veryeasy-v0',
#     # entry_point="overcook_gym:make_env",
#     entry_point="overcook_pygame.overcook_gym_env_llm.py:TwoPlayerGameEnv",
# )
#
# register(
#     id='Overcooked_pygame_supereasy-v0',
#     # entry_point="overcook_gym:make_env",
#     entry_point="overcook_pygame.overcook_gym_env_two_players_llm_supereasy:TwoPlayerGameEnv",
# )
#
# register(
#     id='Overcooked_pygame-v4',
#     # entry_point="overcook_gym:make_env",
#     entry_point="overcook_pygame.overcook_gym_env_four_players:FourPlayerGameEnv",
# )

register(
    id='Overcooked_pygame-zhenghe-v2',
    # entry_point="overcook_gym:make_env",
    entry_point="overcook_pygame.overcook_gym_env_llm:TwoPlayerGameEnv",
)