import pygame
from pygame.transform import scale as picscale
from pygame.image import load as picload
from game_class import *
import random

globalscale = 5
oneblock = 16 * globalscale
ONEBLOCKSIZE = (oneblock, oneblock)
DISHSIZE = (0.75*oneblock, 0.75*oneblock)
ITEMSIZE =  (oneblock/2, oneblock/2)
TASK_FINISH_EVENT = pygame.USEREVENT + 1

TASK_MENU = {'AClemoncookedfish':3,'cookedfish':2,
             'ACtomatocookedbeefhamburger':5,'cookedbeefhamburger':2}
RECIPE = {
    frozenset(['AClemon', 'cookedfish']): 'AClemoncookedfish',
    frozenset(['ACtomatohamburger', 'cookedbeef']): 'ACtomatocookedbeefhamburger',
    frozenset(['ACtomato', 'cookedbeefhamburger']): 'ACtomatocookedbeefhamburger',
    frozenset(['cookedbeef', 'hamburger']): 'cookedbeefhamburger',
    frozenset(['ACtomato', 'hamburger']): 'ACtomatohamburger',
}

# 定义主函数#替换成类方法，方便后续更新

class MainGame(object):
    def __init__(self):
        # 初始化pygame
        self.NOWCOIN = 100
        pygame.init()
        pygame.mixer.music.load("assets/music/background.mp3")
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play()
        lines = ["____E____",
                 "XXXX_XXXX",
                 "X__C____X",
                 "X1_X2___U",
                 "X_______T",
                 "XFXHDLMBX", ]

        window_width = oneblock * len(lines[0])
        window_height = oneblock * (len(lines) + 1)
        self.window = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("多人合作烹饪游戏")
        # 设置窗口大小和标题

        picplayer1 = {
            '[0, 1]_': picscale(picload('assets/chef1/chef_front_lemon.png').convert_alpha(), ONEBLOCKSIZE),
            '[-1, 0]_': picscale(picload('assets/chef1/chef_left_lemon.png').convert_alpha(), ONEBLOCKSIZE),
            '[1, 0]_': picscale(picload('assets/chef1/chef_right_lemon.png').convert_alpha(), ONEBLOCKSIZE),
            '[0, -1]_': picscale(picload('assets/chef1/chef_back_thing.png').convert_alpha(), ONEBLOCKSIZE),
            '[0, 1]': picscale(picload('assets/chef1/chef_front_empty.png').convert_alpha(), ONEBLOCKSIZE),
            '[-1, 0]': picscale(picload('assets/chef1/chef_left_empty.png').convert_alpha(), ONEBLOCKSIZE),
            '[1, 0]': picscale(picload('assets/chef1/chef_right_empty.png').convert_alpha(), ONEBLOCKSIZE),
            '[0, -1]': picscale(picload('assets/chef1/chef_back_empty.png').convert_alpha(), ONEBLOCKSIZE),
        }
        picplayer2 = {
            '[0, 1]_': picscale(picload('assets/chef2/f1.png').convert_alpha(), ONEBLOCKSIZE),
            '[-1, 0]_': picscale(picload('assets/chef2/l1.png').convert_alpha(), ONEBLOCKSIZE),
            '[1, 0]_': picscale(picload('assets/chef2/r1.png').convert_alpha(), ONEBLOCKSIZE),
            '[0, -1]_': picscale(picload('assets/chef2/b1.png').convert_alpha(), ONEBLOCKSIZE),
            '[0, 1]': picscale(picload('assets/chef2/f0.png').convert_alpha(), ONEBLOCKSIZE),
            '[-1, 0]': picscale(picload('assets/chef2/l0.png').convert_alpha(), ONEBLOCKSIZE),
            '[1, 0]': picscale(picload('assets/chef2/r0.png').convert_alpha(), ONEBLOCKSIZE),
            '[0, -1]': picscale(picload('assets/chef2/b0.png').convert_alpha(), ONEBLOCKSIZE),
        }
        itempicslist = ['dish', 'BClemon', 'AClemon', 'rawfish',
                        'AClemoncookedfish', 'cookedfish', 'pot',
                        'ACtomatocookedbeefhamburger', 'cookedbeefhamburger',
                        'hamburger', 'ACtomato', 'BCtomato', 'rawbeef', 'cookedbeef', "ACtomatohamburger"]
        itempics = {key: picscale(picload(f'assets/items/{key}.png').convert_alpha(), ONEBLOCKSIZE) for key in
                    itempicslist}

        supplylist = ['dish', 'BClemon', 'BCtomato', 'rawfish', 'rawbeef', 'hamburger']
        supplyimg = {key: picscale(picload(f'assets/table/{key}.png').convert_alpha(), ONEBLOCKSIZE) for key in
                     supplylist}

        # 设置时钟

        wall_1 = Wall(-20, 0, 20, window_height)
        wall_2 = Wall(0, -20, window_width, 20)
        wall_3 = Wall(window_width, 0, 20, window_height)
        wall_4 = Wall(0, window_height, window_width, 20)
        walls = pygame.sprite.Group(wall_1, wall_2, wall_3, wall_4)

        tables = pygame.sprite.Group()  # 需要交互的

        # 创建布局
        for i, line in enumerate(lines):
            for j, char in enumerate(line):
                x = j * oneblock
                y = (i + 1) * oneblock
                if char == "X":
                    temp = Table(x, y, None, None, itempics)
                    tables.add(temp)
                elif char == "F":
                    temp = supplyTable(x, y, "rawfish", supplyimg)
                    tables.add(temp)
                elif char == "B":
                    temp = supplyTable(x, y, "rawbeef", supplyimg)
                    tables.add(temp)
                elif char == "H":
                    temp = supplyTable(x, y, "hamburger", supplyimg)
                    tables.add(temp)
                elif char == "M":
                    temp = supplyTable(x, y, "BCtomato", supplyimg)
                    tables.add(temp)
                elif char == "D":
                    temp = supplyTable(x, y, "dish", supplyimg)
                    tables.add(temp)
                elif char == "L":
                    temp = supplyTable(x, y, "BClemon", supplyimg)
                    tables.add(temp)
                elif char == "T":
                    temp = trashTable(x, y)
                    tables.add(temp)
                elif char == "E":
                    Cointable = coinTable(x, y)

                elif char == "C":
                    temp = Cook(x, y, itempics)
                    tables.add(temp)
                elif char == "U":
                    temp = CuttingTable(x, y, itempics)
                    tables.add(temp)
                elif char == "1":
                    self.player_a = Player(x, y, \
                                           {
                                               pygame.K_w: (0, -1),
                                               pygame.K_s: (0, 1),
                                               pygame.K_a: (-1, 0),
                                               pygame.K_d: (1, 0)}, pygame.K_SPACE, picplayer2, itempics)
                elif char == "2":
                    self.player_b = Player(x, y, \
                                           {
                                               pygame.K_UP: (0, -1),
                                               pygame.K_DOWN: (0, 1),
                                               pygame.K_LEFT: (-1, 0),
                                               pygame.K_RIGHT: (1, 0)}, pygame.K_RSHIFT, picplayer1, itempics)

        # 创建墙体

        font = pygame.font.SysFont('arial', oneblock)
        timercount = timerTable(window_width - oneblock, 0, font, 99)
        tables.add(timercount)

        walls.add(tables)
        walls.add(tables, Cointable)
        self.tables = tables
        self.walls = walls
        self.num1 = DigitDisplay(oneblock / 2, oneblock / 10)
        self.num2 = DigitDisplay(oneblock / 2 + 5 * 5, oneblock / 10)
        self.num3 = DigitDisplay(oneblock / 2 + 5 * 5 * 2, oneblock / 10)
        self.num4 = DigitDisplay(oneblock / 2 + 5 * 5 * 3, oneblock / 10)
        Coin = Picshow(0, 0, "./assets/font/coin.png")

        task1 = taskBoard(1.75 * oneblock, 0)
        task2 = taskBoard((1.75 + 3) * oneblock, 0)
        self.task_sprites = pygame.sprite.Group(task1, task2)
        # 创建精灵组
        self.all_sprites = pygame.sprite.Group(self.player_a, self.player_b, walls, self.num1, self.num2, self.num3,
                                               self.num4, Coin, self.task_sprites,
                                               Cointable)
        self.Cointable = Cointable

        self.taskmenu = []
        for task in self.task_sprites:
            self.taskmenu.append(task.task)

    def mainloop(self):
        # 游戏循环
        clock = pygame.time.Clock()
        # 设置键盘检测的时间间隔
        key_check_interval = 100  # 单位：毫秒

        # 初始化上一次键盘检测的时间
        last_key_check_time = pygame.time.get_ticks()
        game_over = False
        while not game_over:
            # 处理事件

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                elif event.type == pygame.USEREVENT:
                    if event.action == "countdown_finished":
                        game_over = True

                    elif event.action == "notfinished":
                        self.NOWCOIN -= 1
                        self.taskmenu.remove(event.oldtask)
                        self.taskmenu.append(event.newtask)
                elif event.type == TASK_FINISH_EVENT:
                    self.NOWCOIN += TASK_MENU[event.action]
                    for task in self.task_sprites:
                        if task.task == event.action:
                            self.taskmenu.remove(task.task)

                            task.newtask()
                            self.taskmenu.append(task.task)
                            break

            # 倒计时结束，结束游戏

            current = pygame.time.get_ticks()
            # 如果距离上一次键盘检测的时间已经超过指定的时间间隔
            if current - last_key_check_time >= key_check_interval:
                keys_pressed = pygame.key.get_pressed()

                # 更新玩家

                self.player_a.update(keys_pressed, self.walls, self.player_b)
                self.player_b.update(keys_pressed, self.walls, self.player_a)
                self.tables.update(self.player_a, keys_pressed)
                self.tables.update(self.player_b, keys_pressed)
                self.Cointable.update(self.player_b, keys_pressed, self.taskmenu)
                self.Cointable.update(self.player_a, keys_pressed, self.taskmenu)

                self.task_sprites.update()

                th, hu, te, on = digitize(self.NOWCOIN)
                self.num1.set_num(th)
                self.num2.set_num(hu)
                self.num3.set_num(te)
                self.num4.set_num(on)

                last_key_check_time = current

            # 绘制游戏场景

            self.window.fill((255, 250, 205))
            self.all_sprites.draw(self.window)

            pygame.display.update()
            pygame.display.flip()

            # 控制游戏帧率
            clock.tick(60)

        # 退出pygame
        pygame.quit()


if __name__ == '__main__':
    mainwindows = MainGame()
    mainwindows.mainloop()