"""
=============================================================================
 敌人实体模块 — 普通敌人与射击型敌人
=============================================================================
 所属功能块: 游戏实体
 功能描述  : 实现普通敌人（追踪/躲避/侧移 AI）和射击型敌人（保持距离射击）
=============================================================================
"""
import math
import random
import pygame

from src.objects.common import Bullet
from src.config import *
from src.core.resource_manager import load_image_scaled


class DyingEnemy(pygame.sprite.Sprite):
    """正在死亡的敌人 - 闪烁动画效果"""

    def __init__(self, original_enemy):
        super().__init__()
        self.original_image = original_enemy.original_image
        self.image = original_enemy.image.copy()
        self.rect = original_enemy.rect.copy()
        self.collision_rect = original_enemy.collision_rect.copy()
        self.direction_to_player = getattr(original_enemy, 'direction_to_player', 0)

        self.death_time = pygame.time.get_ticks()
        self.death_duration = 1000
        self.flash_interval = 100
        self.last_flash_time = self.death_time
        self.visible = True
        self.is_dead = True
        self._update_image()

    def _update_image(self):
        if self.visible:
            rot = pygame.transform.rotate(self.original_image, -self.direction_to_player)
            rot.set_colorkey(None)
            self.image = rot
        else:
            self.image = pygame.Surface(self.original_image.get_size(), pygame.SRCALPHA)

    def update(self):
        """更新闪烁动画，返回 True 表示动画结束"""
        now = pygame.time.get_ticks()
        if now - self.last_flash_time >= self.flash_interval:
            self.visible = not self.visible
            self.last_flash_time = now
        self._update_image()
        if now - self.death_time >= self.death_duration:
            self.kill()
            return True
        return False


class Enemy(pygame.sprite.Sprite):
    """普通敌人 - 追踪、躲避、侧移 AI"""

    # 行为权重
    BEHAVIOR_WEIGHTS = [
        (0, 0.4),   # 追踪 40%
        (1, 0.3),   # 躲避 30%
        (2, 0.3),   # 侧移 30%
    ]

    def __init__(self, player):
        super().__init__()
        self.player = player
        self.speed = ENEMY_SPEED
        self.direction_to_player = 0
        self.health = 1
        self.is_dead = False

        # 图像
        img = load_image_scaled('images', 'airship', '0.png', scale_factor=1.0)
        self.original_image = pygame.transform.scale(img, (35, 35))
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(-32, 0)

        # 行为
        self.behavior_timer = 0
        self.current_behavior = 0
        self.safe_distance = 100
        self.dodge_direction = 0
        self.strafe_direction = 1

        # 碰撞矩形
        self.collision_rect = pygame.Rect(0, 0, self.rect.width // 2, self.rect.height // 2)
        self._update_collision_rect()

    def _update_collision_rect(self):
        self.collision_rect.center = self.rect.center

    def _update_image(self):
        self.image = pygame.transform.rotate(self.original_image, -self.direction_to_player)

    def update(self, all_enemies):
        """更新敌人状态"""
        self.behavior_timer += 1
        if self.behavior_timer % 180 == 0:
            self._switch_behavior()

        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        if self.current_behavior == 0:  # 追踪
            move_dir = math.degrees(math.atan2(dy, dx)) % 360
        elif self.current_behavior == 1:  # 躲避
            if dist < self.safe_distance:
                move_dir = (math.degrees(math.atan2(dy, dx)) + 180) % 360
            else:
                self.current_behavior = 0
                move_dir = math.degrees(math.atan2(dy, dx)) % 360
        else:  # 侧移
            move_dir = (math.degrees(math.atan2(dy, dx)) + 90 * self.strafe_direction) % 360

        self.direction_to_player = (90 - math.degrees(math.atan2(-dy, dx))) % 360

        # 移动
        self.rect.x += math.cos(math.radians(move_dir)) * self.speed
        self.rect.y += math.sin(math.radians(move_dir)) * self.speed

        # 避免重叠
        for other in all_enemies:
            if other is not self and self.rect.colliderect(other.rect):
                ox = (self.rect.centerx - other.rect.centerx) * 0.05
                oy = (self.rect.centery - other.rect.centery) * 0.05
                self.rect.x += ox
                self.rect.y += oy

        self.rect.x = max(0, min(SCREEN_WIDTH - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(SCREEN_HEIGHT - self.rect.height, self.rect.y))
        self._update_image()
        self._update_collision_rect()

    def _switch_behavior(self):
        r = random.random()
        if r < 0.4:
            self.current_behavior = 0
        elif r < 0.7:
            self.current_behavior = 1
        else:
            self.current_behavior = 2
            self.strafe_direction = random.choice([-1, 1])

    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0


class ShootingEnemy(pygame.sprite.Sprite):
    """射击型敌人 - 继承 Enemy 功能并增加射击"""

    def __init__(self, player, bullet_group):
        super().__init__()
        self.player = player
        self.bullet_group = bullet_group
        self.speed = SHOOTING_ENEMY_SPEED
        self.direction_to_player = 0
        self.health = 3
        self.is_dead = False
        self.last_shoot_time = 0
        self.shoot_interval = SHOOTING_ENEMY_SHOOT_INTERVAL

        # 图像
        img = load_image_scaled('images', 'airship', '1.png', scale_factor=1.0)
        self.original_image = pygame.transform.scale(img, (45, 45))
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(-32, 0)

        # 射击型 AI
        self.min_optimal_distance = 150
        self.max_optimal_distance = 250
        self.min_distance = 100
        self.max_distance = 300
        self.target_distance = random.randint(self.min_optimal_distance, self.max_optimal_distance)
        self.strafe_direction = random.choice([-90, 90])
        self.last_direction_change = 0
        self.direction_change_cooldown = 60
        self.distance_adjust_timer = 0

        self.collision_rect = pygame.Rect(0, 0, self.rect.width // 2, self.rect.height // 2)
        self._update_collision_rect()

    def _update_collision_rect(self):
        self.collision_rect.center = self.rect.center

    def _update_image(self):
        self.image = pygame.transform.rotate(self.original_image, -self.direction_to_player)

    def update(self, all_enemies):
        """更新射击型敌人"""
        self.last_direction_change += 1
        self.distance_adjust_timer += 1

        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        self.direction_to_player = (90 - math.degrees(math.atan2(-dy, dx))) % 360

        if self.distance_adjust_timer % 180 == 0:
            self.target_distance = random.randint(self.min_optimal_distance, self.max_optimal_distance)

        # 根据距离决定移动
        if dist > self.target_distance + 50:
            move_dir = math.degrees(math.atan2(dy, dx)) % 360
            self.last_direction_change = 0
        elif dist < self.target_distance - 50:
            move_dir = (math.degrees(math.atan2(dy, dx)) + 180) % 360
            self.last_direction_change = 0
        elif self.last_direction_change >= self.direction_change_cooldown:
            self.strafe_direction = random.choice([-90, 90])
            move_dir = (math.degrees(math.atan2(dy, dx)) + self.strafe_direction) % 360
            self.last_direction_change = 0
        else:
            move_dir = (math.degrees(math.atan2(dy, dx)) + self.strafe_direction) % 360

        self.rect.x += math.cos(math.radians(move_dir)) * self.speed
        self.rect.y += math.sin(math.radians(move_dir)) * self.speed

        # 避免重叠
        for other in all_enemies:
            if other is not self and self.rect.colliderect(other.rect):
                ox = (self.rect.centerx - other.rect.centerx) * 0.05
                oy = (self.rect.centery - other.rect.centery) * 0.05
                self.rect.x += ox
                self.rect.y += oy

        self.rect.x = max(0, min(SCREEN_WIDTH - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(SCREEN_HEIGHT - self.rect.height, self.rect.y))
        self._update_image()
        self._shoot()
        self._update_collision_rect()

    def _shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shoot_time > self.shoot_interval:
            self.last_shoot_time = now
            dx = self.player.rect.centerx - self.rect.centerx
            dy = self.player.rect.centery - self.rect.centery
            angle = math.degrees(math.atan2(dy, dx))
            speed = self.speed * 3.5
            b = Bullet(
                self.rect.centerx, self.rect.centery,
                speed * math.cos(math.radians(angle)),
                speed * math.sin(math.radians(angle)),
                1000, (255, 0, 0), self.player, 'enemy'
            )
            self.bullet_group.add(b)

    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0
