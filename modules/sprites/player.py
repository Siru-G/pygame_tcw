import pygame


'''主控'''
class Player(pygame.sprite.Sprite):
    def __init__(self, imagepaths, position=(80, 552), size=(90, 130), **kwargs):
        pygame.sprite.Sprite.__init__(self)
        
        # 导入单张图片（按顺序）
        self.images = []
        # 假设 imagepaths 现在是包含5张图片路径的列表
        for i in range(3):
            # 加载每张单独的图片
            img = pygame.image.load(imagepaths[i])
            # 缩放图片
            self.images.append(pygame.transform.scale(img, size))
        size = (92, 130)
        img = pygame.image.load(imagepaths[3])
        self.images.append(pygame.transform.scale(img, size))
        size = (90, 144)
        img = pygame.image.load(imagepaths[4])
        self.images.append(pygame.transform.scale(img, size))
        # 低头状态的图片（额外的2张）
        strike_images = []
        img = pygame.image.load(imagepaths[5])
        strike_size = (130, 130)  # 图片尺寸不同
        strike_images.append(pygame.transform.scale(img, strike_size))
        img = pygame.image.load(imagepaths[6])
        strike_size = (144, 130)  # 图片尺寸不同
        strike_images.append(pygame.transform.scale(img, strike_size))
        img = pygame.image.load(imagepaths[7])
        strike_size = (92, 130)  # jump
        strike_images.append(pygame.transform.scale(img, strike_size))
        
        # 合并所有图片
        self.images.extend(strike_images)
        
        self.image_idx = 0
        self.image = self.images[self.image_idx]
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.bottom = position
        self.mask = pygame.mask.from_surface(self.image)
        
        # 定义一些必要的变量
        self.init_position = position
        self.refresh_rate = 5
        self.refresh_counter = 0
        self.speed = 15
        self.gravity = 0.7
        self.is_jumping = False
        self.is_striking = False
        self.is_dead = False
        self.movement = [0, 0]
        # 新增跳跃次数限制
        self.max_jumps = 3  # 最大连跳次数
        self.jump_count = 0  # 当前跳跃次数
        self.can_jump_again = False  # 是否可以再次跳跃
        '''
        # 新增击打时长限制
        self.strike_duration = 0  # 当前持续时间
        self.max_strike_duration = 20  # 最大时长
        '''

    '''跳跃'''
    def jump(self, sounds):
        if self.rect.top < -100:
            return
        if not self.can_jump():
            return
        
        sounds['jump'].play()
        self.is_jumping = True
        self.movement[1] = -1 * self.speed

        # 增加跳跃计数
        self.jump_count += 1
        
    
    '''检查是否可以跳跃'''
    def can_jump(self):
        # 如果已经达到最大跳跃次数，不能跳跃
        if self.jump_count >= self.max_jumps:
            return False
        
        # 如果已经可以再次跳跃，允许跳跃
        if self.can_jump_again:
            return True
        
        # 如果是第一次跳跃或者在地面上，允许跳跃
        if self.jump_count == 0 or (not self.is_jumping and self.rect.bottom >= self.init_position[1]):
            return True
        
        return True
    
    '''低头'''
    def strike(self):
        if self.is_jumping:
            return
        
        # 如果是重新开始，重置计时器
        if not self.is_striking:
            self.strike_duration = 0

        self.is_striking = True
    
    '''停止击打'''
    def unstrike(self):
        self.is_striking = False
        self.strike_duration = 0  # 重置计时器

    '''死掉了'''
    def die(self, sounds):
        sounds['die'].play()
        self.is_dead = True
    
    '''将恐龙画到屏幕'''
    def draw(self, screen):
        screen.blit(self.image, self.rect)
    
    '''载入当前状态的图片'''
    def loadImage(self):
        self.image = self.images[self.image_idx]
        rect = self.image.get_rect()
        rect.left, rect.top = self.rect.left, self.rect.top
        self.rect = rect
        self.mask = pygame.mask.from_surface(self.image)
    
    '''更新'''
    def update(self):
        if self.is_striking:
            self.strike_duration += 1
        '''
        # 检查是否超过最大时长
        if self.strike_duration >= self.max_strike_duration:
            self.unstrike()
        '''
        if self.is_dead:
            self.image_idx = 4  # 第5张图片：死亡状态
            self.loadImage()
            return
        
        if self.is_jumping:
            self.movement[1] += self.gravity
            self.image_idx = 7  # 第1张图片：跳跃/站立状态
            self.loadImage()
            self.rect = self.rect.move(self.movement)
            if self.rect.bottom >= self.init_position[1]:
                self.rect.bottom = self.init_position[1]
                self.is_jumping = False
                # 落地后重置跳跃状态
                if self.jump_count > 0:
                    self.jump_count = 0  # 重置跳跃计数
                    self.can_jump_again = True  # 可以再次跳跃
                    #print("落地，跳跃计数重置")  # 调试信息
        
        elif self.is_striking:
            if self.refresh_counter % self.refresh_rate == 0:
                self.refresh_counter = 0
                # 在击打动画的两张图片间切换（第6和第7张）
                self.image_idx = 5 if self.image_idx == 6 else 6
                self.loadImage()
        else:
            self.unstrike()
            if self.refresh_counter % self.refresh_rate == 0:
                self.refresh_counter = 0
                # 行走动画循环（第2、3、4、1张图片）
                if self.image_idx == 1:
                    self.image_idx = 2
                elif self.image_idx == 2:
                    self.image_idx = 0
                elif self.image_idx == 0:
                    self.image_idx = 3
                else:
                    self.image_idx = 1
                self.loadImage()
        
        self.refresh_counter += 1
