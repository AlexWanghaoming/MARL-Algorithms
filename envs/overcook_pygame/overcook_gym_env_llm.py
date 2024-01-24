import numpy as np
import gym
import pygame
import os, sys
import json

from numpy import ndarray

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from collections import defaultdict
from overcook_gym_main import MainGame

from overcook_gym_class import digitize, Table
from typing import Union, Dict, Tuple, List, Optional, Any

globalscale = 5
oneblock = 16 * globalscale
ONEBLOCKSIZE = (oneblock, oneblock)
DISHSIZE = (0.75 * oneblock, 0.75 * oneblock)
ITEMSIZE = (oneblock / 2, oneblock / 2)

TASK_FINISH_EVENT = pygame.USEREVENT + 1
OUT_SUPPLY_EVENT = pygame.USEREVENT + 2
OUT_DISH_EVENT = pygame.USEREVENT + 3
GET_MATERIAL_EVENT = pygame.USEREVENT + 4
GET_DISH_EVENT = pygame.USEREVENT + 5
MADE_NEWTHING_EVENT = pygame.USEREVENT + 6
BEGINCUTTING_EVENT = pygame.USEREVENT + 7
CUTTINGDOWN_EVENT = pygame.USEREVENT + 8
BEGINCOOKING_EVENT = pygame.USEREVENT + 9
COOKINGDOWN_EVENT = pygame.USEREVENT + 10
COOKINGOUT_EVENT = pygame.USEREVENT + 11
TRY_NEWTHING_EVENT = pygame.USEREVENT + 12
PUTTHING_DISH_EVENT = pygame.USEREVENT + 13
TRASH_EVENT = pygame.USEREVENT + 14

source = '/alpha/MARL-Algorithms/envs/'
with open(source + 'overcook_pygame/maps.json', 'r', encoding='utf-8') as file:
    maps = json.load(file)

## 合成菜品的得分
TASK_VALUE = {'AClemoncookedfish': defaultdict(float,{'AClemoncookedfish': 5, 'AClemon': 0, 'cookedfish': 0, 'BClemon': 0,'rawfish': 0}),
              'cookedfish': defaultdict(float, {'cookedfish': 0, 'rawfish': 0}),
              'ACtomatocookedbeefhamburger': defaultdict(float, {'ACtomatocookedbeefhamburger': 8,
                                                                 'ACtomatohamburger': 0,
                                                                 'BCtomato': 0,
                                                                 'ACtomato': 0,
                                                                 'cookedbeefhamburger': 0,
                                                                 'cookedbeef': 0,
                                                                 'rawbeef': 0,
                                                                 'hamburger': 0}),
              'cookedbeefhamburger': defaultdict(float, {'cookedbeefhamburger': 3, 'cookedbeef': 0, 'rawbeef': 0,
                                                         'hamburger': 0})}

# 为了解决前两个问题，需要新的状态，记录场上各个食材的数量，玩家lastpick的标志位
# 计算reward时考虑，如果是【当前需要的食材，且场上食材数量不够2）则reward+1】
# 通过标识位来判断用户是拿起了东西，如果这个东西是需要的则加分，不需要的减分，并且当它放下后是减分的，除非用于处理或合成
# 如果当前盘子不够则加1（可以计算离盘子距离等）
def ManhattanDis(relativepos):
    return abs(relativepos[0]) + abs(relativepos[1])

reawrd_shaping_params = {
    'pick_dish': 0,
    'out_dish': 0,  # 从仓库拿盘子
    'pick_need_material': 0,  #
    'out_need_material': 0,  # 从仓库里拿东西
    'made_newthing': 0,  # hjh合成的奖励要多一点
    'process_cutting': 0.1,  # 只要在切，就加分
    'get_need_cutting': 0.5,  # 切出有意义的东西了
    'process_cooking': 0.1,  # 只要放东西进去煮，就加分/或放进去是need的东西才加分
    'get_need_cooking': 0.5,  # 煮出有意义的东西了
    'try_new_thing': 0,  # hjh 只要去尝试合成了（手上有东西去碰另外的东西）
    'putting_dish': 0  # hjh 只要用盘子收东西，或者把做好的东西放到盘子上就给奖励
}

# 由于会有没有的东西，所以需要将字典更新成defaultdict
RECIPE = {
    frozenset(['AClemon', 'cookedfish']): 'AClemoncookedfish',
    frozenset(['ACtomatohamburger', 'cookedbeef']): 'ACtomatocookedbeefhamburger',
    frozenset(['ACtomato', 'cookedbeefhamburger']): 'ACtomatocookedbeefhamburger',
    frozenset(['cookedbeef', 'hamburger']): 'cookedbeefhamburger',
    frozenset(['ACtomato', 'hamburger']): 'ACtomatohamburger',
}


class TwoPlayerGameEnv(gym.Env):
    metadata = {'name': 'MyEnv-v0', 'render.modes': ['human']}

    # 玩家1：蓝色； 玩家2：红色
    # 玩家动作： stay：0，下：1，右：2，上：3，左：4，interact：5
    # X: 桌子， F：生鱼供应处，B：生牛肉供应处，H：汉堡包供应处，M：番茄供应处，D：盘子供应处，L：柠檬供应处，T：垃圾桶，E：送菜口，C：锅，U：案板
    def __init__(self, map_name, ifrender=True, print_rew_log=True, rew_shaping_horizons=None):
        # 初始化 pygame
        super(TwoPlayerGameEnv, self).__init__()
        self.map_name = map_name
        self.TASK_MENU = maps[map_name]['task']
        self.heatmapsize = maps[map_name]['heatmapsize']
        self.n_agents = maps[map_name]['players']
        ## 送出菜品的得分
        self.TASKNUM = maps[map_name]['tasknum']
        self.ITEMS = maps[map_name]['items']
        self.horizon = 600
        # wanghm
        # self.action_space = gym.spaces.Tuple(tuple(gym.spaces.Discrete(6) for _ in range(self.n_agents)))
        self.action_space = gym.spaces.Discrete(6)
        self.game_over = False
        self.timercount = 0  # 自定义的计时器
        self.showkey()
        self.ifrender = ifrender
        self.print_rew_log = print_rew_log
        self._initial_reward_shaping_factor = 1.0
        self.reward_shaping_factor = 1.0

        # wanghm
        # self.observation_space= gym.spaces.Tuple(tuple(self._setup_observation_space() for _ in range(self.n_agents))) # wanghm
        # self.observation_space = self._setup_observation_space()
        # self.share_observation_space = [self.observation_space, self.observation_space]
        self.obs_shape =self.dummy_reset()[0].shape[0]
        self.reset_featurize_type(obs_shape=self.obs_shape)
        # 初始化游戏
        self.initialize_game()
        self.rew_shaping_horizons = rew_shaping_horizons
        self.t = 0
        self._max_episode_steps = 600

    def get_env_info(self):
        return {'n_actions':self.action_space[0].n,
                'n_agents':self.n_agents,
                'state_shape': self.observation_space[0].shape[0] * self.n_agents,
                'obs_shape': self.observation_space[0].shape[0],
                'episode_limit': 601}

    def _gen_share_observation(self, state):
        if self.n_agents == 2:
            share_obs0 = np.concatenate([state[0], state[1]], axis=-1)
            share_obs1 = np.concatenate([state[1], state[0]], axis=-1)
            # share_obs = np.stack([share_obs0, share_obs1], axis=0)
            share_obs = np.stack(state, axis=0)
        elif self.n_agents == 4:
            share_obs0 = np.concatenate([state[0], state[1], state[2], state[3]], axis=-1)
            share_obs1 = np.concatenate([state[1], state[0], state[2], state[3]], axis=-1)
            share_obs2 = np.concatenate([state[2], state[0], state[1], state[3]], axis=-1)
            share_obs3 = np.concatenate([state[3], state[0], state[1], state[2]], axis=-1)
            # share_obs = np.stack([share_obs0, share_obs1, share_obs2, share_obs3], axis=0)
            share_obs = np.stack(state, axis=0)
        else:
            pass
        return share_obs

    def initialize_game(self):
        self.taskcount = {key: 0 for key in self.TASK_MENU}  # 用来计算送出了多少菜
        self.clock = pygame.time.Clock()
        self.game = MainGame(map_name=self.map_name, ifrender=self.ifrender)
        self.matiral_count = {key: 0 for key in self.itemdict.keys()}
        self.playitem = [self.game.playergroup[i].item for i in range(self.n_agents)]
        self.playdish = [self.game.playergroup[i].dish for i in range(self.n_agents)]

    def dummy_reset(self):
        # 重置游戏
        self.initialize_game()
        self.timercount = 0
        # self.heatmap = [np.zeros((self.heatmapsize[0], self.heatmapsize[1])) for i in
        #                 range(self.n_agents)]  # hjh，这里本来写了跟游戏一起变的，后面改吧
        # 返回初始状态
        _, _, _, _, obs, avaliable_actions = self.get_state()
        return obs

    def reset(self) -> Tuple[Tuple[np.ndarray, np.ndarray], np.ndarray, np.ndarray]:  # wanghm
        # 重置游戏
        self.initialize_game()
        self.timercount = 0
        # self.heatmap = [np.zeros((self.heatmapsize[0], self.heatmapsize[1])) for i in
        #                 range(self.n_agents)]  # hjh，这里本来写了跟游戏一起变的，后面改吧
        # 返回初始状态
        _, _, tasksequence, _, obs, available_actions = self.get_state()
        # available_actions = np.ones((self.n_agents, len(Action.ALL_ACTIONS)), dtype=np.uint8)
        share_obs = self._gen_share_observation(obs)
        self.rewards_dict = {
            "cumulative_sparse_rewards_by_agent": np.array([0.0] * self.n_agents),
            "cumulative_shaped_rewards_by_agent": np.array([0.0] * self.n_agents),
        }
        return obs, share_obs, available_actions

    def reset_featurize_type(self, obs_shape):
        # reset observation_space, share_observation_space and action_space
        self.observation_space = []
        self.share_observation_space = []
        self.action_space = []
        # self._setup_observation_space()
        high = np.ones(obs_shape) * float("inf")
        low = np.ones(obs_shape) * -float("inf")
        for i in range(self.n_agents):
            self.observation_space.append(gym.spaces.Box(np.float32(low), np.float32(high), dtype=np.float32))
            self.action_space.append(gym.spaces.Discrete(6))
            # self.share_observation_space.append(self._setup_share_observation_space(obs_shape * self.n_agents))
            self.share_observation_space.append(self._setup_share_observation_space(obs_shape))

    def _setup_share_observation_space(self, share_obs_shape):
        high = np.ones(share_obs_shape) * float("inf")
        low = np.ones(share_obs_shape) * -float("inf")
        return gym.spaces.Box(np.float32(low), np.float32(high), dtype=np.float32)

    def get_avail_agent_actions(self, agent_id):
        availaction = [0]
        player = self.game.playergroup[agent_id]#python中理论上改动这个player原先的也会变
        if player.cutting:#切菜时只有不动和交互合法
            availaction.append(5)
            avaliable_actions = [0] * 6
            for index in availaction:
                avaliable_actions[index] = 1
            return avaliable_actions
        #检测移动是否会阻塞
        tempplayergroup = []
        for j in range(self.n_agents):
            if j != agent_id:
                tempplayergroup.append(self.game.playergroup[j])
        for action in range(1,5):
            if player.availaction(action, self.game.walls, tempplayergroup):#直接调用移动函数判断是否合法,转向是合法的
                availaction.append(action)
        #检测交互是否合法（比如前面是空气，桌子上也没有菜或者任何可取的，就不合法）
        for table in self.game.tables:
            if table.availbeinter(player):
                availaction.append(5)
                break
        if self.game.Cointable.availbeinter(player):
                availaction.append(5)

        avaliable_actions = [0] * 6
        for index in availaction:
            avaliable_actions[index] = 1
        return avaliable_actions

    def step(self, action_n):
        # for i in range(self.n_agents):
        #     self.heatmap[i][self.game.playergroup[i].rect.x // 80 - 1][self.game.playergroup[i].rect.y // 80 - 2] += 1
        # print(ego_action, alt_action)
        self.timercount += 1
        for i in range(self.n_agents):
            if action_n[i] <= 4:
                tempplayergroup = []
                for j in range(self.n_agents):
                    if j != i:
                        tempplayergroup.append(self.game.playergroup[j])
                self.game.playergroup[i].update(action_n[i], self.game.walls, tempplayergroup)
            else:
                self.game.tables.update(self.game.playergroup[i], True, self.timercount)#有可能会post not finished
                self.game.Cointable.update(self.game.playergroup[i], True, self.game.taskmenu)#有可能会post success

        self.game.timercount.update(self.timercount)
        # 计算奖励和是否结束
        sparse_reward, shaped_reward, tasksequence, done, obs, available_actions  = self.get_state()
        self.t += 1  # 训练总时间

        if self.rew_shaping_horizons:
            reward = sparse_reward + shaped_reward * self.reward_shaping_factor
        else:
            reward = sparse_reward + shaped_reward

        if self.ifrender:
            self.render()

        infos = {'shaped_r': shaped_reward, 'sparse_r': sparse_reward, 'tasksequence': tasksequence}
        self._update_reward_dict(infos)
        if done:  # wanghm: 每个episode结束后绘制 玩家轨迹热图 和 交互动作点图
            infos["episode"] = {
                "ep_game_stats": self.rewards_dict,
                "ep_sparse_r": sum(self.rewards_dict["cumulative_sparse_rewards_by_agent"]),
                "ep_shaped_r": sum(self.rewards_dict["cumulative_shaped_rewards_by_agent"]),
                "ep_sparse_r_by_agent": self.rewards_dict["cumulative_sparse_rewards_by_agent"],
                "ep_shaped_r_by_agent": self.rewards_dict["cumulative_shaped_rewards_by_agent"],
                "ep_length": self.timercount
            }

        # available_actions = np.ones((self.n_agents, len(Action.ALL_ACTIONS)), dtype=np.uint8)
        share_obs = self._gen_share_observation(obs)
        # done = [done] * self.n_agents
        # reward = [[reward]] * self.n_agents
        # 返回新的状态、奖励、是否结束和其他信息
        return obs, share_obs, reward, done, infos, available_actions

    def _update_reward_dict(self, infos):
        self.rewards_dict["cumulative_sparse_rewards_by_agent"] += np.array(infos["sparse_r"])
        self.rewards_dict["cumulative_shaped_rewards_by_agent"] += np.array(infos["shaped_r"])

    def anneal_reward_shaping_factor(self, timesteps):
        """
        Set the current reward shaping factor such that we anneal linearly until self.reward_shaping_horizon
        timesteps, given that we are currently at timestep "timesteps"
        """
        new_factor = self._anneal(self._initial_reward_shaping_factor, timesteps, self.rew_shaping_horizons)
        self.reward_shaping_factor = new_factor

    def _anneal(self, start_v, curr_t, end_t, end_v=0, start_t=0):
        if end_t == 0:
            # No annealing if horizon is zero
            return start_v
        else:
            off_t = curr_t - start_t
            # Calculate the new value based on linear annealing formula
            fraction = max(1 - float(off_t) / (end_t - start_t), 0)
            return fraction * start_v + (1 - fraction) * end_v

    def pick_random_state_or_goal(self):  # 返回一个随机的合理的状态
        pass

    def showkey(self):
        # 将各种状态转换为onehot的字典
        self.directiondict = {'[0, 1]': 0, '[1, 0]': 1, '[-1, 0]': 2, '[0, -1]': 3}

        # 可以让环境反馈一个itempiclist，就不用自己设定了
        # itempicslist = self.showitemlist()
        itempicslist = self.ITEMS
        self.itemlist = itempicslist
        '''
        itempicslist = ['dish', 'BClemon', 'AClemon', 'rawfish',
                        'AClemoncookedfish', 'cookedfish', 'pot',
                        'ACtomatocookedbeefhamburger', 'cookedbeefhamburger',
                        'hamburger', 'ACtomato', 'BCtomato', 'rawbeef', 'cookedbeef', "ACtomatohamburger"]
        '''
        self.itemdict = {char: index + 1 for index, char in enumerate(itempicslist)}
        self.taskdict = {char: index for index, char in enumerate(self.TASK_MENU)}
        # self.taskscore ={'AClemoncookedfish':3,'cookedfish':2,
        #      'ACtomatocookedbeefhamburger':5,'cookedbeefhamburger':2}
        self.taskscore = self.TASK_MENU

    def _calculate_rew(self):
        tasksequence = []

        # 计算奖励和是否游戏结束
        finished_count = 0
        sparse_reward = 0.0
        shaped_reward = 0.0

        self.game.task_sprites.update(self.timercount)
        taskfinished = [False for _ in range(len(self.game.task_sprites))]  # 当前这个时间步，有没有任务被完成了
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                if event.action == "countdown_finished":
                    self.game_over = True

                elif event.action == "notfinished":
                    # 如果不同，代表已经经过前面的事件更新了，那此时我不用更新了
                    if self.game.taskmenu[self.game.task_dict[event.taskclass]] != event.oldtask:
                        print("任务冲突，以新任务为准,这条不应该会出现")
                    else:
                        self.game.NOWCOIN -= 1
                        self.game.taskmenu[self.game.task_dict[event.taskclass]] = event.newtask

                        tasksequence.append("Failed to complete required food within the time")
                    # print("未能在任务时间内完成菜品制作")
                    # reward-=10
            elif event.type == TASK_FINISH_EVENT:  # hjh这里是任务完成的奖励
                self.game.NOWCOIN += self.TASK_MENU[event.action]
                finished_count += self.TASK_MENU[event.action]
                self.taskcount[event.action] += 1  # 用于展示任务完成次数
                sparse_reward += self.TASK_MENU[event.action]
                tasksequence.append("Successfully delivered the required food")
                # print("成功送出菜品！")
                named_tasks = []
                for task in self.game.task_sprites:
                    if task.task == event.action:  # 优先筛检剩余时间少的任务
                        named_tasks.append(task)  # 有可能为空，为空是因为前面倒计时重新更新了
                if named_tasks:
                    min_task = min(named_tasks, key=lambda task: task.remaining_time)
                    min_task.newtask(self.timercount)
                    self.game.taskmenu[self.game.task_dict[min_task]] = min_task.task
                    # taskfinished[self.game.task_dict[min_task]]=True#对应的任务被完成了，此时对应的task被更新了一次
                else:
                    self.game.NOWCOIN += 1  # 代表之前倒计时重新了
            elif event.type == OUT_SUPPLY_EVENT:
                self.matiral_count[event.item] += 1
                if self.matiral_count[event.item] <= 2:
                    for task in self.game.task_sprites:
                        # if event.item in task.task:
                        if event.item in TASK_VALUE[task.task]:
                            shaped_reward += reawrd_shaping_params['out_need_material']
                            # self.get_reward_counts['out_need_material']+=1
                            tasksequence.append("Take out the required materials from the supplys")
                            if self.print_rew_log:
                                print("从仓库中拿到东西")

            elif event.type == OUT_DISH_EVENT:
                self.matiral_count['dish'] += 1
                if self.matiral_count['dish'] <= 2:
                    shaped_reward += reawrd_shaping_params['out_dish']
                    tasksequence.append("Take out the dish from the supplys")
                    if self.print_rew_log:
                        print("从仓库中拿到盘子")
                    # self.get_reward_counts['out_dish']+=1

            elif event.type == GET_MATERIAL_EVENT:
                # 如果拿到手里的东西对比原来是更需要的，那么加分，否则扣分
                for task in self.game.task_sprites:
                    if TASK_VALUE[task.task][event.newitem] > TASK_VALUE[task.task][event.olditem]:
                        shaped_reward += reawrd_shaping_params['pick_need_material']
                        tasksequence.append("Exchange a thing more meaningful for the tasks")
                        if self.print_rew_log:
                            print("换过来的东西是更有价值的")
                        # self.get_reward_counts['pick_need_material']+=1
                    # else:
                    #     reward -=reawrd_shaping_params['pick_need_material']
                    #     print("未能从仓库中拿到菜品制作所需要的材料")
                    #     self.get_reward_counts['pick_need_material']-=1
            elif event.type == TRY_NEWTHING_EVENT:
                shaped_reward += reawrd_shaping_params['try_new_thing']
                # self.get_reward_counts['try_new_thing']+=1
                tasksequence.append("Trying to synthesize new things")
                if self.print_rew_log:
                    print("尝试合成")
            elif event.type == MADE_NEWTHING_EVENT:
                # 如果合成的是当前需要的任务的东西,则加分
                tempreward = 0
                for task in self.game.task_sprites:
                    tempreward += TASK_VALUE[task.task][event.newitem]

                # if tempreward==0:
                #     shaped_reward-=reawrd_shaping_params['made_newthing'] # 合成了废品 会扣分
                #     if self.print_rew_log:
                #         print("合成了废品")
                # #     self.get_reward_counts['made_newthing']-=1
                # else:
                shaped_reward += tempreward
                tasksequence.append(f"Synthesized a {event.newitem}")
                # if self.print_rew_log:
                # print(f"合成了{event.newitem}，获得奖励{tempreward}")

            elif event.type == BEGINCUTTING_EVENT:
                shaped_reward += reawrd_shaping_params['process_cutting']
                tasksequence.append(f"begin cutting up material")
                if self.print_rew_log:
                    print("正在切菜")

            elif event.type == CUTTINGDOWN_EVENT:
                for task in self.game.task_sprites:
                    if event.item in task.task:
                        shaped_reward += reawrd_shaping_params['get_need_cutting']
                        tasksequence.append(f"cut the {event.item} completely")
                        # if self.print_rew_log:
                        # print(f"把{event.item}切好了，奖励{shaped_reward}")

            elif event.type == BEGINCOOKING_EVENT:
                shaped_reward += reawrd_shaping_params['process_cooking']
                tasksequence.append(f"begin cooking")
                if self.print_rew_log:
                    print("正在煮菜")

            elif event.type == COOKINGDOWN_EVENT:
                for task in self.game.task_sprites:
                    if event.item in task.task:
                        shaped_reward += reawrd_shaping_params['get_need_cooking']
                        tasksequence.append(f"cook up the required material{event.item}")
                        # if self.print_rew_log:
                        # print(f"把{event.item}煮好了，奖励{shaped_reward}")
            # elif event.type == COOKINGOUT_EVENT:
            #     if 'raw' in event.item:
            #         reward-=10
            #     else:
            #         for task in self.game.task_sprites:
            #             reward+=TASK_VALUE[task.task][event.item]

            elif event.type == PUTTHING_DISH_EVENT:
                if 'raw' or 'BC' in event.item:
                    tasksequence.append("Carrying unprocessed products on a plate")
                    if self.print_rew_log:
                        print('用盘子端未加工品')
                    shaped_reward -= reawrd_shaping_params['putting_dish']
                else:
                    for task in self.game.task_sprites:
                        if event.item in TASK_VALUE[task.task]:
                            tasksequence.append("Carrying required processed products on a plate")
                            if self.print_rew_log:
                                print('端到的东西是加工过的')
                            shaped_reward += reawrd_shaping_params['putting_dish']

            elif event.type == TRASH_EVENT:
                for task in self.game.task_sprites:
                    if event.item in TASK_VALUE[task.task].keys():  # wanghm
                        tasksequence.append("Pour something into the trash can")
                        # if TASK_VALUE[task.task][event.item] >=3:
                        #     if self.print_rew_log:
                        #     print(f"倒掉了{event.item},得到负奖励-1")

                        # 这里如果考虑如果把第二级的合成品放进去（如牛肉番茄汉堡）有马上要合成的牛肉汉堡，把这种东西倒掉就很可惜，就扣分。先不考虑为场上空出来位置这种、因为要计算的量太大了
                        # shaped_reward -= 1
                        break

            th, hu, te, on = digitize(self.game.NOWCOIN)
            self.game.num1.set_num(th)
            self.game.num2.set_num(hu)
            self.game.num3.set_num(te)
            self.game.num4.set_num(on)

        return sparse_reward, shaped_reward, tasksequence

    def get_state(self):

        sparse_r, shaped_r, tasksequence = self._calculate_rew()

        players = self.game.playergroup
        playab_tables = [[] for i in range(self.n_agents)]  # 所有可交互物的位置
        playab_cointables = [[] for i in range(self.n_agents)]  # cointable的位置，不需要（最近）因为coin只会有一个

        playab_closet_item_pos = [[10e9] * (len(self.itemdict)) * 2 for i in range(self.n_agents)]  # 所有最近物品的位置
        playab_closet_empty_table_pos = [[10e9, 10e9] for i in range(self.n_agents)]  # 最近的空桌子

        emptypalcenum = 0  # 空桌子的数量
        avaliable_actions = []
        for i, player in enumerate(players):
            playab_cointables[i] = [player.rect.x - self.game.Cointable.rect.x,
                                    player.rect.y - self.game.Cointable.rect.y]
            # 计算一下收银台的位置
            if player.item:
                itemindex = (self.itemdict[player.item] - 1) * 2
                playab_closet_item_pos[i][itemindex:itemindex + 2] = [0, 0]
            elif player.dish:
                dishindex = (self.itemdict[player.dish] - 1) * 2
                playab_closet_item_pos[i][dishindex:dishindex + 2] = [0, 0]
            avaliable_actions.append(self.get_avail_agent_actions(i))

        tablenum = 0
        for temp in self.game.tables:  # 目前的tables中不包含trash和coin
            if temp.item:
                # supply的item属性也被改了，现在所有tables都有item属性，如果true说明有这个东西，需要计算最近距离
                # 在别的玩家身上还要算
                for i, player in enumerate(players):
                    itemindex = (self.itemdict[temp.item] - 1) * 2  # 如番茄的存储位置
                    temppos = [player.rect.x - temp.rect.x, player.rect.y - temp.rect.y]  # 如玩家a到番茄的桌子的距离

                    if ManhattanDis(temppos) < ManhattanDis(playab_closet_item_pos[i][itemindex:itemindex + 2]):
                        playab_closet_item_pos[i][itemindex:itemindex + 2] = temppos

            if isinstance(temp, Table):
                if temp.dish:  # 在考虑dish距离，和上一段是一致的，只是dish单独有个属性
                    for i, player in enumerate(players):
                        dishindex = (self.itemdict[temp.dish] - 1) * 2
                        temppos = [player.rect.x - temp.rect.x, player.rect.y - temp.rect.y]
                        if ManhattanDis(temppos) < ManhattanDis(playab_closet_item_pos[i][dishindex:dishindex + 2]):
                            playab_closet_item_pos[i][dishindex:dishindex + 2] = temppos
                if not temp.item:
                    emptypalcenum += 1
                    # 空桌子就计算一下最近的空桌子
                    for i, player in enumerate(players):
                        temppos = [player.rect.x - temp.rect.x, player.rect.y - temp.rect.y]
                        if ManhattanDis(temppos) < ManhattanDis(playab_closet_empty_table_pos[i][0:2]):
                            playab_closet_empty_table_pos[i][0:2] = temppos
                continue
            for i, player in enumerate(players):
                tablenum += 1
                playab_tables[i] += [player.rect.x - temp.rect.x, player.rect.y - temp.rect.y]
        # print(tablenum)
        # print(list(self.game.tables))
        # print(len(self.game.tables))
        # print("*"*10)
        for i, player in enumerate(players):
            if playab_closet_empty_table_pos[i][0] > 100000:  # 没有空桌子了
                playab_closet_empty_table_pos[i] = [0, 0]
            for j in range(len(playab_closet_item_pos[i])):  # 如果没有找到这个物品说明还没出现，也赋值0
                if playab_closet_item_pos[i][j] > 100000:
                    playab_closet_item_pos[i][j] = 0
        collide = [[] for i in range(self.n_agents)]
        # 计算人物面前有无桌子等无法通过的东西，因为用了tables，后期计算量上可以优化
        rect_sprite = pygame.sprite.Sprite()
        for i, player in enumerate(players):
            rect_sprite.rect = player.rect.move(player.direction[0] * oneblock / 2,
                                                player.direction[1] * oneblock / 2)
            collide[i] = int(bool(pygame.sprite.spritecollide(rect_sprite, self.game.tables, False)))

        tasks = []
        tasktime = []
        nowtime = self.timercount
        for task in self.game.task_sprites:
            tasks.append(task)
            tasktime.append((task.timer - (nowtime - task.start_time)))

        remaintime = (self.game.timercount.timer - nowtime)
        if self.game.cook.item and 'raw' in self.game.cook.item:
            iscook = 1
        else:
            iscook = 0

        taskreward = list(map(lambda x: self.taskscore[x.task], tasks))
        current_goal = list(map(lambda x: (np.eye(len(self.taskdict) + 1)[self.taskdict[x.task]]).tolist(), tasks))  # 这里为什么+1

        # TODO
        # 增加最近的空桌子，最近的几个操作台，最近的所有物资，如果在手上，则(0,0)
        # 如果这个环境中不会出现这个物资，该怎么办？不加，或者还没产生，怎么赋值？(0,0)

        """
        编码player i 的特征如下：
        【玩家i的特征，其他玩家的特征，玩家i和同伴的相对距离，玩家i的绝对位置】（维度：54）
        玩家i的特征 （维度：25）：
            玩家朝向：长度为4的one-hot编码
            玩家持有物品：长度为6的one-hot编码
            玩家是否在切菜
            玩家当前方向有无可交互墙壁（桌子等）
            玩家和每一个有功能的桌子的相对距离
            玩家和收银台的相对距离
            玩家和最近的物品的相对距离，按目前的地图是6个物品，也就是12维度的相对距
            玩家和最近的空桌子的相对距离

        # TODO 
        玩家i和同伴的相对距离：（dx, dy）
        玩家i的绝对位置：（x,y）

        # task：当前的总时间，当前的分数，当前有无烧菜，当前桌子上有多少空位，当前所有任务的剩余时间，当前的任务目标分数，当前目标名称等等。
        """
        player_pos = []
        player_dis2other = []
        player_feature = []

        for i, player in enumerate(players):
            player_pos.append(np.array([player.rect.x // 80, player.rect.y // 80]))
            tempplayergroup = []
            tempdis = []
            for j in range(self.n_agents):
                # tempdis = []
                if j != i:
                    tempdis += [(players[i].rect.x - self.game.playergroup[j].rect.x) // 80,
                                (players[i].rect.y - self.game.playergroup[j].rect.y) // 80]
            player_dis2other.append(np.array(tempdis))
            # try:
            #     sss = np.eye(len(self.itemdict)+1)[self.itemdict[player.item] if player.item else 0]
            # except IndexError:
            #     print('ssss')
            player_feature.append(
                np.array(np.eye(len(self.directiondict))[self.directiondict[str(player.direction)]].tolist() +
                         np.eye(len(self.itemdict) + 1)[self.itemdict[player.item] if player.item else 0].tolist() +
                         # [int(player.cutting)] +
                         [collide[i]] +
                         [dis // 80 for dis in playab_tables[i]] +  # 这个会变多
                         [dis // 80 for dis in playab_cointables[i]] +
                         [dis // 80 for dis in playab_closet_item_pos[i]] +
                         [dis // 80 for dis in playab_closet_empty_table_pos[i]]
                         ))
        # 当前需要作的task
        flatencurrent_goal = []
        for taskonehot in current_goal:
            flatencurrent_goal += taskonehot
        # task = np.array([remaintime/10, self.game.NOWCOIN, iscook, emptypalcenum ] + tasktime + taskreward + flatencurrent_goal)
        task = [i / 100 for i in tasktime] + flatencurrent_goal

        # ordered_features_p0 = np.concatenate([p0_features,p1_features,task])
        # ordered_features_p1 = np.concatenate([p1_features,p0_features,task])
        # ordered_features_p0 = np.concatenate([player_feature[0], player_feature[1], player_dis2other[0], player_pos[0]])
        # ordered_features_p1 = np.concatenate([player_feature[1], player_feature[0], player_dis2other[1], player_pos[1]])
        ordered_features = [[] for i in range(self.n_agents)]
        for i in range(self.n_agents):
            ordered_features[i].append(player_feature[i])
            for j in range(self.n_agents):
                if j != i:
                    ordered_features[i].append(player_feature[j])
            ordered_features[i].append(player_dis2other[i])
            ordered_features[i].append(player_pos[i])
            ordered_features[i].append(task)  # wanghm 加上任务相关的状态特征
            ordered_features[i] = np.concatenate(ordered_features[i])
        return sparse_r, shaped_r, tasksequence, self.timercount > self.horizon, ordered_features, avaliable_actions

    def render(self, mode='human', close=False):
        # hjh 增加送菜的个数
        self.game.window.fill((255, 250, 205))
        self.game.all_sprites.draw(self.game.window)
        i = 0
        for k, v in self.taskcount.items():
            text = self.game.font.render(f"{k}:{v}", True, (0, 0, 0))
            self.game.window.blit(text, (80 * 6, 80 * 5 + 24 * i))  # 在最后一行的右下角显示
            i += 1
        # for k in range(self.n_agents):
        #     for i in range(self.heatmap[k].shape[0]):
        #         for j in range(self.heatmap[k].shape[1]):
        #             temp = self.heatmap[k][i][j] / np.max(self.heatmap[k]) * 255
        #             color = (temp, 255 - temp, 0)
        #             rect = pygame.Rect(80 * 6 + i * 20, 80 * (2 + 1.5 * k) + j * 20, 20, 20)
        #             pygame.draw.rect(self.game.window, color, rect)

        pygame.display.update()
        pygame.display.flip()

        # 控制游戏帧率：一秒跑多少timestep
        self.clock.tick(20)

    def close(self):
        # 关闭 Pygame
        pygame.quit()

    # def seed(self, seed=None):
    #     # 设置随机数生成器的种子
    #     return np.random(seed=seed)


def make_env():
    env = TwoPlayerGameEnv()
    return env

