"""
=============================================================================
 Boss 实体模块 — 关卡 Boss
=============================================================================
 所属功能块: 游戏实体
 功能描述  : 实现 Boss 出入场动画、多模式移动/射击 AI、突进攻击
             包含保护罩机制与判定滑轨交互系统
=============================================================================
"""
import math
import random
import pygame

from src.objects.common import Bullet
from src.config import *
from src.core.resource_manager import load_image_scaled
from src.core.shield_utils import create_shield_surface, calculate_shield_flash


class DyingBoss(pygame.sprite.Sprite):
    """正在死亡的 Boss - 闪烁动画"""

    SHIELD_COLORS = {'outer': (173, 216, 230), 'inner': (173, 216, 230)}

    def __init__(self, original_boss):
        super().__init__()
        self.original_image = original_boss.original_image
        self.image = original_boss.image.copy()
        self.rect = original_boss.rect.copy()
        self.collision_rect = original_boss.collision_rect.copy()
        self.current_direction = getattr(original_boss, 'current_direction', 0)
        self.shield_active = getattr(original_boss, 'shield_active', False)
        self.shield_temp_deactivated = getattr(original_boss, 'shield_temp_deactivated', False)

        self.death_time = pygame.time.get_ticks()
        self.death_duration = 1500
        self.flash_interval = 100
        self.last_flash_time = self.death_time
        self.visible = True
        self.is_dead = True
        self._update_image()

    def _update_image(self):
        if not self.visible:
            self.image = pygame.Surface(self.original_image.get_size(), pygame.SRCALPHA)
            return

        if self.shield_active and not self.shield_temp_deactivated:
            shield_surf = create_shield_surface(
                self.original_image, self.SHIELD_COLORS['outer'],
                self.SHIELD_COLORS['inner'], flash_alpha=150
            )
            self.image = pygame.transform.rotate(shield_surf, -self.current_direction)
        else:
            self.image = pygame.transform.rotate(self.original_image, -self.current_direction)

    def update(self):
        """返回 True 表示动画结束"""
        now = pygame.time.get_ticks()
        if now - self.last_flash_time >= self.flash_interval:
            self.visible = not self.visible
            self.last_flash_time = now
        self._update_image()
        if now - self.death_time >= self.death_duration:
            self.kill()
            return True
        return False


class Boss(pygame.sprite.Sprite):
    """Boss 类 - 复杂移动、射击、保护罩、判定滑轨机制"""

    SHIELD_COLORS = {'outer': (173, 216, 230), 'inner': (173, 216, 230)}

    def __init__(self, player, bullet_group, spawn_count=0):
        super().__init__()
        self.player = player
        self.bullet_group = bullet_group
        self.last_shoot_time = 0
        self.spawn_count = spawn_count

        # 难度缩放
        self.health = BOSS_BASE_HEALTH + spawn_count * BOSS_HEALTH_PER_SPAWN
        self.max_health = self.health
        self.shoot_interval = max(BOSS_MIN_SHOOT_INTERVAL,
                                  BOSS_BASE_SHOOT_INTERVAL - spawn_count * BOSS_SHOOT_INTERVAL_DECREASE)
        self.speed = min(BOSS_MAX_SPEED, BOSS_BASE_SPEED + spawn_count * BOSS_SPEED_PER_SPAWN)
        self.rotation_speed = min(BOSS_MAX_ROTATION_SPEED,
                                  BOSS_BASE_ROTATION_SPEED + spawn_count * BOSS_ROTATION_SPEED_PER_SPAWN)

        # 图像
        img = load_image_scaled('images', 'airship', '2.png', scale_factor=1.0)
        self.original_image = pygame.transform.scale(img, (100, 100))
        self.image = self.original_image
        self.mask = pygame.mask.from_surface(self.original_image)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -self.rect.height)

        self.direction_to_player = 0

        # 入场
        self.is_entering = True
        self.enter_speed = BOSS_ENTER_SPEED
        self.visual_direction = 180
        self.current_direction = 180
        self.target_direction = 180

        # 碰撞
        self.collision_rect = pygame.Rect(0, 0, self.rect.width, self.rect.height)
        self._update_collision_rect()

        # 移动/射击模式
        self.move_pattern = 0
        self.move_timer = 0
        self.shoot_pattern = 0
        self.shoot_timer = 0

        # 突进
        self.dash_cooldown = 0
        self.is_dashing = False
        self.dash_speed = 0
        self.dash_target_x = 0
        self.dash_target_y = 0
        self.dash_duration = 0
        self.dash_timer = 0
        self.needs_target_update = False

        # 保护罩
        self.shield_active = True
        self.shield_flash_timer = 0

        # 判定滑轨
        self.rail_active = False
        self.rail_timer = 0
        self.rail_duration = BOSS_RAIL_DURATION
        self.rail_position = 0
        self.rail_direction = 1
        self.rail_speed = BOSS_RAIL_SPEED
        self.rail_success_position = 30
        self.rail_success_direction = 1
        self.rail_success_speed = BOSS_RAIL_SUCCESS_SPEED
        self.rail_success_range = 50
        self.shield_temp_deactivated = False
        self.shield_deactivation_time = 0
        self.initial_rail_success_range = 50

        # 抖动
        self.rail_shake_active = False
        self.rail_shake_timer = 0
        self.rail_shake_duration = BOSS_RAIL_SHAKE_DURATION
        self.rail_shake_intensity = BOSS_RAIL_SHAKE_INTENSITY

    # ---- 更新主循环 ----

    def update(self, all_enemies):
        self._update_shield()
        self._update_rail()

        if self._handle_dash():
            self._update_collision_rect()
            return

        if self.is_entering:
            self._handle_entrance()
        else:
            self.move_timer += 1
            self.shoot_timer += 1

            if self.dash_cooldown <= 0 and self.move_timer % 500 == 0:
                health_ratio = self.health / self.max_health
                if random.random() < 0.3 + (1 - health_ratio) * 0.4:
                    self._start_dash()

            if self.move_timer % 300 == 0:
                self.move_pattern = (self.move_pattern + 1) % 3
            if self.shoot_timer % 200 == 0:
                self.shoot_pattern = (self.shoot_pattern + 1) % 3

            {0: self._move_towards_player,
             1: self._move_horizontally,
             2: self._move_vertically}[self.move_pattern]()

            self.rect.x = max(0, min(SCREEN_WIDTH - self.rect.width, self.rect.x))
            self.rect.y = max(0, min(SCREEN_HEIGHT - self.rect.height, self.rect.y))

            dx = self.player.rect.centerx - self.rect.centerx
            dy = self.player.rect.centery - self.rect.centery
            self.target_direction = (90 - math.degrees(math.atan2(-dy, dx))) % 360

        self._smooth_rotate()
        self._update_image()
        if not self.is_entering:
            self._shoot()
        self._update_collision_rect()

    # ---- 移动模式 ----

    def _move_towards_player(self):
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        angle = math.radians(math.degrees(math.atan2(dy, dx)) % 360)
        self.rect.x += math.cos(angle) * self.speed * 0.5
        self.rect.y += math.sin(angle) * self.speed * 0.5

    def _move_horizontally(self):
        dir_ = 1 if self.player.rect.centerx > self.rect.centerx else -1
        self.rect.x += dir_ * self.speed
        self.rect.y += (self.player.rect.centery - self.rect.centery) * 0.02

    def _move_vertically(self):
        dir_ = 1 if self.player.rect.centery > self.rect.centery else -1
        self.rect.x += (self.player.rect.centerx - self.rect.centerx) * 0.02
        self.rect.y += dir_ * self.speed

    # ---- 入场 ----

    def _handle_entrance(self):
        self.rect.y += self.enter_speed
        if self.rect.y >= 50:
            self.is_entering = False

    # ---- 突进 ----

    def _start_dash(self):
        self.is_dashing = True
        self.dash_target_x = self.player.rect.centerx
        self.dash_target_y = self.player.rect.centery
        dx = self.dash_target_x - self.rect.centerx
        dy = self.dash_target_y - self.rect.centery
        dist = max(1, math.hypot(dx, dy))
        health_ratio = self.health / self.max_health
        self.dash_speed = (8 + self.spawn_count * 0.5) * (2 - health_ratio)
        self.dash_duration = int(dist / self.dash_speed * 0.8)
        self.dash_timer = 0
        self.dash_cooldown = int(300 * health_ratio)
        self.needs_target_update = True

    def _handle_dash(self):
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        if not self.is_dashing:
            return False

        self.dash_timer += 1

        if self.needs_target_update:
            health_ratio = self.health / self.max_health
            if random.random() < 0.1 + (1 - health_ratio) * 0.6:
                self.dash_target_x = self.player.rect.centerx
                self.dash_target_y = self.player.rect.centery
                self.needs_target_update = False
                dx = self.dash_target_x - self.rect.centerx
                dy = self.dash_target_y - self.rect.centery
                dist = max(1, math.hypot(dx, dy))
                self.dash_duration = int(dist / self.dash_speed * 0.8)
                self.dash_timer = 0

        self.rect.x += (self.dash_target_x - self.rect.centerx) / max(1, self.dash_duration - self.dash_timer)
        self.rect.y += (self.dash_target_y - self.rect.centery) / max(1, self.dash_duration - self.dash_timer)

        if self.dash_timer >= self.dash_duration:
            self.is_dashing = False

        return True

    # ---- 保护罩 ----

    def _update_shield(self):
        if self.shield_temp_deactivated:
            now = pygame.time.get_ticks()
            if now - self.shield_deactivation_time >= 5000:
                self.shield_temp_deactivated = False
                self.shield_active = True
        if self.shield_active and not self.shield_temp_deactivated:
            self.shield_flash_timer = (self.shield_flash_timer + 1) % 60

    # ---- 判定滑轨 ----

    def _update_rail(self):
        if not self.is_entering and not self.rail_active:
            self.rail_active = True
            self.rail_timer = pygame.time.get_ticks()

        if self.rail_shake_active:
            now = pygame.time.get_ticks()
            if now - self.rail_shake_timer >= self.rail_shake_duration:
                self.rail_shake_active = False

        if not self.rail_active:
            return

        # 主滑块移动
        self.rail_position += self.rail_speed * self.rail_direction
        self._clamp_rail()

        # 成功区域根据血量缩放
        health_ratio = self.health / self.max_health
        self.rail_success_range = max(10, self.initial_rail_success_range * health_ratio)

        self.rail_success_position += self.rail_success_speed * self.rail_success_direction
        self._clamp_success_rail()

        now = pygame.time.get_ticks()
        if now - self.rail_timer >= self.rail_duration:
            self.rail_active = False

    def _clamp_rail(self):
        if self.rail_position <= 0:
            self.rail_position = 0
            self.rail_direction = 1
        elif self.rail_position >= 100:
            self.rail_position = 100
            self.rail_direction = -1

    def _clamp_success_rail(self):
        left = self.rail_success_position - self.rail_success_range / 2
        right = self.rail_success_position + self.rail_success_range / 2
        if left <= 0:
            self.rail_success_position = self.rail_success_range / 2
            self.rail_success_direction = 1
        elif right >= 100:
            self.rail_success_position = 100 - self.rail_success_range / 2
            self.rail_success_direction = -1

    # ---- 图像 ----

    def _smooth_rotate(self):
        diff = (self.target_direction - self.current_direction) % 360
        if diff > 180:
            diff -= 360
        step = self.rotation_speed
        self.current_direction += step if diff > step else (-step if diff < -step else diff)

    def _update_image(self):
        if self.shield_active and not self.shield_temp_deactivated:
            alpha = calculate_shield_flash(self.shield_flash_timer)
            shield_surf = create_shield_surface(
                self.original_image, self.SHIELD_COLORS['outer'],
                self.SHIELD_COLORS['inner'], flash_alpha=alpha
            )
            self.image = pygame.transform.rotate(shield_surf, -self.current_direction)
        else:
            self.image = pygame.transform.rotate(self.original_image, -self.current_direction)

        self.mask = pygame.mask.from_surface(self.image)

    def _update_collision_rect(self):
        self.collision_rect.center = self.rect.center

    # ---- 射击 ----

    def _shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shoot_time < self.shoot_interval:
            return
        self.last_shoot_time = now

        angles = {
            0: [0],                         # 单发
            1: [-10, 10],                   # 双发
            2: [-15, 0, 15],                # 三发
        }
        pattern = self.shoot_pattern % 3
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        base_angle = math.degrees(math.atan2(dy, dx))

        for offset in angles.get(pattern, [0]):
            a = math.radians(base_angle + offset)
            speed = 4 + random.random() * 2
            b = Bullet(
                self.rect.centerx, self.rect.centery,
                math.cos(a) * speed, math.sin(a) * speed,
                1000, (255, 50, 50), self.player, 'enemy'
            )
            self.bullet_group.add(b)

    # ---- 伤害 ----

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.is_dead = True
            return True
        return False
