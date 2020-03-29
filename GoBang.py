import pygame
from enum import IntEnum
from pygame.locals import *
from MaxMin_AlphaBeta import *

#定义游戏棋盘的参数
REC_SIZE = 50#棋子移动空间的大小
CHESS_RADIUS = REC_SIZE // 2 - 2
CHESS_LEN = 15#棋子长度
MAP_WIDTH = CHESS_LEN * REC_SIZE#地图宽度
MAP_HEIGHT = CHESS_LEN * REC_SIZE#地图高度
INFO_WIDTH = 200#信息宽度
BUTTON_WIDTH = 140#按钮宽度
BUTTON_HEIGHT = 50#按钮高度
SCREEN_WIDTH = MAP_WIDTH + INFO_WIDTH#屏幕宽度
SCREEN_HEIGHT = MAP_HEIGHT#屏幕高度
SEARCH_DEPTH = 5       #搜索深度5
LIMITED_MOVE_NUM = 10   #限制步数10
#地图类
class Map():
    #初始化，设置
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.map = [[0 for x in range(self.width)] for y in range(self.height)]
        self.steps = []
    #复位函数
    def reset(self):
        for y in range(self.height):
            for x in range(self.width):
                self.map[y][x] = 0
        self.steps = []
    #转换玩家
    def reverseTurn(self, turn):
        if turn == MAP_ENTRY_TYPE.MAP_PLAYER_ONE:
            return MAP_ENTRY_TYPE.MAP_PLAYER_TWO
        else:
            return MAP_ENTRY_TYPE.MAP_PLAYER_ONE
    #获取地图中可以下棋的单元
    def getMapUnitRect(self, x, y):
        map_x = x * REC_SIZE
        map_y = y * REC_SIZE
        return (map_x, map_y, REC_SIZE, REC_SIZE)
    #地图上点的下标
    def MapPosToIndex(self, map_x, map_y):
        x = map_x // REC_SIZE
        y = map_y // REC_SIZE
        return (x, y)
    #判断是否在地图上
    def isInMap(self, map_x, map_y):
        if (map_x <= 0 or map_x >= MAP_WIDTH or
                map_y <= 0 or map_y >= MAP_HEIGHT):
            return False
        return True
    #判断是否为空
    def isEmpty(self, x, y):
        return (self.map[y][x] == 0)
    #点击时反应
    def click(self, x, y, type):
        self.map[y][x] = type.value
        self.steps.append((x, y))
    #画出棋子
    def drawChess(self, screen):
        player_one = (255, 251, 240)#颜色rgb
        player_two = (10, 10, 10)
        player_color = [player_one, player_two]

        font = pygame.font.SysFont('simsunnsimsun', REC_SIZE * 2 // 3)#棋盘表面
        for i in range(len(self.steps)):
            x, y = self.steps[i]#步长
            map_x, map_y, width, height = self.getMapUnitRect(x, y)#棋盘上能下棋的位置
            pos, radius = (map_x + width // 2, map_y + height // 2), CHESS_RADIUS#棋子半径
            turn = self.map[y][x]#转换
            if turn == 1:
                op_turn = 2
            else:
                op_turn = 1
            pygame.draw.circle(screen, player_color[turn - 1], pos, radius)#画出圈
            msg_image = font.render(str(i), True, player_color[op_turn - 1], player_color[turn - 1])#双方的棋子
            msg_image_rect = msg_image.get_rect()#棋子反应
            msg_image_rect.center = pos#棋子中心
            screen.blit(msg_image, msg_image_rect)#屏幕刷新

        if len(self.steps) > 0:
            last_pos = self.steps[-1]
            map_x, map_y, width, height = self.getMapUnitRect(last_pos[0], last_pos[1])
            purple_color = (0, 0, 255)
            point_list = [(map_x, map_y), (map_x + width, map_y),
                          (map_x + width, map_y + height), (map_x, map_y + height)]
            pygame.draw.lines(screen, purple_color, True, point_list, 1)
    #绘制棋盘
    def drawBackground(self, screen):
        color = (0, 0, 0)
        for y in range(self.height):
            # draw a horizontal line
            start_pos, end_pos = (REC_SIZE // 2, REC_SIZE // 2 + REC_SIZE * y), (
            MAP_WIDTH - REC_SIZE // 2, REC_SIZE // 2 + REC_SIZE * y)#棋盘位置
            if y == (self.height) // 2:
                width = 2
            else:
                width = 1
            pygame.draw.line(screen, color, start_pos, end_pos, width)#画线
        for x in range(self.width):
            # draw a horizontal line
            start_pos, end_pos = (REC_SIZE // 2 + REC_SIZE * x, REC_SIZE // 2), (
            REC_SIZE // 2 + REC_SIZE * x, MAP_HEIGHT - REC_SIZE // 2)
            if x == (self.width) // 2:
                width = 2
            else:
                width = 1
            pygame.draw.line(screen, color, start_pos, end_pos, width)
        rec_size = 8
        pos = [(3, 3), (11, 3), (3, 11), (11, 11), (7, 7)]
        for (x, y) in pos:
            pygame.draw.rect(screen, color, (
            REC_SIZE // 2 + x * REC_SIZE - rec_size // 2, REC_SIZE // 2 + y * REC_SIZE - rec_size // 2, rec_size,
            rec_size))
#Button类，用来绘制按钮和按钮上的文字，self.button_color 保存2种颜色，表示按钮enable或disable时的颜色。
class Button():
    def __init__(self, screen, text, x, y, color, enable):
        self.screen = screen
        self.width = BUTTON_WIDTH
        self.height = BUTTON_HEIGHT
        self.button_color = color
        self.text_color = (255, 255, 255)
        self.enable = enable
        self.font = pygame.font.SysFont('simsunnsimsun', BUTTON_HEIGHT * 2 // 3)
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.topleft = (x, y)
        self.text = text
        self.init_msg()
    def init_msg(self):
        if self.enable:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[0])
        else:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[1])
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def draw(self):
        if self.enable:
            self.screen.fill(self.button_color[0], self.rect)
        else:
            self.screen.fill(self.button_color[1], self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)
#开始按钮
class StartButton(Button):
    def __init__(self, screen, text, x, y):
        super().__init__(screen, text, x, y, [(107,194,53),(174, 221, 129)], True)
    def click(self, game):
        if self.enable:
            game.start()
            game.winner = None
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[1])
            self.enable = False
            return True
        return False
    def unclick(self):
        if not self.enable:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[0])
            self.enable = True
#认输按钮（其和开始按钮同一时间只有一个可以点击，点击一个就要调用另外一个的unclick函数）
class GiveupButton(Button):
    def __init__(self, screen, text, x, y):
        super().__init__(screen, text, x, y, [(254,67,101), (252,157,154)], False)
    def click(self, game):
        if self.enable:
            game.is_play = False
            if game.winner is None:
                game.winner = game.map.reverseTurn(game.player)
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[1])
            self.enable = False
            return True
        return False
#按钮锁定unclick函数
    def unclick(self):
        if not self.enable:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[0])
            self.enable = True
#初始化棋盘及相关参数
class Game():
    def __init__(self, caption):
        pygame.init()
        self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()
        self.buttons = []
        self.buttons.append(StartButton(self.screen, '开始战斗', MAP_WIDTH + 30, 15))
        self.buttons.append(GiveupButton(self.screen, '发起投降', MAP_WIDTH + 30, BUTTON_HEIGHT + 45))
        self.is_play = False
        self.map = Map(CHESS_LEN, CHESS_LEN)
        self.player = MAP_ENTRY_TYPE.MAP_PLAYER_ONE
        self.action = None
        self.AI = ChessAI(CHESS_LEN)
        self.useAI = False
        self.winner = None
    def start(self):
        self.is_play = True
        self.player = MAP_ENTRY_TYPE.MAP_PLAYER_ONE
        self.map.reset()
    def play(self):
        self.clock.tick(60)
        background23 = pygame.image.load("bgmain.jpg")
        self.screen.blit(background23, (0, 0))
        background22 = pygame.image.load("bgbian.jpg")
        self.screen.blit(background22, (MAP_WIDTH, 0))
        for button in self.buttons:
            button.draw()
        if self.is_play and not self.isOver():
            if self.useAI:
                x, y = self.AI.findBestChess(self.map.map, self.player)
                self.checkClick(x, y, True)
                self.useAI = False
            if self.action is not None:
                self.checkClick(self.action[0], self.action[1])
                self.action = None
            if not self.isOver():
                self.changeMouseShow()
        if self.isOver():
            self.showWinner()
        self.map.drawBackground(self.screen)
        self.map.drawChess(self.screen)
#修改鼠标显示
    def changeMouseShow(self):
        map_x, map_y = pygame.mouse.get_pos()
        x, y = self.map.MapPosToIndex(map_x, map_y)
        if self.map.isInMap(map_x, map_y) and self.map.isEmpty(x, y):
            pygame.mouse.set_visible(False)
            light_red = (21, 174, 103)
            pos, radius = (map_x, map_y), CHESS_RADIUS
            pygame.draw.circle(self.screen, light_red, pos, radius)
        else:
            pygame.mouse.set_visible(True)

    def checkClick(self, x, y, isAI=False):
        self.map.click(x, y, self.player)
        if self.AI.isWin(self.map.map, self.player):
            self.winner = self.player
            self.click_button(self.buttons[1])
        else:
            self.player = self.map.reverseTurn(self.player)
            if not isAI:
                self.useAI = True
#处理鼠标输入
    def mouseClick(self, map_x, map_y):
        if self.is_play and self.map.isInMap(map_x, map_y) and not self.isOver():
            x, y = self.map.MapPosToIndex(map_x, map_y)
            if self.map.isEmpty(x, y):
                self.action = (x, y)
    def isOver(self):
        return self.winner is not None
    def showWinner(self):
        def showPIC(screen):
            if self.winner == MAP_ENTRY_TYPE.MAP_PLAYER_ONE:
                background1 = pygame.image.load("manwin.jpg")
                screen.blit(background1, (MAP_WIDTH + 25, SCREEN_HEIGHT-200))
            else:
                background2 = pygame.image.load("comwin.jpg")
                screen.blit(background2, (MAP_WIDTH + 25, SCREEN_HEIGHT-200))
        showPIC(self.screen)
        pygame.mouse.set_visible(True)
    def click_button(self, button):
        if button.click(self):
            for tmp in self.buttons:
                if tmp != button:
                    tmp.unclick()
    def check_buttons(self, mouse_x, mouse_y):
        for button in self.buttons:
            if button.rect.collidepoint(mouse_x, mouse_y):
                self.click_button(button)
                break
#获取鼠标点击事件，判断是点击棋盘还是点击按钮。
game = Game("五子棋")
while True:
    game.play()
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            game.mouseClick(mouse_x, mouse_y)
            game.check_buttons(mouse_x, mouse_y)