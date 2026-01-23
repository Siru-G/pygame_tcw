import cfg
import sys
import random
import pygame
from modules import *


'''main'''
def main(highest_score, highest_count):
    # 游戏初始化
    pygame.init()
    screen = pygame.display.set_mode(cfg.SCREENSIZE)
    pygame.display.set_caption('tcw_game')
    
    # 导入所有声音文件
    sounds = {}
    for key, value in cfg.AUDIO_PATHS.items():
        sounds[key] = pygame.mixer.Sound(value)
    # 游戏开始界面
    GameStartInterface(screen, sounds, cfg)
    # 记分板
    score = 0
    score_board = Scoreboard(cfg.IMAGE_PATHS['numbers'], position=(1060, 15), bg_color=None)
    highest_score = highest_score
    highest_score_board = Scoreboard(cfg.IMAGE_PATHS['numbers'], position=(920, 15), bg_color=None, is_highest=True)
    # 计数板
    count = 0
    count_board = Countboard(cfg.IMAGE_PATHS['numbers'], position=(1060, 35), bg_color=None)
    highest_count = highest_count
    highest_count_board = Countboard(cfg.IMAGE_PATHS['numbers'], position=(920, 35), bg_color=None, is_highest=True)

    player = Player(cfg.IMAGE_PATHS['player'])
    ground = Ground(cfg.IMAGE_PATHS['ground'], position=(0, cfg.SCREENSIZE[1]))
    # 加载背景图片
    background = pygame.image.load(cfg.IMAGE_PATHS['background'])
    background = pygame.transform.scale(background, cfg.SCREENSIZE)
    background_rect = background.get_rect()
    # 定义sprite
    cloud_sprites_group = pygame.sprite.Group()
    droid_sprites_group = pygame.sprite.Group()
    vulture_sprites_group = pygame.sprite.Group()
    blast_sprites_group = pygame.sprite.Group()
    add_obstacle_timer = 0
    score_timer = 0
    # 游戏主循环
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    player.jump(sounds)
                    #print(player.rect.top)
                elif event.key == pygame.K_DOWN:
                    player.strike()
            elif event.type == pygame.KEYUP and event.key == pygame.K_DOWN:
                player.unstrike()
        
        # --随机添加云
        if len(cloud_sprites_group) < 2 and random.randrange(0, 300) == 10:
            cloud_sprites_group.add(Cloud(cfg.IMAGE_PATHS['cloud'], position=(cfg.SCREENSIZE[0], random.randrange(50, 300))))
        # --随机添加地面/空中机器人
        add_obstacle_timer += 1
        if add_obstacle_timer > random.randrange(80, 150):
            add_obstacle_timer = 0
            random_value = random.randrange(0, 10)
            if random_value >= 4 and random_value <= 9:
                droid_sprites_group.add(Droid(cfg.IMAGE_PATHS['droid'], speed=ground.speed))
            else:
                position_ys = [cfg.SCREENSIZE[1]*0.82, cfg.SCREENSIZE[1]*0.75, cfg.SCREENSIZE[1]*0.60, cfg.SCREENSIZE[1]*0.40]
                rspeed = random.randrange(35, 50)
                rspeed /= 10
                vulture_sprites_group.add(Vulture(cfg.IMAGE_PATHS['vulture'], position=(1200, random.choice(position_ys)), speed=ground.speed-rspeed))
        
        # --更新游戏元素
        player.update()
        ground.update()
        cloud_sprites_group.update()

        droid_sprites_group.update(blast_sprites_group)
        vulture_sprites_group.update()
        blast_sprites_group.update()

        if count > highest_count:
            highest_count = count
        score_timer += 1
        if score_timer > (cfg.FPS//12):
            score_timer = 0
            score += 1
            score = min(score, 99999)
            if score > highest_score:
                highest_score = score
            #if score % 100 == 0:
            #    sounds['point'].play()
            if score % 200 == 0:
                ground.speed -= 1
                for item in cloud_sprites_group:
                    item.speed -= 1
                for item in droid_sprites_group:
                    item.speed -= 1
                for item in vulture_sprites_group:
                    item.speed -= 1
                    
        # --碰撞检测
        for item in droid_sprites_group:
            if pygame.sprite.collide_mask(player, item):
                if player.is_striking:  # 如果在击打状态
                    if item.exploding:
                        continue
                    sounds['point'].play()  # 播放清除音效
                    item.explode_and_kill()  # 清除障碍物
                    count += 1
                    score += 10
                else:  # 正常状态
                    player.die(sounds)
                    player.update()
        for item in vulture_sprites_group:
            if pygame.sprite.collide_mask(player, item):
                player.die(sounds)
                player.update()
        for blast in blast_sprites_group:
            if pygame.sprite.collide_mask(player, blast):
                if player.is_striking:  # 击打状态
                    blast.reflect(new_direction=1)  # 向右反弹
                    sounds['jump'].play()  # 格挡音效
                else:  # 正常状态
                    player.die(sounds)
                    player.update()
                    blast.kill()

        for blast in blast_sprites_group:
            if blast.is_reflected:  # 只检测反弹的子弹
                for droid in droid_sprites_group:
                    if pygame.sprite.collide_mask(blast, droid) and not droid.exploding:
                        # 反弹子弹击中
                        blast.kill()
                        is_droid_dead = droid.hit_by_reflected_blast()
                        
                        if is_droid_dead:
                            score += 10  # 击杀奖励
                            sounds['point'].play()
                            count += 1
                            #print("被消灭！")
                        else:
                            score += 5   # 击中奖励

        # --将游戏元素画到屏幕上
        screen.blit(background, background_rect)
        cloud_sprites_group.draw(screen)
        ground.draw(screen)

        droid_sprites_group.draw(screen)
        vulture_sprites_group.draw(screen)
        player.draw(screen)
        blast_sprites_group.draw(screen)  

        score_board.set(score)
        highest_score_board.set(highest_score)
        score_board.draw(screen)
        highest_score_board.draw(screen)

        count_board.set(count)
        highest_count_board.set(highest_count)
        count_board.draw(screen)
        highest_count_board.draw(screen)

        # --更新屏幕
        pygame.display.update()
        clock.tick(cfg.FPS)
        # --游戏是否结束
        if player.is_dead:
            break
    # 游戏结束界面
    return GameEndInterface(screen, cfg), highest_score, highest_count


'''run'''
if __name__ == '__main__':
    highest_score = 0
    highest_count = 0
    while True:
        flag, highest_score, highest_count = main(highest_score, highest_count)
        if not flag: break
