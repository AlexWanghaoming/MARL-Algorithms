import pygame
from pygame.transform import scale as picscale
from pygame.image import load as picload

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
def digitize(num):
    # 将数字转换为字符串并填充为4位
    num_str = str(num).zfill(4)
    # 取出每一位
    thousands = int(num_str[0])
    hundreds = int(num_str[1])
    tens = int(num_str[2])
    ones = int(num_str[3])
    # 返回每一位数字组成的元组
    return thousands, hundreds, tens, ones
# 定义玩家类
# to do 可以以table类为基础做基类


class taskBoard(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.menu = TASK_MENU

        self.task = random.choice(list(self.menu.keys()))
        self.image = picscale(picload(f'assets/TASK/{self.task}.png').convert_alpha(), (3 * oneblock, oneblock))

        self.rect = self.image.get_rect()  # 获取图片的矩形区域
        self.rect.x = x  # 设置矩形区域的位置
        self.rect.y = y
        self.timer = random.randint(10,20)*1000
        self.start_time = pygame.time.get_ticks()
    def update(self,) -> None:
        if self.timer > 0:
            elapsed_time = pygame.time.get_ticks() - self.start_time
            remaining_time = self.timer - elapsed_time

            if remaining_time <= 0:
                oldtask = self.task
                self.newtask()

                pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"action": "notfinished","newtask":self.task,
                                                                        "oldtask":oldtask}))

            else:

                progress_bar_rect = pygame.Rect(0, oneblock*7/8-3, 3*oneblock * (1-remaining_time / self.timer), oneblock / 8)
                progress_bar_surface = pygame.Surface(progress_bar_rect.size)
                progress_bar_surface.fill((128, 200, 0))
                self.image.blit(progress_bar_surface, progress_bar_rect)
    def newtask(self,):
        self.task = random.choice(list(self.menu.keys()))
        self.timer = random.randint(10, 20) * 1000
        self.start_time = pygame.time.get_ticks()
        self.image = picscale(picload(f'assets/TASK/{self.task}.png').convert_alpha(), (3 * oneblock, oneblock))
class DigitDisplay(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        # 加载数字精灵表
        self.digit_sprite_sheet = picload("assets/font/number.png").convert_alpha()
        # 确定每个数字的位置和大小
        self.digit_rects = [
            pygame.Rect(i * 5, 0, 4, 5) for i in range(10)
        ]
        # 初始化显示数字为0
        self.num = 0
        self.image = picscale(self.digit_sprite_sheet.subsurface(self.digit_rects[self.num]), (4*5,5*5))
        self.rect = self.image.get_rect()  # 获取图片的矩形区域
        self.rect.x = x  # 设置矩形区域的位置
        self.rect.y = y
    def set_num(self, num):
        # 设置显示的数字，并更新图像
        self.num = num
        self.image = picscale(self.digit_sprite_sheet.subsurface(self.digit_rects[self.num]), (4*5,5*5))



class Picshow(pygame.sprite.Sprite):
    def __init__(self, x, y, picdir):
        super().__init__()
        self.image = picscale(picload(picdir).convert_alpha(),(oneblock/2,oneblock/2))
        self.rect = self.image.get_rect()  # 获取图片的矩形区域
        self.rect.x = x  # 设置矩形区域的位置
        self.rect.y = y
class Gifshow(pygame.sprite.Sprite):
    def __init__(self, x, y, picdir):
        super().__init__()
        gif = picload("assets/table/cutting.png").convert_alpha()
        self.frames = []
        for i in range(3):
            self.frames.append(gif.subsurface(pygame.Rect(i * 32, 0, 32, 32)))
        self.frame_index = 0
        self.frame_count = 3
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()  # 获取图片的矩形区域
        self.rect.x = x  # 设置矩形区域的位置
        self.rect.y = y
    def update(self,):
        temp = (pygame.time.get_ticks()//100) %self.frame_count

        if self.frame_index!=temp:

            self.frame_index = temp
            self.image = self.frames[self.frame_index]
class supplyTable(pygame.sprite.Sprite):
    def __init__(self, x, y, supplyitem, itempics):
        super().__init__()
        self.supplyitem = supplyitem  # 设置物品属性，默认为 None
        self.pics = itempics
        self.updateimg()
        self.rect = self.image.get_rect()  # 获取图片的矩形区域
        self.rect.x = x  # 设置矩形区域的位置
        self.rect.y = y

    def updateimg(self, ):
        self.image = picscale(picload('assets/table/table.png').convert_alpha(), ONEBLOCKSIZE)  #
        item_rect = pygame.Rect(0,0, oneblock, oneblock)
        item_surface = picscale(self.pics[self.supplyitem], (oneblock, oneblock))
        self.image.blit(item_surface, item_rect)    
    def update(self, player, keys) -> None:
        if keys[player.interkey]:
            if player.rect.move(player.direction[0] * oneblock / 2,
                                player.direction[1] * oneblock / 2).colliderect(self.rect):
                #
                if self.supplyitem=="dish":
                    
                    player.dish = "dish"
                else:
                    if not player.item:
                        player.item = self.supplyitem
                player.updateimg()
class timerTable(pygame.sprite.Sprite):
    def __init__(self, x, y, font,time):
        super().__init__()
        self.timer = time
        self.image = font.render(str(self.timer),True,(0,0,0))
        self.font = font
        self.rect = self.image.get_rect()  # 获取图片的矩形区域
        self.rect.x = x  # 设置矩形区域的位置
        self.rect.y = y
    def update(self,player,keys) -> None:
        if self.timer - pygame.time.get_ticks()// 1000<=0:
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"action": "countdown_finished"}))
        self.image = self.font.render(str(self.timer - pygame.time.get_ticks() // 1000),True,(0,0,0))
class coinTable(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.updateimg()
        self.rect = self.image.get_rect()  # 获取图片的矩形区域
        self.rect.x = x  # 设置矩形区域的位置
        self.rect.y = y

    def updateimg(self, ):
        self.image = picscale(picload('assets/table/table.png').convert_alpha(), ONEBLOCKSIZE)  #
        item_rect = pygame.Rect(0,0, oneblock, oneblock)
        item_surface = picscale(picload('assets/table/cointable.png'), (oneblock, oneblock))
        self.image.blit(item_surface, item_rect)    
    def update(self, player, keys,taskmenu) -> None:
        if keys[player.interkey]:
            if player.rect.move(player.direction[0] * oneblock / 2,
                                player.direction[1] * oneblock / 2).colliderect(self.rect):
                #

                if player.dish and player.item in taskmenu:

                    pygame.event.post(pygame.event.Event(TASK_FINISH_EVENT, {"action": player.item}))
                    player.dish = None
                    player.item = None
                    player.updateimg()
class trashTable(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.updateimg()
        self.rect = self.image.get_rect()  # 获取图片的矩形区域
        self.rect.x = x  # 设置矩形区域的位置
        self.rect.y = y

    def updateimg(self, ):
        self.image = picscale(picload('assets/table/trashbin.png').convert_alpha(), ONEBLOCKSIZE)  #
    def update(self, player, keys) -> None:
        if keys[player.interkey]:
            if player.rect.move(player.direction[0] * oneblock / 2,
                                player.direction[1] * oneblock / 2).colliderect(self.rect):
                #

                player.dish = None
                player.item = None
                player.updateimg()
class Table(pygame.sprite.Sprite):
    def __init__(self, x, y, item, dish, tablepics):
        super().__init__()
        self.item = item  # 设置物品属性，默认为 None
        self.dish = dish
        self.pics = tablepics
        self.updateimg()
        self.rect = self.image.get_rect()  # 获取图片的矩形区域
        self.rect.x = x  # 设置矩形区域的位置
        self.rect.y = y
        self.recipe = RECIPE
    def isnewthing(self,item):
        if frozenset([self.item,item]) in self.recipe:
            return self.recipe[frozenset([self.item,item])]

    def updateimg(self, ):
        self.image = picscale(picload('assets/table/table.png').convert_alpha(), ONEBLOCKSIZE)  #
        if self.dish:
            item_rect = pygame.Rect(oneblock / 8, oneblock / 8, 0.75 * oneblock, 0.75 * oneblock)
            item_surface = picscale(self.pics[self.dish], (0.75 * oneblock, 0.75 * oneblock))
            self.image.blit(item_surface, item_rect)
        if self.item:
            item_rect = pygame.Rect(oneblock / 4, oneblock / 4, oneblock / 2, oneblock / 2)
            item_surface = picscale(self.pics[self.item], (oneblock / 2, oneblock / 2))
            self.image.blit(item_surface, item_rect)

    def update(self, player, keys) -> None:
        if keys[player.interkey]:
            if player.rect.move(player.direction[0] * oneblock / 2,
                                player.direction[1] * oneblock / 2).colliderect(self.rect):
                #
                if self.dish:  # 桌上有盘子
                    if self.item:  # 盘子里有东西
                        if not player.item and not player.dish:
                            player.dish, self.dish =self.dish,player.dish
                            self.item, player.item =player.item,self.item

                        elif not player.item and player.dish:  # 手上有盘子
                            self.item, player.item =player.item,self.item

                        else:#手上有东西
                            tmp = self.isnewthing(player.item)
                            if tmp:
                                self.item = tmp
                                player.item = None
                        # 手上有盘有东西或手上无盘有东西没法拿了
                    else:#盘子里没东西
                        if player.item and player.dish:#把手上的盘子里的东西放桌上的盘子里
                            self.item, player.item =player.item,self.item

                        elif player.item and not player.dish:#把东西放盘子里
                            self.item, player.item =player.item,self.item


                        else:
                            player.dish, self.dish =self.dish,player.dish#拿起盘子或交换盘子（无事发生）

                else:#桌上没盘子
                    if self.item:  # 桌上有东西
                        if not player.item:#玩家拿东西# 玩家手上有盘子，东西装盘子里
                            self.item, player.item =player.item,self.item

                        elif player.dish:
                            tmp = self.isnewthing(player.item)
                            if tmp:
                                self.item = tmp
                                self.dish,player.dish = player.dish,self.dish
                                player.item = None


                        # 手上有盘有东西或手上无盘有东西没法拿了
                    else:  # 桌上没东西
                        if player.item:  # 把手上的盘子里的东西放桌上的盘子里
                            self.item, player.item =player.item,self.item


                        if player.dish:
                            player.dish, self.dish =self.dish,player.dish
                self.updateimg()
                player.updateimg()
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, controls, interkey, playerpic, itempic):

        super().__init__()
        self.playerpic = playerpic
        self.itempic = itempic
        self.direction = [0, 1]
        self.item = None
        self.dish = None
        self.image = playerpic[str(self.direction)]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.controls = controls
        self.interkey = interkey
        self.speed = oneblock
        self.cutting=False

    def updateimg(self, ):
        if self.dish or self.item:
            self.image = self.playerpic[str(self.direction) + '_'].copy()
            if self.direction != [0, -1]:
                if self.dish:
                        item_rect = pygame.Rect((1 + self.direction[0]) * oneblock / 8, oneblock / 4, DISHSIZE[0],DISHSIZE[0])
                        item_surface = picscale(self.itempic[self.dish], DISHSIZE)
                        self.image.blit(item_surface, item_rect)
                if self.item:


                        item_rect = pygame.Rect((1 + self.direction[0]) * oneblock / 4, oneblock / 2, oneblock / 2,
                                                oneblock / 2)
                        item_surface = picscale(self.itempic[self.item], (oneblock / 2, oneblock / 2))
                        self.image.blit(item_surface, item_rect)
        else:
            self.image = self.playerpic[str(self.direction)]

    def update(self, keys_pressed, pengzhuang, player):
        if self.cutting:
            return
        tempx = self.rect.x
        tempy = self.rect.y

        move_vector = [sum(self.controls[key][i] for key in self.controls if keys_pressed[key]) for i in range(2)]
        if move_vector == self.direction:
            self.rect.x += move_vector[0] * self.speed
            self.rect.y += move_vector[1] * self.speed
        elif sum(move_vector) == 0 or abs(sum(move_vector)) == 2:
            return
        else:
            self.direction = move_vector
            self.updateimg()

        # 碰撞检测
        for wall in pengzhuang:
            if self.rect.colliderect(wall.rect):
                self.rect.x = tempx
                self.rect.y = tempy
        if self.rect.colliderect(player.rect):
            self.rect.x = tempx
            self.rect.y = tempy
class CuttingTable(pygame.sprite.Sprite):
    def __init__(self, x, y,  itempics):
        super().__init__()
        self.item = None  # 设置物品属性，默认为 None
        self.pics = itempics
        self.cuttingtime = 3 * 1000
        self.timer = 0
        self.start_time = 0
        self.updateimg()
        self.rect = self.image.get_rect()  # 获取图片的矩形区域
        self.rect.x = x  # 设置矩形区域的位置
        self.rect.y = y
        gif = picload("assets/table/cutting.png").convert_alpha()
        self.frames = []
        self.e_time=0
        self.cuttingplayer = None
        for i in range(3):
            self.frames.append(gif.subsurface(pygame.Rect(i * 32, 0, 32, 32)))

    def updateimg(self, ):
          #
        if self.item:
            self.image = picscale(picload('assets/table/cuttingboard-pixilart.png').convert_alpha(), ONEBLOCKSIZE)
            item_rect = pygame.Rect(oneblock / 4, oneblock / 4, oneblock / 2, oneblock / 2)
            item_surface = picscale(self.pics[self.item], (oneblock / 2, oneblock / 2))
            self.image.blit(item_surface, item_rect)
            cut_rect = pygame.Rect(0,oneblock/4, oneblock, oneblock )
            cut_surface = picscale(self.frames[self.e_time%3], (oneblock , oneblock ))
            self.image.blit(cut_surface,cut_rect)
        else:
            self.image = picscale(picload('assets/table/cuttingtable.png').convert_alpha(), ONEBLOCKSIZE)
    def update(self, player, keys) -> None:
        if keys[player.interkey]:
            if player.rect.move(player.direction[0] * oneblock / 2,
                                player.direction[1] * oneblock / 2).colliderect(self.rect):             # 如果玩家手中有物品
                if player.item:

                    if 'BC' in player.item:
                    # 如果玩家有可以烧的东西，就放进去烧

                        if self.item is None:
                            self.item, player.item = player.item, self.item
                            player.cutting = True
                            self.cuttingplayer = player
                            player.updateimg()
                            self.updateimg()

                            self.start_time = pygame.time.get_ticks()
                            self.timer = self.cuttingtime
                else:
                    #没东西可以把东西拿出来
                    if self.item:
                        self.item, player.item = player.item, self.item
                        player.cutting = False
                        player.updateimg()
                        self.updateimg()

        if self.item and self.timer > 0:

            elapsed_time = pygame.time.get_ticks() - self.start_time
            self.e_time = (pygame.time.get_ticks()//100) %3
            remaining_time = self.timer - elapsed_time

            if remaining_time <= 0:
                self.cuttingplayer.cutting = False
                if 'BC' in self.item:
                    self.item=self.item.replace('BC','AC')
                    self.image = picscale(picload('assets/table/cuttingboard-pixilart.png').convert_alpha(),
                                          ONEBLOCKSIZE)
                    item_rect = pygame.Rect(oneblock / 4, oneblock / 4, oneblock / 2, oneblock / 2)
                    item_surface = picscale(self.pics[self.item], (oneblock / 2, oneblock / 2))
                    self.image.blit(item_surface, item_rect)
                self.timer=0

            else:

                self.updateimg()
                progress_bar_rect = pygame.Rect(0, 0, oneblock * (1 - remaining_time / self.timer), oneblock / 8)
                progress_bar_surface = pygame.Surface(progress_bar_rect.size)
                progress_bar_surface.fill((255, 0, 0))
                self.image.blit(progress_bar_surface, progress_bar_rect)
class Cook(pygame.sprite.Sprite):
    def __init__(self, x, y,  itempics):
        super().__init__()
        self.item = None  # 设置物品属性，默认为 None
        self.pics = itempics
        self.timer = 0
        self.start_time = 0
        self.updateimg()
        self.rect = self.image.get_rect()  # 获取图片的矩形区域
        self.rect.x = x  # 设置矩形区域的位置
        self.rect.y = y
        self.cookingtime = 3*1000

    def updateimg(self, ):
        self.image = picscale(picload('assets/cook/cook.png').convert_alpha(), ONEBLOCKSIZE)  #
        if self.item:
            item_rect = pygame.Rect(oneblock / 4, oneblock / 4, oneblock / 2, oneblock / 2)
            item_surface = picscale(self.pics[self.item], (oneblock / 2, oneblock / 2))
            self.image.blit(item_surface, item_rect)
    def update(self, player, keys) -> None:
        if keys[player.interkey]:
            if player.rect.move(player.direction[0] * oneblock / 2,
                                player.direction[1] * oneblock / 2).colliderect(self.rect):             # 如果玩家手中有物品
                if player.item:
                    if 'raw' in player.item:
                    # 如果玩家有可以烧的东西，就放进去烧
                        if self.item is None:
                            self.item, player.item = player.item, self.item
                            player.updateimg()
                            self.updateimg()

                            self.start_time = pygame.time.get_ticks()
                            self.timer = self.cookingtime
                else:
                    #没东西可以把东西拿出来
                    if self.item:
                        self.item, player.item = player.item, self.item
                        player.updateimg()
                        self.updateimg()

        if self.item and self.timer > 0:
            elapsed_time = pygame.time.get_ticks() - self.start_time
            remaining_time = self.timer - elapsed_time

            if remaining_time <= 0:
                if 'raw' in self.item:
                    self.item=self.item.replace('raw','cooked')
                    self.updateimg()
                self.timer=0
            else:
                progress_bar_rect = pygame.Rect(0, 0, oneblock * (1 - remaining_time / self.timer), oneblock / 8)
                progress_bar_surface = pygame.Surface(progress_bar_rect.size)
                progress_bar_surface.fill((255, 0, 0))
                self.image.blit(progress_bar_surface, progress_bar_rect)
# 定义墙体类
class Wall(pygame.sprite.Sprite):

    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
