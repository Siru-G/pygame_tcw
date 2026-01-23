
import random
import pygame
import cfg

'''地面机器人障碍'''
class Droid(pygame.sprite.Sprite):
    def __init__(self, imagepaths, position=(1200, 555), size=(125, 140), speed=-5, **kwargs):
        pygame.sprite.Sprite.__init__(self)
        # 导入图片
        self.images = []
        # 加载big图片
        size = (125, 140)
        img1 = pygame.image.load(imagepaths[0]).convert_alpha()
        self.images.append(pygame.transform.scale(img1, size))
        img1 = pygame.image.load(imagepaths[1]).convert_alpha()
        self.images.append(pygame.transform.scale(img1, size))
        # 加载small图片
        size = (85, 130)
        img2 = pygame.image.load(imagepaths[2]).convert_alpha()
        self.images.append(pygame.transform.scale(img2, size))
        img2 = pygame.image.load(imagepaths[3]).convert_alpha()
        self.images.append(pygame.transform.scale(img2, size))
        # 加载explode图片
        size = (70, 90)
        img2 = pygame.image.load(imagepaths[4]).convert_alpha()
        self.images.append(pygame.transform.scale(img2, size))
        # 随机选择一张图片
        random_value = random.randrange(0, 10)
        if random_value >= 4 and random_value <= 9:
            self.image_idx = 0
            self.image = self.images[self.image_idx]
        else:
            self.image_idx = 2
            self.image = self.images[self.image_idx]
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.bottom = position
        self.mask = pygame.mask.from_surface(self.image)
        # 定义一些必要的变量
        # 运动速度
        self.speed = speed
        # 生命值和状态
        self.health = 2  # 需要被击中两次才会死亡
        # 爆炸
        self.exploding = False
        self.explode_frame = 0
        self.explode_frames = 2  # 爆炸持续帧数
        # 切换位置
        self.switch_position = 1060  # 当x坐标小于时切换图片
        self.has_switched = False  # 是否已经切换过
        # 发射子弹相关参数
        self.shoot_timer = 90
        self.shoot_interval = 90  # 每90帧发射一次
        self.can_shoot = True     # 是否可以发射
        self.speed = speed
    
    '''载入当前状态的图片'''
    def loadImage(self):
        self.image = self.images[self.image_idx]
        rect = self.image.get_rect()
        rect.left, rect.top = self.rect.left, self.rect.top
        self.rect = rect
        self.mask = pygame.mask.from_surface(self.image)
    
    '''自定义kill方法，添加清除特效'''
    def explode_and_kill(self):
        self.exploding = True
        self.image_idx = 4  # 爆炸图片
        self.loadImage()

    '''画到屏幕上'''
    def draw(self, screen):
        screen.blit(self.image, self.rect)
    
    '''更新'''
    def update(self, blast_group):
        if self.exploding:
            # 播放爆炸动画
            self.explode_frame += 1
            if self.explode_frame >= self.explode_frames:
                super().kill()  # 动画播放完后真正移除
            return
        self.rect.x += self.speed
        # 检查是否到达切换位置且尚未切换
        if not self.has_switched and self.rect.right < self.switch_position:
            self.image = self.images[self.image_idx+1]  # 切换到第二张图片
            self.has_switched = True
        # 发射子弹逻辑
        if  self.rect.right < self.switch_position and self.can_shoot:
            self.shoot_timer += 1
            if self.shoot_timer >= self.shoot_interval:
                self.shoot(blast_group)
                self.shoot_timer = 0  # 重置计时器

        if self.rect.right < 0:
            self.kill()

    def shoot(self, blast_group):
        """发射子弹"""
        # 向左侧发射子弹
        if self.image_idx == 2:
            blast_position = (self.rect.left, self.rect.centery-15)
        else:
            blast_position = (self.rect.left, self.rect.centery-50)
        blast = Blast(
            position=blast_position,
            imagepaths=cfg.IMAGE_PATHS['blast'],
            size=(50, 8),  # 子弹大小
            speed=8,        # 子弹速度
            direction=-1     # 向左发射
        )
        blast_group.add(blast)
        #print("发射子弹!")  # 调试信息
    
    """被反弹子弹击中"""
    def hit_by_reflected_blast(self):
        self.health -= 1
        #print(f"被击中！剩余生命值: {self.health}")
        
        if self.health <= 0:
            self.explode_and_kill()
            return True  # 返回True表示死亡
        return False  # 返回False表示还活着

'''空中机器人障碍'''
class Vulture(pygame.sprite.Sprite):
    def __init__(self, imagepath, position, size=(180, 120), speed=-6, **kwargs):
        pygame.sprite.Sprite.__init__(self)
        # 导入并缩放图片
        self.image = pygame.transform.scale(pygame.image.load(imagepath), size)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.centery = position
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = speed
    
    '''画到屏幕上'''
    def draw(self, screen):
        screen.blit(self.image, self.rect)
    
    '''更新'''
    def update(self):
        # 只处理移动逻辑
        self.rect.x += self.speed
        if self.rect.right < 0:
            self.kill()

class Blast(pygame.sprite.Sprite):
    def __init__(self, imagepaths, position, size=(50, 8), speed=8, direction=-1, is_reflected=False, **kwargs):
        pygame.sprite.Sprite.__init__(self)
        # 导入并缩放图片
        self.images = []
        # 0: red
        img1 = pygame.image.load(imagepaths[0]).convert_alpha()
        self.images.append(pygame.transform.scale(img1, size))
        # 1: blue
        img2 = pygame.image.load(imagepaths[1]).convert_alpha()
        self.images.append(pygame.transform.scale(img2, size))
        # 选择图片，敌方选红，反弹用蓝
        if direction == -1:
            self.image_idx = 0 
        else:
            self.image_idx = 1

        self.image = self.images[self.image_idx]
        self.rect = self.image.get_rect()
        self.rect.right, self.rect.centery = position
        self.mask = pygame.mask.from_surface(self.image)
        
        self.speed = speed
        self.direction = direction
        self.lifetime = 100  # 存在时间（帧数）
        self.timer = 0
        self.is_reflected = is_reflected  # 是否是反弹的子弹
    
    '''画到屏幕上'''
    def draw(self, screen):
        screen.blit(self.image, self.rect)
    
    ''''''
    '''更新'''
    def update(self):
        # 只处理移动逻辑
        self.rect.x += self.speed*self.direction*2
        # 更新时间
        self.timer += 1
        
        # 超过生命周期或移出屏幕时移除
        if (self.timer >= self.lifetime or 
            self.rect.right < 0 or 
            self.rect.left > cfg.SCREENSIZE[0]):
            self.kill()

    """反弹子弹"""
    def reflect(self, new_direction=1):
        self.direction = new_direction
        self.is_reflected = True
        self.image = self.images[1]
        self.speed += 1  # 反弹后速度加快