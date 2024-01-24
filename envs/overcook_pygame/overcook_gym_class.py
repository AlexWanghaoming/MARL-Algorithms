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
OUT_SUPPLY_EVENT = pygame.USEREVENT + 2
OUT_DISH_EVENT = pygame.USEREVENT + 3

GET_MATERIAL_EVENT = pygame.USEREVENT + 4
GET_DISH_EVENT = pygame.USEREVENT + 5
MADE_NEWTHING_EVENT = pygame.USEREVENT+6
BEGINCUTTING_EVENT = pygame.USEREVENT+7
CUTTINGDOWN_EVENT = pygame.USEREVENT+8
BEGINCOOKING_EVENT = pygame.USEREVENT+9
COOKINGDOWN_EVENT = pygame.USEREVENT+10
COOKINGOUT_EVENT = pygame.USEREVENT +11
TRY_NEWTHING_EVENT = pygame.USEREVENT+12
PUTTHING_DISH_EVENT = pygame.USEREVENT+13
TRASH_EVENT = pygame.USEREVENT+14
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

source = '/alpha/MARL-Algorithms/envs/'

class taskBoard(pygame.sprite.Sprite):
    def __init__(self, x, y, taskmenu):
        super().__init__()

        self.menu = taskmenu

        self.task = random.choice(list(self.menu.keys()))
        self.image = picscale(picload(source + f'overcook_pygame/assets/TASK/{self.task}.png').convert_alpha(), (3 * oneblock, oneblock))

        self.rect = self.image.get_rect()  # 获取图片的矩形区域
        self.rect.x = x  # 设置矩形区域的位置
        self.rect.y = y
        # self.timer = random.randint(50,100)
        self.timer = 200  # wanghm: 任务栏中需要供应菜品的剩余时间
        self.remaining_time = self.timer
        self.start_time = 0

    def update(self,nowtime) -> None:
        if self.timer > 0:
            elapsed_time = nowtime - self.start_time
            self.remaining_time = self.timer - elapsed_time

            if self.remaining_time <= 0:
                oldtask = self.task
                self.newtask(nowtime)

                pygame.event.post(pygame.event.Event(pygame.USEREVENT, {'action': 'notfinished','newtask':self.task,
                                                                        'oldtask':oldtask,'taskclass':self}))

            else:

                progress_bar_rect = pygame.Rect(0, oneblock*7/8-3, 3*oneblock * (1-self.remaining_time / self.timer), oneblock / 8)
                progress_bar_surface = pygame.Surface(progress_bar_rect.size)
                progress_bar_surface.fill((128, 200, 0))
                self.image.blit(progress_bar_surface, progress_bar_rect)

    def newtask(self,nowtime):
        self.task = random.choice(list(self.menu.keys()))
        # self.timer = random.randint(50, 100)
        # self.timer = 50
        self.start_time = nowtime
        self.remaining_time = self.timer
        self.image = picscale(picload(source + f'overcook_pygame/assets/TASK/{self.task}.png').convert_alpha(), (3 * oneblock, oneblock))
        return self.task

class DigitDisplay(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        # 加载数字精灵表
        self.digit_sprite_sheet = picload(source + 'overcook_pygame/assets/font/number.png').convert_alpha()
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

class supplyTable(pygame.sprite.Sprite):
    def __init__(self, x, y, item, itempics):
        super().__init__()
        self.item = item  # 设置物品属性，默认为 None
        self.pics = itempics
        self.updateimg()
        self.rect = self.image.get_rect()  # 获取图片的矩形区域
        self.rect.x = x  # 设置矩形区域的位置
        self.rect.y = y
    def isnewthing(self,item):
        pygame.event.post(pygame.event.Event(TRY_NEWTHING_EVENT))
        if frozenset([self.item,item]) in RECIPE:
            pygame.event.post(pygame.event.Event(MADE_NEWTHING_EVENT,{'newitem':RECIPE[frozenset([self.item,item])]}))
            return RECIPE[frozenset([self.item,item])]
    def updateimg(self, ):
        self.image = picscale(picload(source + 'overcook_pygame/assets/table/table.png').convert_alpha(), ONEBLOCKSIZE)  #
        item_rect = pygame.Rect(0,0, oneblock, oneblock)
        item_surface = picscale(self.pics[self.item], (oneblock, oneblock))
        self.image.blit(item_surface, item_rect)    
    def update(self, player, keys,nowtime) -> None:
        if keys:
            if player.rect.move(player.direction[0] * oneblock / 2,
                                player.direction[1] * oneblock / 2).colliderect(self.rect):
                #
                if self.item=='dish':
                    if not player.dish:
                        player.dish = 'dish'
                        pygame.event.post(pygame.event.Event(OUT_DISH_EVENT))
                        if player.item:
                            pygame.event.post(pygame.event.Event(PUTTHING_DISH_EVENT, {'item': player.item}))
                else:
                    if not player.item:


                        player.item = self.item
                        pygame.event.post(pygame.event.Event(OUT_SUPPLY_EVENT, {'item': self.item}))
                    elif player.dish and self.item:
                        tmp = self.isnewthing(player.item)
                        if tmp:
                            pygame.event.post(pygame.event.Event(PUTTHING_DISH_EVENT, {'item': tmp}))
                            player.item = tmp
                            player.updateimg()


                player.updateimg()
    def availbeinter(self,player):
        if player.rect.move(player.direction[0] * oneblock / 2,
                            player.direction[1] * oneblock / 2).colliderect(self.rect):
            if self.item == 'dish':
                if not player.dish:
                    return True
            else:
                if not player.item:
                    return True
                elif player.dish and self.item:
                    tmp = self.isnewthing(player.item)
                    if tmp:
                        return True
        return False
                
class timerTable(pygame.sprite.Sprite):
    def __init__(self, x, y, font, time):
        super().__init__()
        self.timer = time
        self.image = font.render(str(self.timer),True,(0,0,0))
        self.font = font
        self.rect = self.image.get_rect()  # 获取图片的矩形区域
        self.rect.x = x  # 设置矩形区域的位置
        self.rect.y = y
    def update(self,nowtime) -> None:
        
        if self.timer - nowtime<=0:
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, {'action': 'countdown_finished'}))
        self.image = self.font.render(str((self.timer - nowtime)//10),True,(0,0,0))
        
class coinTable(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.updateimg()
        self.rect = self.image.get_rect()  # 获取图片的矩形区域
        self.rect.x = x  # 设置矩形区域的位置
        self.rect.y = y

    def updateimg(self, ):
        self.image = picscale(picload(source + 'overcook_pygame/assets/table/table.png').convert_alpha(), ONEBLOCKSIZE)  #
        item_rect = pygame.Rect(0,0, oneblock, oneblock)
        item_surface = picscale(picload(source + 'overcook_pygame/assets/table/cointable.png'), (oneblock, oneblock))
        self.image.blit(item_surface, item_rect)    
    def update(self, player, keys,taskmenu) -> None:
        if keys:
            if player.rect.move(player.direction[0] * oneblock / 2,
                                player.direction[1] * oneblock / 2).colliderect(self.rect):
                #

                if player.dish and player.item in taskmenu:

                    pygame.event.post(pygame.event.Event(TASK_FINISH_EVENT, {'action': player.item}))
                    player.dish = None
                    player.item = None
                    player.updateimg()

    def availbeinter(self,player):
        if player.rect.move(player.direction[0] * oneblock / 2,
                            player.direction[1] * oneblock / 2).colliderect(self.rect):
            if player.dish and player.item:
                return True
        return False
                    
class trashTable(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.updateimg()
        self.rect = self.image.get_rect()  # 获取图片的矩形区域
        self.rect.x = x  # 设置矩形区域的位置
        self.rect.y = y
        self.item = None

    def updateimg(self, ):
        self.image = picscale(picload(source + 'overcook_pygame/assets/table/trashbin.png').convert_alpha(), ONEBLOCKSIZE)  #
    def update(self, player, keys,nowtime) -> None:
        if keys:
            if player.rect.move(player.direction[0] * oneblock / 2,
                                player.direction[1] * oneblock / 2).colliderect(self.rect):
                #
                pygame.event.post(pygame.event.Event(TRASH_EVENT, {'item': player.item}))
                player.dish = None
                player.item = None
                player.updateimg()
    def availbeinter(self,player):
        if player.rect.move(player.direction[0] * oneblock / 2,
                            player.direction[1] * oneblock / 2).colliderect(self.rect):
            if player.dish or player.item:
                return True
        return False
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

    def isnewthing(self,item):
        pygame.event.post(pygame.event.Event(TRY_NEWTHING_EVENT))
        if frozenset([self.item,item]) in RECIPE:
            pygame.event.post(pygame.event.Event(MADE_NEWTHING_EVENT,{'newitem':RECIPE[frozenset([self.item,item])]}))
            return RECIPE[frozenset([self.item,item])]
        

    def updateimg(self, ):
        self.image = picscale(picload(source + 'overcook_pygame/assets/table/table.png').convert_alpha(), ONEBLOCKSIZE)  #
        if self.dish:
            item_rect = pygame.Rect(oneblock / 8, oneblock / 8, 0.75 * oneblock, 0.75 * oneblock)
            item_surface = picscale(self.pics[self.dish], (0.75 * oneblock, 0.75 * oneblock))
            self.image.blit(item_surface, item_rect)
        if self.item:
            item_rect = pygame.Rect(oneblock / 4, oneblock / 4, oneblock / 2, oneblock / 2)
            item_surface = picscale(self.pics[self.item], (oneblock / 2, oneblock / 2))
            self.image.blit(item_surface, item_rect)

    def update(self, player, keys,nowtime) -> None:
        if keys:
            if player.rect.move(player.direction[0] * oneblock / 2,
                                player.direction[1] * oneblock / 2).colliderect(self.rect):
                #
                if self.dish:  # 桌上有盘子
                    if self.item:  # 盘子里有东西
                        if not player.item and not player.dish:
                            player.exchangedish(self)
                            player.exchangeitem(self)

                        elif not player.item and player.dish:  # 手上有盘子

                            pygame.event.post(pygame.event.Event(PUTTHING_DISH_EVENT, {'item': self.item}))
                            player.exchangeitem(self)
                            #pygame.event.post(pygame.event.Event(PUTTHING_DISH_EVENT, {'item': self.item}))交换，因此不变情况

                        else:#手上有东西
                            tmp = self.isnewthing(player.item)
                            if tmp:
                                pygame.event.post(pygame.event.Event(PUTTHING_DISH_EVENT, {'item': tmp}))
                                self.item = tmp
                                player.item = None
                        # 手上有盘有东西或手上无盘有东西没法拿了
                    else:#盘子里没东西
                        if player.item and player.dish:#把手上的盘子里的东西放桌上的盘子里
                            
                            self.item, player.item =player.item,self.item
                            #pygame.event.post(pygame.event.Event(PUTTHING_DISH_EVENT, {'item': self.item}))放置，场上情况也不变
                        elif player.item and not player.dish:#把东西放盘子里
                            self.item, player.item =player.item,self.item
                            pygame.event.post(pygame.event.Event(PUTTHING_DISH_EVENT, {'item': self.item}))


                        else:
                            player.dish, self.dish =self.dish,player.dish#拿起盘子或交换盘子（无事发生）

                else:#桌上没盘子
                    if self.item:  # 桌上有东西
                        if not player.item:#玩家空手,东西# 玩家手上有盘子，东西装盘子里
                            self.item, player.item =player.item,self.item
                            if player.dish:
                                pygame.event.post(pygame.event.Event(PUTTHING_DISH_EVENT, {'item': player.item}))

                        elif player.dish:
                            tmp = self.isnewthing(player.item)
                            if tmp:
                                pygame.event.post(pygame.event.Event(PUTTHING_DISH_EVENT, {'item': tmp}))
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

    def availbeinter(self,player):
        if player.rect.move(player.direction[0] * oneblock / 2,
                            player.direction[1] * oneblock / 2).colliderect(self.rect):
            if self.dish:  # 桌上有盘子
                if self.item:  # 盘子里有东西
                    if not player.item and not player.dish:
                        return True

                    elif not player.item and player.dish:  # 手上有盘子
                        return
                    else:  # 手上有东西
                        tmp = self.isnewthing(player.item)
                        if tmp:
                            return True
                        return False
                    # 手上有盘有东西或手上无盘有东西没法拿了
                else:  # 盘子里没东西
                    if player.item and player.dish:  # 把手上的盘子里的东西放桌上的盘子里

                        return True
                    elif player.item and not player.dish:  # 把东西放盘子里
                        return True

                    else:
                        return False  # 拿起盘子或交换盘子（无事发生）

            else:  # 桌上没盘子
                if self.item:  # 桌上有东西
                    if not player.item:  # 玩家空手,东西# 玩家手上有盘子，东西装盘子里
                        return True
                    elif player.dish:
                        tmp = self.isnewthing(player.item)
                        if tmp:
                            return True

                    # 手上有盘有东西或手上无盘有东西没法拿了
                else:  # 桌上没东西
                    if not player.item and not player.dish:  # 把手上的盘子里的东西放桌上的盘子里
                        return False
                    return True
        return False

class Player(pygame.sprite.Sprite):
    def __init__(self,name, x, y, playerpic, itempic):

        super().__init__()
        self.name = name
        self.playerpic = playerpic
        self.itempic = itempic
        self.direction = [0, 1]
        self.item = None
        self.dish = None
        self.image = playerpic[str(self.direction)]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.control = {0:[0,0],1:[0,1],2:[1,0],3:[0,-1],4:[-1,0]}   # 玩家动作： stay：0，下：1，右：2，上：3，左：4，interact：5
        self.speed = oneblock
        self.cutting=False
    def exchangedish(self,table):
        self.dish,table.dish = table.dish,self.dish
        pygame.event.post(pygame.event.Event(GET_DISH_EVENT, 
                                             {'player': self.name,'olditem':self.dish,
                                              'newitem':table.dish}))

    def exchangeitem(self,table):
        self.item,table.item = table.item,self.item
        pygame.event.post(pygame.event.Event(GET_MATERIAL_EVENT, 
                                             {'player': self.name,'olditem':self.item,
                                              'newitem':table.item}))        
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

    def availaction(self, action, pengzhuang, player):
        move_vector = self.control[action]

        if move_vector == self.direction:
            pengzhuangflag = True
            for wall in pengzhuang:
                if self.rect.move(move_vector[0] * self.speed,
                             move_vector[1] * self.speed).colliderect(wall.rect):
                    pengzhuangflag = False
                    break
            if pengzhuangflag:
                if isinstance(player,list):
                    for play in player:
                        if self.rect.move(move_vector[0] * self.speed,
                             move_vector[1] * self.speed).colliderect(play.rect):
                            pengzhuangflag = False
                            break
                else:
                    if self.rect.move(move_vector[0] * self.speed,
                             move_vector[1] * self.speed).colliderect(player.rect):
                        pengzhuangflag = False
            return pengzhuangflag
        else:
            return True

    def update(self, action, pengzhuang, player):
    
        if self.cutting:
            return
        tempx = self.rect.x
        tempy = self.rect.y

        move_vector = self.control[action]
        if move_vector == self.direction:
            self.rect.x += move_vector[0] * self.speed
            self.rect.y += move_vector[1] * self.speed
        elif sum(move_vector) == 0:
            return
        else:
            self.direction = move_vector
            self.updateimg()
            return True#改变方向是available的
        pengzhuangflag = True
        # 碰撞检测
        for wall in pengzhuang:
            if self.rect.colliderect(wall.rect):
                self.rect.x = tempx
                self.rect.y = tempy
                pengzhuangflag = False
                break
        if pengzhuangflag:
            if isinstance(player,list):
                for play in player:
                    if self.rect.colliderect(play.rect):
                        self.rect.x = tempx
                        self.rect.y = tempy
                        pengzhuangflag = False
                        break
            else:
                if self.rect.colliderect(player.rect):
                    self.rect.x = tempx
                    self.rect.y = tempy
                    pengzhuangflag = False
        return pengzhuangflag

            
class CuttingTable(pygame.sprite.Sprite):
    def __init__(self, x, y,  itempics):
        super().__init__()
        self.item = None  # 设置物品属性，默认为 None
        self.pics = itempics
        self.cuttingtime = 6
        self.timer = 0
        self.start_time = 0
        self.updateimg()
        self.rect = self.image.get_rect()  # 获取图片的矩形区域
        self.rect.x = x  # 设置矩形区域的位置
        self.rect.y = y
        gif = picload(source + 'overcook_pygame/assets/table/cutting.png').convert_alpha()
        self.frames = []
        self.e_time=0
        self.cuttingplayer = None
        for i in range(3):
            self.frames.append(gif.subsurface(pygame.Rect(i * 32, 0, 32, 32)))
    def isnewthing(self,item):
        pygame.event.post(pygame.event.Event(TRY_NEWTHING_EVENT))
        if frozenset([self.item,item]) in RECIPE:
            pygame.event.post(pygame.event.Event(MADE_NEWTHING_EVENT,{'newitem':RECIPE[frozenset([self.item,item])]}))
            return RECIPE[frozenset([self.item,item])]
    def updateimg(self, ):
          #
        if self.item:
            self.image = picscale(picload(source + 'overcook_pygame/assets/table/cuttingboard-pixilart.png').convert_alpha(), ONEBLOCKSIZE)
            item_rect = pygame.Rect(oneblock / 4, oneblock / 4, oneblock / 2, oneblock / 2)
            item_surface = picscale(self.pics[self.item], (oneblock / 2, oneblock / 2))
            self.image.blit(item_surface, item_rect)
            cut_rect = pygame.Rect(0,oneblock/4, oneblock, oneblock )
            cut_surface = picscale(self.frames[self.e_time%3], (oneblock , oneblock ))
            self.image.blit(cut_surface,cut_rect)
        else:
            self.image = picscale(picload(source + 'overcook_pygame/assets/table/cuttingtable.png').convert_alpha(), ONEBLOCKSIZE)
    def update(self, player, keys,nowtime) -> None:
        if keys:
            if player.rect.move(player.direction[0] * oneblock / 2,
                                player.direction[1] * oneblock / 2).colliderect(self.rect):             # 如果玩家手中有物品
                if player.item:

                    if 'BC' in player.item:
                    # 如果玩家有可以切的东西，就放进去切
                        
                        if self.item is None:
                            pygame.event.post(pygame.event.Event(BEGINCUTTING_EVENT,{'item':player.item}))
                            self.item, player.item = player.item, self.item
                            player.cutting = True
                            self.cuttingplayer = player
                            player.updateimg()
                            self.updateimg()

                            self.start_time = nowtime
                            self.timer = self.cuttingtime
                    elif player.dish and self.item:
                        tmp = self.isnewthing(player.item)
                        if tmp:
                            pygame.event.post(pygame.event.Event(PUTTHING_DISH_EVENT, {'item': tmp}))
                            player.item = tmp
                            self.item = None
                            player.updateimg()
                            self.updateimg()
                else:
                    #没东西可以把东西拿出来
                    if not player.cutting:
                        if self.item:
                            if player.dish:
                                pygame.event.post(pygame.event.Event(PUTTHING_DISH_EVENT, {'item': self.item}))                            
                            player.exchangeitem(self)

                            #self.item, player.item = player.item, self.item
                        
                            player.updateimg()
                            self.updateimg()

        if self.item and self.timer > 0:

            elapsed_time = nowtime - self.start_time
            self.e_time = nowtime %3
            remaining_time = self.timer - elapsed_time

            if remaining_time <= 0:
                self.cuttingplayer.cutting = False
                if 'BC' in self.item:
                    self.item=self.item.replace('BC','AC')
                    
                    pygame.event.post(pygame.event.Event(CUTTINGDOWN_EVENT,{'item':self.item}))
                    self.image = picscale(picload(source + 'overcook_pygame/assets/table/cuttingboard-pixilart.png').convert_alpha(),
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
    def availbeinter(self,player):
        if player.rect.move(player.direction[0] * oneblock / 2,
                            player.direction[1] * oneblock / 2).colliderect(self.rect):  # 如果玩家手中有物品
            if player.item:

                if 'BC' in player.item:
                    # 如果玩家有可以切的东西，就放进去切
                    return True
                elif player.dish and self.item:
                    tmp = self.isnewthing(player.item)
                    if tmp:
                        return True
            else:
                # 没东西可以把东西拿出来
                if not player.cutting:
                    if self.item:
                        return True
        return False
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
        self.cookingtime = 20

    def updateimg(self, ):
        self.image = picscale(picload(source + 'overcook_pygame/assets/cook/cook.png').convert_alpha(), ONEBLOCKSIZE)  #
        if self.item:
            item_rect = pygame.Rect(oneblock / 4, oneblock / 4, oneblock / 2, oneblock / 2)
            item_surface = picscale(self.pics[self.item], (oneblock / 2, oneblock / 2))
            self.image.blit(item_surface, item_rect)
    def isnewthing(self,item):
        pygame.event.post(pygame.event.Event(TRY_NEWTHING_EVENT))
        if frozenset([self.item,item]) in RECIPE:
            pygame.event.post(pygame.event.Event(MADE_NEWTHING_EVENT,{'newitem':RECIPE[frozenset([self.item,item])]}))
            return RECIPE[frozenset([self.item,item])]
    def update(self, player, keys,nowtime) -> None:
        if keys:
            if player.rect.move(player.direction[0] * oneblock / 2,player.direction[1] * oneblock / 2).colliderect(self.rect):             # 如果玩家手中有物品
                if player.item:
                    if 'raw' in player.item:
                    # 如果玩家有可以烧的东西，就放进去烧
                        if self.item is None:
                            pygame.event.post(pygame.event.Event(BEGINCOOKING_EVENT,{'item':player.item}))
                            self.item, player.item = player.item, self.item
                            player.updateimg()
                            self.updateimg()

                            self.start_time = nowtime
                            self.timer = self.cookingtime
                    elif player.dish and self.item:
                        tmp = self.isnewthing(player.item)
                        if tmp:
                            pygame.event.post(pygame.event.Event(PUTTHING_DISH_EVENT, {'item': tmp}))
                            player.item = tmp
                            self.item = None
                            player.updateimg()
                            self.updateimg()
                        
                else:
                    #没东西可以把东西拿出来#7.18修改如果没熟不能拿出来
                    if self.item and 'raw' not in self.item:
                        if player.dish:
                            pygame.event.post(pygame.event.Event(PUTTHING_DISH_EVENT, {'item': self.item}))
                        pygame.event.post(pygame.event.Event(COOKINGOUT_EVENT,{'item':self.item}))
                        self.item,player.item = player.item,self.item
                        
                        player.updateimg()
                        self.updateimg()

        if self.item and self.timer > 0:
            elapsed_time = nowtime - self.start_time
            remaining_time = self.timer - elapsed_time

            if remaining_time <= 0:
                if 'raw' in self.item:
                    self.item=self.item.replace('raw','cooked')
                    pygame.event.post(pygame.event.Event(COOKINGDOWN_EVENT,{'item':self.item}))
                    self.updateimg()
                self.timer=0
            else:
                progress_bar_rect = pygame.Rect(0, 0, oneblock * (1 - remaining_time / self.timer), oneblock / 8)
                progress_bar_surface = pygame.Surface(progress_bar_rect.size)
                progress_bar_surface.fill((255, 0, 0))
                self.image.blit(progress_bar_surface, progress_bar_rect)
    def availbeinter(self,player):
        if player.rect.move(player.direction[0] * oneblock / 2,
                            player.direction[1] * oneblock / 2).colliderect(self.rect):  # 如果玩家手中有物品
            if player.item:
                if 'raw' in player.item:
                    # 如果玩家有可以烧的东西，就放进去烧
                    return True
                elif player.dish and self.item:
                    tmp = self.isnewthing(player.item)
                    if tmp:
                        return True
            else:
                # 没东西可以把东西拿出来#7.18修改如果没熟不能拿出来
                if self.item and 'raw' not in self.item:
                    return True
        return False
# 定义墙体类
class Wall(pygame.sprite.Sprite):

    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
