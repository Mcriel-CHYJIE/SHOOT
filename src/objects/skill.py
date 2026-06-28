"""
=============================================================================
 技能系统模块 — 能量与技能
=============================================================================
 所属功能块: 游戏实体
 功能描述  : 实现技能能量系统、Q 技能（散射特殊奖励）、E 技能（护盾+回血）
=============================================================================
"""
import math
import random
import pygame

from src.objects.common import Bullet, TrackingBullet
from src.config import *
from src.core.resource_manager import load_image_scaled


class SpecialReward(pygame.sprite.Sprite):
    """特殊奖励 - 可被子弹击中，爆炸产生追踪子弹"""

    def __init__(self, player):
        pygame.sprite.Sprite.__init__(self)
        self.player = player
        self.score_value = 50
        self.speed = 2
        self.direction = random.uniform(0, 2 * math.pi)
        self.rotation_speed = 1.5
        self.current_rotation = 0
        self.is_special = True
        self.creation_time = pygame.time.get_ticks()
        self.invincible_duration = 500

        try:
            img = load_image_scaled('images', 'specialreward.png', scale_factor=1.0)
        except (pygame.error, FileNotFoundError):
            img = load_image_scaled('images', 'reward.png', scale_factor=1.0)

        self.reward_image = img
        self.resized_image = pygame.transform.scale(img, (15, 15))
        self.image = self.resized_image
        self.rect = self.image.get_rect()
        self.collision_rect = pygame.Rect(0, 0, self.rect.width, self.rect.height)
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(0, SCREEN_HEIGHT - self.rect.height)
        self._update_collision_rect()

    def _update_collision_rect(self):
        self.collision_rect = self.image.get_rect(center=self.rect.center)

    def init_position(self):
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(0, SCREEN_HEIGHT - self.rect.height)

    def update(self):
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
        """爆炸产生追踪子弹"""
        from src.objects.enemies import Enemy
        from src.objects.boss import Boss

        enemies_group = None
        bosses_group = None
        # 从场景中获取敌人组（通过 sprite group 查找）
        for sprite in self.player.bullets_group:
            if hasattr(sprite, 'player') and hasattr(sprite.player, 'enemies_group'):
                enemies_group = sprite.player.enemies_group
            break

        for i in range(0, 360, 15):
            a = math.radians(i)
            self.player.bullets_group.add(TrackingBullet(
                self.rect.centerx, self.rect.centery,
                math.cos(a) * 5, math.sin(a) * 5,
                1000, (255, 255, 255), self.player,
                enemies_group, bosses_group, 'reward'
            ))
        try:
            from src.core.resource_manager import load_sound
            s = load_sound('sounds', 'reward.mp3')
            s.set_volume(0.05)
            s.play()
        except pygame.error:
            pass


class SkillSystem:
    """技能系统 - 管理能量、技能冷却、技能效果"""

    def __init__(self, player, bullets_group, enemy_bullets_group, enemies_group, bosses_group):
        self.player = player
        self.bullets_group = bullets_group
        self.enemy_bullets_group = enemy_bullets_group
        self.enemies_group = enemies_group
        self.bosses_group = bosses_group

        # 能量
        self.energy = 0
        self.display_energy = 0
        self.max_energy = 9
        self.energy_per_reward = 1
        self.energy_smooth_speed = 0.05

        # 冷却
        self.q_skill_cooldown = 5000
        self.e_skill_cooldown = 10000
        self.last_q_skill_time = 0
        self.last_e_skill_time = 0

        # 技能状态
        self.is_q_skill_active = False
        self.is_e_skill_active = False
        self.q_skill_duration = 3000
        self.e_skill_duration = 10000
        self.q_skill_start_time = 0
        self.e_skill_start_time = 0
        self.e_skill_health_boost = 0

        # 图标
        self.reward_icon = None
        self._load_icon()

    def _load_icon(self):
        try:
            img = load_image_scaled('images', 'reward.png', scale_factor=1.0)
            self.reward_icon = pygame.transform.scale(img, (32, 32))
        except pygame.error:
            self.reward_icon = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(self.reward_icon, (255, 215, 0), (16, 16), 16)

    def add_energy(self, amount=1):
        self.energy = min(self.max_energy, self.energy + amount)

    def can_use_q_skill(self, now):
        return (self.energy >= self.max_energy and
                now - self.last_q_skill_time >= self.q_skill_cooldown)

    def can_use_e_skill(self, now):
        return (self.energy >= self.max_energy and
                now - self.last_e_skill_time >= self.e_skill_cooldown)

    def use_q_skill(self, now):
        if not self.can_use_q_skill(now):
            return False
        self.energy = 0
        self.is_q_skill_active = True
        self.q_skill_start_time = now
        self.last_q_skill_time = now

        for _ in range(10):
            sr = SpecialReward(self.player)
            sr.rect.center = self.player.rect.center
            sr.direction = random.uniform(0, 2 * math.pi)
            sr.speed = random.uniform(2, 5)
            from src.engine import rewards
            rewards.add(sr)
        return True

    def use_e_skill(self, now):
        if not self.can_use_e_skill(now):
            return False
        self.energy = 0
        self.is_e_skill_active = True
        self.e_skill_start_time = now
        self.last_e_skill_time = now

        self.player.shield_active = True
        self.player.extra_bullets += 2
        self.player.health += 25
        self.e_skill_health_boost = 25
        return True

    def update(self, now):
        # 能量条平滑
        if self.display_energy < self.energy:
            self.display_energy = min(self.energy, self.display_energy + self.energy_smooth_speed)
        elif self.display_energy > self.energy:
            self.display_energy = max(self.energy, self.display_energy - self.energy_smooth_speed)

        if self.is_q_skill_active and now - self.q_skill_start_time >= self.q_skill_duration:
            self.is_q_skill_active = False

        if self.is_e_skill_active and now - self.e_skill_start_time >= self.e_skill_duration:
            self.is_e_skill_active = False
            self.player.shield_active = False
            self.player.extra_bullets = max(0, self.player.extra_bullets // 2)

    def draw_energy_bar(self, screen):
        """绘制能量条（屏幕底部中央）"""
        bar_w, bar_h = 250, 12
        bar_x = SCREEN_WIDTH // 2 - bar_w // 2
        bar_y = SCREEN_HEIGHT - 50

        # 背景
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h), border_radius=10)
        # 填充
        energy_w = int((self.display_energy / self.max_energy) * bar_w)
        if energy_w > 0:
            pygame.draw.rect(screen, (255, 250, 100), (bar_x, bar_y, energy_w, bar_h), border_radius=10)
        # 边框
        pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=10)

        # 图标
        icon_x = max(bar_x - 16, min(bar_x + energy_w - 16, bar_x + bar_w - 16))
        screen.blit(self.reward_icon, (icon_x, bar_y + bar_h // 2 - 16))

        # 技能提示
        try:
            from src.core.resource_manager import load_font
            font = load_font('fonts', 'pixel_script.ttf', size=16)
        except (pygame.error, FileNotFoundError):
            font = pygame.font.SysFont(None, 16)

        now = pygame.time.get_ticks()
        q_col = (255, 250, 100) if self.can_use_q_skill(now) else (100, 100, 100)
        e_col = (255, 250, 100) if self.can_use_e_skill(now) else (100, 100, 100)
        screen.blit(font.render("Q", True, q_col), (bar_x - 40, bar_y - 5))
        screen.blit(font.render("E", True, e_col), (bar_x + bar_w + 25, bar_y - 5))
