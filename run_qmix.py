from runner import Runner
from common.arguments import get_common_args, get_coma_args, get_mixer_args, get_centralv_args, get_reinforce_args, get_g2anet_args
from envs.overcook_pygame.overcook_gym_env_llm import TwoPlayerGameEnv
import wandb
from pathlib import Path
import os, sys

if __name__ == '__main__':
    args = get_common_args()
    if args.alg.find('coma') > -1:
        args = get_coma_args(args)
    elif args.alg.find('central_v') > -1:
        args = get_centralv_args(args)
    elif args.alg.find('reinforce') > -1:
        args = get_reinforce_args(args)
    else:
        args = get_mixer_args(args)  # qmix args

    if args.alg.find('g2anet') > -1:
        args = get_g2anet_args(args)

    env = TwoPlayerGameEnv(map_name=args.map, ifrender=False, print_rew_log=False,
                           rew_shaping_horizons=args.reward_shaping_horizon)

    env_info = env.get_env_info()
    args.n_actions = env_info["n_actions"]
    args.n_agents = env_info["n_agents"]
    args.state_shape = env_info["state_shape"]
    args.obs_shape = env_info["obs_shape"]
    args.episode_limit = env_info["episode_limit"]

    run_dir = Path(os.path.dirname(os.path.abspath(__file__)) + "/results") / args.map
    if not run_dir.exists():
        os.makedirs(str(run_dir))

    if args.use_wandb:
        wandb_name = f'qmix_{args.map}_{args.seed}'
        run = wandb.init(config=args,
                         project='overcooked_qmix',
                         name=wandb_name,
                         group=args.map,
                         dir=str(run_dir),
                         job_type="training",
                         reinit=True)


    runner = Runner(env, args)
    if not args.evaluate:
        runner.run(1)
    else:
        runner.evaluate()
    env.close()
    wandb.finish()
