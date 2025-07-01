# -*- coding: utf-8 -*-

import pygame
import random
import os

#基本設定
WIDTH,HEIGH = 288,512
FPS = 30

#遊戲設定
pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGH))
pygame.display.set_caption("Flappy Bird")
CLOCK = pygame.time.Clock()

#遊戲圖片素材
IMAGES = {}
for images in os.listdir("Flappy_Bird/Game"):
    name,extension = os.path.splitext(images)
    path = os.path.join("Flappy_Bird/Game", images)
    IMAGES[name] = pygame.image.load(path)

#計算地板高度
FLOOR_Y = HEIGH - IMAGES["floor"].get_height()

#音效設定
AUDIO = {}
for audio in os.listdir("Flappy_Bird/Sound"):
    name,extension = os.path.splitext(audio)
    path = os.path.join("Flappy_Bird/Sound", audio)
    AUDIO[name] = pygame.mixer.Sound(path)
    AUDIO[name].set_volume(0.4) #調整音量

#背景音樂，使用mixer.music播放整首音樂
pygame.mixer.music.load("Flappy_Bird/Sound/bgm.wav")
pygame.mixer.music.set_volume(0.1)  #調整音量
pygame.mixer.music.play(-1)  # -1 表示無限循環播放

#主要函數
def main():
    while True:
        AUDIO["swoosh"].play()
        #建立鳥的圖
        IMAGES["birds"] = [IMAGES["bird_up"],IMAGES["bird_mid"],IMAGES["bird_down"]]
        #建立水管圖(上下翻轉)
        pipe = IMAGES["pipe_green"]
        IMAGES["pipe"] = [pipe,pygame.transform.flip(pipe,False,True)]
        menu_window()               #開始畫面
        result = game_window()      #遊戲主畫面
        end_window(result)          #結束畫面

#開始畫面
def menu_window():
    floor_gap = IMAGES["floor"].get_width() - WIDTH
    floor_x = 0

    guid_x = (WIDTH - IMAGES["guid"].get_width()) / 2
    guid_y = (HEIGH - IMAGES["guid"].get_height()) / 2

    bird_x = WIDTH * 0.2
    bird_y = (HEIGH - IMAGES["bird_up"].get_height()) / 2
    bird_y_vel = 1
    bird_y_range = [bird_y-8, bird_y+8]

    idx = 0
    repeat = 5
    frames = [0]*repeat + [1]*repeat + [2]*repeat + [1]*repeat  #飛行動作循環

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return  #開始遊戲

        #地板滾動
        floor_x -= 4
        if floor_x <= -floor_gap:
            floor_x = 0

        #鳥上下移動(漂浮動畫)
        bird_y += bird_y_vel
        if bird_y < bird_y_range[0] or bird_y > bird_y_range[1]:
            bird_y_vel *= -1

        idx += 1
        idx%=len(frames)

        #劃出畫面
        SCREEN.blit(IMAGES["day"], (0, 0))
        SCREEN.blit(IMAGES["floor"], (floor_x, FLOOR_Y))
        SCREEN.blit(IMAGES["guid"], (guid_x, guid_y))
        SCREEN.blit(IMAGES["birds"][frames[idx]], (bird_x, bird_y))
        pygame.display.update()
        CLOCK.tick(FPS)

#遊戲主畫面
def game_window():

    score = 0

    AUDIO["wing"].play()
    floor_gap = IMAGES["floor"].get_width() - WIDTH
    floor_x = 0

    bird = Bird(WIDTH*0.2,HEIGH*0.4)

    #建立一組初始水管
    n_pairs = 4
    distance = 150
    pipe_gap = 100
    pipe_group = pygame.sprite.Group()
    for i in range(n_pairs):
        pipe_y = random.randint(int(HEIGH*0.3),int(HEIGH*0.7))
        pipe_up = Pipe(WIDTH+i*distance,pipe_y,True)
        pipe_down = Pipe(WIDTH+i*distance,pipe_y-pipe_gap,False)
        pipe_group.add(pipe_up)
        pipe_group.add(pipe_down)

    while True:
        flap = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    flap = True
                    AUDIO["wing"].play()

        #地板滾動
        floor_x -= 4
        if floor_x <= -floor_gap:
            floor_x = 0

        bird.update(flap)   #更新鳥的位置與動畫

        #檢查第一隊水管是否超出螢幕,並補上新的
        first_pipe_up = pipe_group.sprites()[0]
        first_pipe_down = pipe_group.sprites()[1]
        if first_pipe_up.rect.right < 0:
            pipe_y = random.randint(int(HEIGH * 0.3), int(HEIGH * 0.7))
            new_pipes_up = Pipe(first_pipe_up.rect.x+n_pairs*distance,pipe_y,True)
            new_pipes_down = Pipe(first_pipe_down.rect.x+n_pairs*distance,pipe_y-pipe_gap,False)
            pipe_group.add(new_pipes_up)
            pipe_group.add(new_pipes_down)
            first_pipe_up.kill()
            first_pipe_down.kill()

        pipe_group.update()

        #判斷失敗(掉下去或是撞到水管)
        if bird.rect.y > FLOOR_Y or bird.rect.y < 0 or pygame.sprite.spritecollideany(bird, pipe_group):
            bird_dying = True
            AUDIO["hit"].play()
            AUDIO["die"].play()
            result = {"bird":bird,"pipe_group":pipe_group,"score":score}
            return result

        #因為使用了精靈類所以可以不用
        #for pipe in pipe_group.sprites():
            #right_to_left = max(bird.rect.right,pipe.rect.right) - min(bird.rect.left,pipe.rect.left)
            #bottom_to_top = max(bird.rect.bottom,pipe.rect.bottom) - min(bird.rect.top,pipe.rect.top)
            #if right_to_left < bird.rect.width+pipe.rect.width and bottom_to_top < bird.rect.height + pipe.rect.height:
                #AUDIO["hit"].play()
                #AUDIO["die"].play()
                #result = {"bird":bird,"pipe_group":pipe_group}
                #return result

        #判斷加分(通過水管中間)
        if bird.rect.left + first_pipe_up.x_vel <= first_pipe_up.rect.centerx < bird.rect.left:
            AUDIO["point"].play()
            score += 1
        #劃出畫面
        SCREEN.blit(IMAGES["day"], (0,0))
        pipe_group.draw(SCREEN)
        SCREEN.blit(IMAGES["floor"], (floor_x, FLOOR_Y))
        show_score(score)
        SCREEN.blit(bird.image,bird.rect)
        pygame.display.update()
        CLOCK.tick(FPS)

#結束畫面
def end_window(result):
    gameover_x = (WIDTH - IMAGES["gameover"].get_width())/2
    gameover_y = (FLOOR_Y - IMAGES["gameover"].get_height()) / 2

    bird = result["bird"]
    pipe_group = result["pipe_group"]

    while True:
        if bird.dying:
            bird.go.die()   #播放死亡動畫
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    pygame.mixer.music.stop()   #死亡停止撥放背景音樂
                    return

        SCREEN.blit(IMAGES["day"], (0,0))
        pipe_group.draw(SCREEN)
        SCREEN.blit(IMAGES["floor"], (0, FLOOR_Y))
        SCREEN.blit(IMAGES["gameover"], (gameover_x, gameover_y))
        show_score(result["score"])
        SCREEN.blit(bird.image,bird.rect)
        pygame.display.update()
        CLOCK.tick(FPS)

#顯示分數
def show_score(score):
    score_str = str(score)
    n = len(score_str)
    w = IMAGES["0"].get_width() * 1.1
    x = (WIDTH - n * w) / 2
    y = HEIGH * 0.2
    for number in score_str:
        SCREEN.blit(IMAGES[number], (x, y))
        x += w

#小鳥類別
class Bird:
    def __init__(self, x, y):
        self.frames = [0]*5 + [1]*5 + [2]*5 + [1]*5 #飛行動畫
        self.idx = 0
        self.images = IMAGES["birds"]   #取得三種小鳥圖片
        self.image = self.images[self.frames[self.idx]]
        self.rect = self.image.get_rect()   #取得圖片的位置與大小
        self.rect.x = x
        self.rect.y = y
        #垂直速度(初始為向上飛)
        self.y_vel = -10
        self.max_y_vel = 10 #向下最大速度
        self.gravity = 1    #每幀增加重力
        #旋轉角度設定(飛的時候會有旋轉的感覺)
        self.rotate = 45    #初始角度
        self.max_rotate = -20   #最低角度限制
        self.rotate_vel = -3    #每幀旋轉速度
        self.y_vel_after_flap = -10 #按下空白建後的跳躍速度(向上衝)
        self.rotate_after_flap = 45 #按下後立即抬高的角度
        self.dying = False

    def update(self,flap=False):
        if flap:
            self.y_vel = self.y_vel_after_flap  #向上的速度
            self.rotate = self.rotate_after_flap    #抬頭旋轉

        #加上重力,家道最大速度限制
        self.y_vel = min(self.y_vel+self.gravity, self.max_y_vel)
        self.rect.y += self.y_vel   #根據速度改變y的位置(往上或往下)
        #小鳥旋轉角度逐幀下降,但不能低於最大限制(避免頭朝下太誇張)
        self.rotate = max(self.rotate+self.rotate_vel, self.max_rotate)
        self.idx += 1
        self.idx %= len(self.frames)
        #設定當前圖片,並根據角度旋轉
        self.image = self.images[self.frames[self.idx]]
        self.image = pygame.transform.rotate(self.image, self.rotate)

    def go_die(self):
        #死亡動畫,讓小鳥往地板落
        if self.rect.y < FLOOR_Y:
            self.rect.y += self.max_y_vel
            self.rotate = -90   #小鳥死亡垂直往下
            self.image = self.images[self.frames[self.idx]]
            self.image = pygame.transform.rotate(self.image, self.rotate)
        else:
            self.dying = False  #落地停止死亡動畫

#水管類別
class Pipe(pygame.sprite.Sprite):   #繼承pygame的精靈類別
    def __init__(self, x, y,upwards=False):
        pygame.sprite.Sprite.__init__(self)
        if upwards:
            self.image = IMAGES["pipe"][0]
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.top = y
        else:
            self.image = IMAGES["pipe"][1]
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.bottom = y
        self.x_vel = -4

    def update(self):
        self.rect.x += self.x_vel   #向左移動


#遊戲主程式執行
main()
