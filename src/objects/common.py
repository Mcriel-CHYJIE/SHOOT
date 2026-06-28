"""
=============================================================================
 基础对象模块 — 子弹/奖励/动画
=============================================================================
 所属功能块: 游戏实体
 功能描述  : 定义 Bullet（含追踪弹）、Reward、TrackingBullet、Animation
             所有实体共用的基础游戏对象
=============================================================================
"""
import math
import random
import pygame

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.core.resource_manager import load_image_scaled, load_sound


class Bullet(pygame.sprite.Sprite):
    """子弹类 - 实现子弹的显示、移动和动画效果"""

    _bullet_config = {
        'player': {'img': ('images', 'Bullet', '2.png'), 'size': (84, 9)},
        'enemy': {'img': ('images', 'Bullet', '1.png'), 'size': (68, 9)},
        'reward': {'img': ('images', 'Bullet', '0.png'), 'size': (68, 9)},
    }

    def __init__(self, x, y, dx, dy, range_, color, player, bullet_type='player'):
        super().__init__()
        self.bullet_type = bullet_type
        self.dx = dx
        self.dy = dy
        self.range = range_
        self.player = player
        self.initial_x = x
        self.initial_y = y

        cfg = self._bullet_config.get(bullet_type, self._bullet_config['player'])
        self.frame_width, self.frame_height = cfg['size']

        try:
            sheet = load_image_scaled(*cfg['img'], scale_factor=1.0)
        except (pygame.error, FileNotFoundError):
            self._fallback_circle(x, y, color)
            return

        self.bullet_sheet = sheet
        self.cols = sheet.get_width() // self.frame_width
        self.rows = sheet.get_height() // self.frame_height
        self.current_frame = 0
        self.original_image = self._get_frame(0)
        self.image = pygame.transform.scale(
            self.original_image, (self.frame_width // 2, self.frame_height // 2)
        )
        self.rect = self.image.get_rect(center=(x, y))
        self.animation_speed = 5
        self.animation_counter = 0
        self._rotate_to_direction()

    def _fallback_circle(self, x, y, color):
        """回退：绘制简单圆形子弹"""
        self.image = pygame.Surface((3, 3), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, color, (2, 2), 3, 3)
        self.rect = self.image.get_rect(center=(x, y))

    def _get_frame(self, idx):
        """获取精灵图的指定帧"""
        if idx >= self.rows * self.cols:
            idx = 0
        row, col = idx // self.cols, idx % self.cols
        rect = pygame.Rect(col * self.frame_width, row * self.frame_height,
                           self.frame_width, self.frame_height)
        frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
        frame.blit(self.bullet_sheet, (0, 0), rect)
        return frame

    def _rotate_to_direction(self):
        """旋转子弹朝向移动方向"""
        if self.dx != 0 or self.dy != 0:
            angle = math.degrees(math.atan2(self.dy, self.dx)) + 180
            img = pygame.transform.scale(
                self.original_image, (self.frame_width // 2, self.frame_height // 2)
            )
            self.image = pygame.transform.rotate(img, -angle)
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        """更新位置和动画"""
        self.rect.x += self.dx
        self.rect.y += self.dy

        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.current_frame = (self.current_frame + 1) % (self.rows * self.cols)
            self.original_image = self._get_frame(self.current_frame)
            self.animation_counter = 0

        self._rotate_to_direction()

        if (self.rect.left < 0 or self.rect.right > SCREEN_WIDTH or
                self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT or
                math.hypot(self.rect.centerx - self.initial_x,
                           self.rect.centery - self.initial_y) > self.range):
            self.kill()


class TrackingBullet(Bullet):
    """追踪子弹 - 追踪最近目标"""

    def __init__(self, x, y, dx, dy, range_, color, player,
                 enemies_group, bosses_group=None, bullet_type='reward'):
        super().__init__(x, y, dx, dy, range_, color, player, bullet_type)
        self.enemies_group = enemies_group
        self.bosses_group = bosses_group
        self.tracking_speed = 0.2
        self.max_speed = math.hypot(dx, dy)

    def update(self):
        super().update()
        targets = list(self.enemies_group or [])
        if self.bosses_group:
            targets.extend(self.bosses_group)

        closest, min_dist = None, float('inf')
        for t in targets:
            d = math.hypot(t.rect.centerx - self.rect.centerx,
                           t.rect.centery - self.rect.centery)
            if d < min_dist:
                min_dist, closest = d, t

        if closest and min_dist < 500:
            dx = closest.rect.centerx - self.rect.centerx
            dy = closest.rect.centery - self.rect.centery
            dist = math.hypot(dx, dy) or 1
            self.dx += (dx / dist) * self.tracking_speed
            self.dy += (dy / dist) * self.tracking_speed
            speed = math.hypot(self.dx, self.dy)
            if speed > 0:
                self.dx = self.dx / speed * self.max_speed
                self.dy = self.dy / speed * self.max_speed


class Reward(pygame.sprite.Sprite):
    """奖励类 - 实现奖励的显示、移动和收集效果"""

    def __init__(self, player):
        super().__init__()
        self.player = player
        self.score_value = 50
        self.speed = 2
        self.direction = random.uniform(0, 2 * math.pi)
        self.rotation_speed = 1.5
        self.current_rotation = 0

        self.reward_image = load_image_scaled('images', 'reward.png', scale_factor=1.0)
        self.resized_image = pygame.transform.scale(self.reward_image, (15, 15))
        self.image = self.resized_image
        self.rect = self.image.get_rect()
        self.collision_rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(0, SCREEN_HEIGHT - self.rect.height)
        self._update_collision_rect()

    def _update_collision_rect(self):
        self.collision_rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        """更新旋转和移动"""
        self.current_rotation = (self.current_rotation + self.rotation_speed) % 360
        self.image = pygame.transform.rotate(self.resized_image, -self.current_rotation)

        self.rect.x += math.cos(self.direction) * self.speed
        self.rect.y += math.sin(self.direction) * self.speed

        if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
            self.direction = (self.direction + math.pi) % (2 * math.pi)
        if self.rect.bottom > SCREEN_HEIGHT or self.rect.top < 0:
            self.direction = (self.direction + math.pi) % (2 * math.pi)

        self._update_collision_rect()

    def explode(self):
        """奖励爆炸 - 向四周发射子弹并播放音效"""
        for i in range(0, 360, 15):
            a = math.radians(i)
            self.player.bullets_group.add(Bullet(
                self.rect.centerx, self.rect.centery,
                math.cos(a) * 5, math.sin(a) * 5,
                1000, (255, 255, 255), self.player, 'reward'
            ))
        try:
            s = load_sound('sounds', 'reward.mp3')
            s.set_volume(0.05)
            s.play()
        except pygame.error:
            pass


class Animation:
    """动画类 - 精灵图动画播放"""

    def __init__(self, image_path, frames, duration):
        self.sheet = load_image_scaled('images', image_path, scale_factor=1.0)
        self.frames = []
        self.duration = duration
        self.current_frame = 0
        self.last_update_time = pygame.time.get_ticks()
        self.frame_width = self.sheet.get_width() // frames[0]
        self.frame_height = self.sheet.get_height() // frames[1]

        for y in range(frames[1]):
            for x in range(frames[0]):
                self.frames.append(self.sheet.subsurface(pygame.Rect(
                    x * self.frame_width, y * self.frame_height,
                    self.frame_width, self.frame_height
                )))
        self.rect = self.frames[0].get_rect()

    def update(self):
        """切换到下一帧"""
        now = pygame.time.get_ticks()
        if now - self.last_update_time > self.duration:
            self.last_update_time = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)
        return self.frames[self.current_frame]

    def get_current_frame(self):
        """获取当前帧，动画结束返回 None"""
        frame = self.update()
        return None if self.current_frame == len(self.frames) - 1 else frame

    def get_rect(self):
        return self.rect
