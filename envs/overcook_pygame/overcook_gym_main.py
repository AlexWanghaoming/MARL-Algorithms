import pygame
import os, sys
from pygame.transform import scale as picscale
from pygame.image import load as picload
from overcook_gym_class import *
import json

globalscale = 5
oneblock = 16 * globalscale
ONEBLOCKSIZE = (oneblock, oneblock)
DISHSIZE = (0.75 * oneblock, 0.75 * oneblock)
ITEMSIZE = (oneblock / 2, oneblock / 2)
TASK_FINISH_EVENT = pygame.USEREVENT + 1

source = '/alpha/MARL-Algorithms/envs/'
RECIPE = {
    frozenset(['AClemon', 'cookedfish']): 'AClemoncookedfish',
    frozenset(['ACtomatohamburger', 'cookedbeef']): 'ACtomatocookedbeefhamburger',
    frozenset(['ACtomato', 'cookedbeefhamburger']): 'ACtomatocookedbeefhamburger',
    frozenset(['cookedbeef', 'hamburger']): 'cookedbeefhamburger',
    frozenset(['ACtomato', 'hamburger']): 'ACtomatohamburger',
}

with open(source + 'overcook_pygame/maps.json', 'r', encoding='utf-8') as file:
    maps = json.load(file)


class MainGame(object):
    def __init__(self, map_name, ifrender=True):

        LINES = maps[map_name]['layout']

        TASK_MENU = maps[map_name]['task']
        TASKNUM = maps[map_name]['tasknum']
        PLAYERNUM = maps[map_name]['players']
        # 定义主函数#替换成类方法，方便后续更新

        # 初始化pygame
        self.done = False
        self.NOWCOIN = 100
        pygame.init()
        # pygame.mixer.music.load('overcook_pygame/music/background.mp3')
        # pygame.mixer.music.set_volume(0.2)
        # pygame.mixer.music.play()

        """
        X: 桌子， F：生鱼供应处，B：生牛肉供应处，H：汉堡包供应处，M：番茄供应处，D：盘子供应处，L：柠檬供应处，
        T：垃圾桶，E：送菜口，C：锅，U：案板
        """

        lines = LINES
        window_width = oneblock * (len(lines[0]) + 2)
        window_height = oneblock * (len(lines) + 1)
        if ifrender:
            self.window = pygame.display.set_mode((window_width, window_height))
            pygame.display.set_caption('双人游戏')
        else:
            self.window = pygame.display.set_mode((window_width, window_height), pygame.HIDDEN)

        # 设置窗口大小和标题

        picplayerlist = [{
            '[0, 1]_': picscale(picload(source + f'overcook_pygame/assets/chef{i}/f1.png').convert_alpha(),
                                ONEBLOCKSIZE),
            '[-1, 0]_': picscale(picload(source + f'overcook_pygame/assets/chef{i}/l1.png').convert_alpha(),
                                 ONEBLOCKSIZE),
            '[1, 0]_': picscale(picload(source + f'overcook_pygame/assets/chef{i}/r1.png').convert_alpha(),
                                ONEBLOCKSIZE),
            '[0, -1]_': picscale(picload(source + f'overcook_pygame/assets/chef{i}/b1.png').convert_alpha(),
                                 ONEBLOCKSIZE),
            '[0, 1]': picscale(picload(source + f'overcook_pygame/assets/chef{i}/f0.png').convert_alpha(),
                               ONEBLOCKSIZE),
            '[-1, 0]': picscale(picload(source + f'overcook_pygame/assets/chef{i}/l0.png').convert_alpha(),
                                ONEBLOCKSIZE),
            '[1, 0]': picscale(picload(source + f'overcook_pygame/assets/chef{i}/r0.png').convert_alpha(),
                               ONEBLOCKSIZE),
            '[0, -1]': picscale(picload(source + f'overcook_pygame/assets/chef{i}/b0.png').convert_alpha(),
                                ONEBLOCKSIZE),
        } for i in range(1, PLAYERNUM + 1)]
        itempicslist = ['dish', 'BClemon', 'AClemon', 'rawfish',
                        'AClemoncookedfish', 'cookedfish', 'pot',
                        'ACtomatocookedbeefhamburger', 'cookedbeefhamburger',
                        'hamburger', 'ACtomato', 'BCtomato', 'rawbeef', 'cookedbeef', 'ACtomatohamburger']
        itempics = {
            key: picscale(picload(source + f'overcook_pygame/assets/items/{key}.png').convert_alpha(), ONEBLOCKSIZE) for
            key in
            itempicslist}

        supplylist = ['dish', 'BClemon', 'BCtomato', 'rawfish', 'rawbeef', 'hamburger']
        supplyimg = {
            key: picscale(picload(source + f'overcook_pygame/assets/table/{key}.png').convert_alpha(), ONEBLOCKSIZE) for
            key in
            supplylist}

        # 设置时钟

        wall_1 = Wall(-20, 0, 20, window_height)
        wall_2 = Wall(0, -20, window_width, 20)
        wall_3 = Wall(window_width, 0, 20, window_height)
        wall_4 = Wall(0, window_height, window_width, 20)
        walls = pygame.sprite.Group(wall_1, wall_2, wall_3, wall_4)
        self.playergroup = []
        tables = pygame.sprite.Group()  # 需要交互的

        # 创建布局
        for i, line in enumerate(lines):
            for j, char in enumerate(line):
                x = j * oneblock
                y = (i + 1) * oneblock
                if char == 'X':
                    temp = Table(x, y, None, None, itempics)
                    tables.add(temp)
                elif char == 'F':
                    temp = supplyTable(x, y, 'rawfish', supplyimg)
                    tables.add(temp)
                elif char == 'B':
                    temp = supplyTable(x, y, 'rawbeef', supplyimg)
                    tables.add(temp)
                elif char == 'H':
                    temp = supplyTable(x, y, 'hamburger', supplyimg)
                    tables.add(temp)
                elif char == 'M':
                    temp = supplyTable(x, y, 'BCtomato', supplyimg)
                    tables.add(temp)
                elif char == 'D':
                    temp = supplyTable(x, y, 'dish', supplyimg)
                    tables.add(temp)
                elif char == 'L':
                    temp = supplyTable(x, y, 'BClemon', supplyimg)
                    tables.add(temp)
                elif char == 'T':
                    temp = trashTable(x, y)
                    tables.add(temp)
                elif char == 'E':
                    Cointable = coinTable(x, y)

                elif char == 'C':
                    self.cook = Cook(x, y, itempics)
                    tables.add(self.cook)
                elif char == 'U':
                    temp = CuttingTable(x, y, itempics)
                    tables.add(temp)
                elif char == '1':
                    self.playergroup.append(Player('a', x, y, picplayerlist[0], itempics))
                elif char == '2':
                    self.playergroup.append(Player('b', x, y, picplayerlist[1], itempics))
                elif char == '3':
                    self.playergroup.append(Player('c', x, y, picplayerlist[2], itempics))
                elif char == '4':
                    self.playergroup.append(Player('d', x, y, picplayerlist[3], itempics))

        # 创建墙体
        font = pygame.font.SysFont('arial', oneblock)
        self.font = pygame.font.SysFont('arial', 24)
        self.timercount = timerTable(window_width - oneblock, 0, font, 600)
        walls.add(tables)
        walls.add(tables, Cointable)
        self.tables = tables
        self.walls = walls
        self.num1 = DigitDisplay(oneblock / 2, oneblock / 10)
        self.num2 = DigitDisplay(oneblock / 2 + 5 * 5, oneblock / 10)
        self.num3 = DigitDisplay(oneblock / 2 + 5 * 5 * 2, oneblock / 10)
        self.num4 = DigitDisplay(oneblock / 2 + 5 * 5 * 3, oneblock / 10)
        Coin = Picshow(0, 0, source + 'overcook_pygame/assets/font/coin.png')
        self.task_sprites = pygame.sprite.Group()
        for i in range(TASKNUM):
            self.task_sprites.add(taskBoard((1.75 + 3 * i) * oneblock, 0, TASK_MENU))
        self.task_dict = {}
        for i,task in enumerate(self.task_sprites):
            self.task_dict[task] = i
        # print(self.task_dict)

        # task1 = taskBoard(1.75 * oneblock, 0,TASK_MENU)
        # task2 = taskBoard((1.75 + 3) * oneblock, 0)
        # self.task_sprites = pygame.sprite.Group(task1)
        # 创建精灵组
        self.all_sprites = pygame.sprite.Group(walls, self.num1, self.num2, self.num3,
                                               self.num4, Coin, self.task_sprites,
                                               Cointable, self.timercount)
        for i in range(PLAYERNUM):
            self.all_sprites.add(self.playergroup[i])
        self.Cointable = Cointable

        self.taskmenu = []
        for task in self.task_sprites:
            self.taskmenu.append(task.task)

    def mainloop(self):
        # step循环
        # 绘制游戏场景
        # 退出pygame
        clock = pygame.time.Clock()
        # 设置键盘检测的时间间隔
        key_check_interval = 100  # 单位：毫秒

        # 初始化上一次键盘检测的时间
        last_key_check_time = pygame.time.get_ticks()
        game_over = False
        nowtime = 0
        while not game_over:
            # 处理事件
            # 倒计时结束，结束游戏

            # 如果距离上一次键盘检测的时间已经超过指定的时间间隔
            # 更新玩家

            self.window.fill((255, 250, 205))
            self.all_sprites.draw(self.window)

            pygame.display.update()
            pygame.display.flip()

            # 控制游戏帧率
            clock.tick(1)
        pygame.quit()


if __name__ == '__main__':
    mainwindows = MainGame()
    mainwindows.mainloop()