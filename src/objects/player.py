"""
=============================================================================
 玩家实体模块 — 玩家飞船
=============================================================================
 所属功能块: 游戏实体
 功能描述  : 实现键盘控制移动、鼠标瞄准射击、尾迹效果、入场动画、保护罩
=============================================================================
"""
import math
import pygame

from src.objects.common import Bullet
from src.config import *
from src.core.resource_manager import load_image_scaled
from src.core.shield_utils import create_shield_surface, calculate_shield_flash


class Player(pygame.sprite.Sprite):
    """玩家类 - 实现飞船移动、射击、动画效果"""

    # 护盾颜色配置
    SHIELD_COLORS = {
        'outer': (255, 215, 0),    # 金色
        'inner': (255, 255, 224),  # 淡黄色
    }

    def __init__(self, bullets_group):
        super().__init__()
        self.bullets_group = bullets_group

        # 基础属性
        self.health = PLAYER_HEALTH
        self.max_health = PLAYER_MAX_HEALTH
        self.bullet_speed = PLAYER_BULLET_SPEED
        self.bullet_range = PLAYER_BULLET_RANGE
        self.extra_bullets = 0
        self.score = 20
        self.velocity_x = 0
        self.velocity_y = 0
        self.max_speed = PLAYER_MAX_SPEED
        self.deceleration_rate = PLAYER_DECELERATION_RATE

        # 方向
        self.direction = 0
        self.target_direction = 0
        self.rotation_speed = PLAYER_ROTATION_SPEED

        # 保护罩
        self.shield_active = False
        self.shield_flash_timer = 0

        # 尾迹
        self.trail_points = []
        self.max_trail_points = 50
        self.trail_lifetime = 250

        # 入场动画
        self.entrance_animation_active = False
        self.entrance_animation_start_time = 0
        self.entrance_animation_duration = 2000
        self.entrance_start_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT + 50)
        self.entrance_end_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
        self.should_play_entrance_animation = False

        # 加载图像
        try:
            player_image = load_image_scaled('images', 'airship', '4.png', scale_factor=1.0)
            self.original_image = pygame.transform.scale(player_image, (51, 51))
        except (pygame.error, FileNotFoundError) as e:
            print(f"无法加载玩家图像: {e}")
            raise

        self.image = self.original_image
        self.rect = self.image.get_rect(center=(400, 300))

        # 碰撞矩形（显示矩形的一半）
        self.collision_rect = pygame.Rect(0, 0, 26, 26)
        self._update_collision_rect()

    # ---- 重置 ----

    def reset(self):
        """重置玩家状态"""
        self.health = PLAYER_HEALTH
        self.max_health = PLAYER_MAX_HEALTH
        self.score = PLAYER_INITIAL_SCORE
        self.velocity_x = 0
        self.velocity_y = 0
        self.direction = 0
        self.target_direction = 0
        self.extra_bullets = 0
        self.max_speed = 5
        self.trail_points.clear()
        self.shield_active = False
        self.shield_flash_timer = 0

        if self.should_play_entrance_animation:
            self.rect.center = self.entrance_start_pos
            self.entrance_animation_active = True
            self.entrance_animation_start_time = pygame.time.get_ticks()
        else:
            self.rect.center = self.entrance_end_pos
            self.entrance_animation_active = False
            self.entrance_animation_start_time = 0

        self.should_play_entrance_animation = False
        self._update_collision_rect()

    # ---- 更新 ----

    def update(self):
        if self.entrance_animation_active:
            self._update_entrance_animation()
            self._update_collision_rect()
            return

        keys = pygame.key.get_pressed()
        ax, ay = 0, 0

        # 对角线
        left = keys[pygame.K_a] or keys[pygame.K_LEFT]
        right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
        up = keys[pygame.K_w] or keys[pygame.K_UP]
        down = keys[pygame.K_s] or keys[pygame.K_DOWN]

        if left and up:
            ax, ay, self.target_direction = -self.max_speed, -self.max_speed, 45
        elif left and down:
            ax, ay, self.target_direction = -self.max_speed, self.max_speed, 135
        elif right and up:
            ax, ay, self.target_direction = self.max_speed, -self.max_speed, 315
        elif right and down:
            ax, ay, self.target_direction = self.max_speed, self.max_speed, 225
        elif left:
            ax, self.target_direction = -self.max_speed, 90
        elif right:
            ax, self.target_direction = self.max_speed, 270
        elif up:
            ay, self.target_direction = -self.max_speed, 0
        elif down:
            ay, self.target_direction = self.max_speed, 180

        # 减速
        if ax == 0:
            self.velocity_x = self._decelerate(self.velocity_x)
        if ay == 0:
            self.velocity_y = self._decelerate(self.velocity_y)

        self.velocity_x = max(-self.max_speed, min(self.max_speed, self.velocity_x + ax))
        self.velocity_y = max(-self.max_speed, min(self.max_speed, self.velocity_y + ay))

        self.rect.x = max(0, min(SCREEN_WIDTH - self.rect.width, self.rect.x + self.velocity_x))
        self.rect.y = max(0, min(SCREEN_HEIGHT - self.rect.height, self.rect.y + self.velocity_y))

        if abs(self.velocity_x) > 0.1 or abs(self.velocity_y) > 0.1:
            self._add_trail_point()

        self._update_trail()
        self._update_collision_rect()
        self._smooth_rotate()
        self.update_image()

    # ---- 入场动画 ----

    def _update_entrance_animation(self):
        now = pygame.time.get_ticks()
        progress = min(1.0, (now - self.entrance_animation_start_time) / self.entrance_animation_duration)
        progress = 1 - (1 - progress) ** 3  # ease-out cubic

        sx, sy = self.entrance_start_pos
        ex, ey = self.entrance_end_pos
        self.rect.center = (sx + (ex - sx) * progress, sy + (ey - sy) * progress)

        if progress >= 1.0:
            self.entrance_animation_active = False

    # ---- 尾迹 ----

    def _add_trail_point(self):
        now = pygame.time.get_ticks()
        angle = math.radians(self.direction)
        tx = self.rect.centerx + math.sin(angle) * (self.rect.height // 2)
        ty = self.rect.centery + math.cos(angle) * (self.rect.height // 2)
        self.trail_points.append({'pos': (tx, ty), 'time': now, 'direction': self.direction})
        if len(self.trail_points) > self.max_trail_points:
            self.trail_points.pop(0)

    def _update_trail(self):
        now = pygame.time.get_ticks()
        self.trail_points = [p for p in self.trail_points if now - p['time'] < self.trail_lifetime]

    def draw_trail(self, screen):
        """绘制尾迹效果"""
        now = pygame.time.get_ticks()
        for pt in self.trail_points:
            age = (now - pt['time']) / self.trail_lifetime
            if age >= 1:
                continue
            alpha = int(255 * (1 - age))
            size = max(1, int(3 * (1 - age)))
            color = (255, max(100, int(255 * (1 - age))), 0, alpha)
            surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (size, size), size)
            screen.blit(surf, (pt['pos'][0] - size, pt['pos'][1] - size))

    # ---- 碰撞矩形 ----

    def _update_collision_rect(self):
        self.collision_rect.center = self.rect.center

    # ---- 减速 ----

    @staticmethod
    def _decelerate(v):
        if v > 0:
            return max(0, v - PLAYER_DECELERATION_RATE)
        elif v < 0:
            return min(0, v + PLAYER_DECELERATION_RATE)
        return 0

    # ---- 旋转 ----

    def _smooth_rotate(self):
        diff = (self.target_direction - self.direction) % 360
        if diff > 180:
            diff -= 360
        step = self.rotation_speed
        self.direction += step if diff > step else (-step if diff < -step else diff)

    def update_image(self):
        """更新玩家图像（含护盾效果）"""
        if self.shield_active:
            self.shield_flash_timer = (self.shield_flash_timer + 1) % 60
            alpha = calculate_shield_flash(self.shield_flash_timer)
            shield_surf = create_shield_surface(
                self.original_image,
                self.SHIELD_COLORS['outer'],
                self.SHIELD_COLORS['inner'],
                flash_alpha=alpha
            )
            rotated = pygame.transform.rotate(shield_surf, self.direction)
        else:
            rotated = pygame.transform.rotate(self.original_image, self.direction)

        old_center = self.rect.center
        self.rect = rotated.get_rect()
        self.rect.center = old_center
        self.image = rotated

    # ---- 射击 ----

    def shoot(self, mouse_pos):
        """玩家射击，返回发射子弹数"""
        if self.entrance_animation_active:
            return 0

        mx, my = mouse_pos
        dx = mx - self.rect.centerx
        dy = my - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist == 0:
            return 0

        dx, dy = dx / dist, dy / dist
        spread = math.pi / 36

        bullets_fired = 0

        def fire(off_x, off_y):
            nonlocal bullets_fired
            b = Bullet(
                self.rect.centerx, self.rect.centery,
                off_x * self.bullet_speed, off_y * self.bullet_speed,
                self.bullet_range, (255, 255, 0), self, 'player'
            )
            self.bullets_group.add(b)
            bullets_fired += 1

        fire(dx, dy)  # 中心子弹

        for i in range(self.extra_bullets):
            off = (-spread / 2) + ((i + 1) * spread)
            fire(dx * math.cos(off) - dy * math.sin(off),
                 dx * math.sin(off) + dy * math.cos(off))

        return bullets_fired
