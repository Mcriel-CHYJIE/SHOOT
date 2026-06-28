"""
=============================================================================
 背景模块 — 多层星空背景
=============================================================================
 所属功能块: 游戏实体
 功能描述  : 实现三层星星视差滚动效果，支持闪烁动画与关卡行星图像叠加
=============================================================================
"""
import math
import random
import pygame

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.core.resource_manager import load_image_scaled


class StarLayer:
    """单层星星层"""

    def __init__(self, count, brightness_range, parallax_factor, speed_multiplier, size=1):
        self.stars = []
        self.parallax_factor = parallax_factor
        self.speed_multiplier = speed_multiplier
        self.size = size

        for _ in range(count):
            self.stars.append([
                random.randint(0, SCREEN_WIDTH - 1),
                random.randint(0, SCREEN_HEIGHT - 1),
                [random.randint(*brightness_range) for _ in range(3)],
            ])

    def update(self, delta_x, delta_y, star_speed_y):
        """更新层内所有星星位置"""
        removed = []
        for i, star in enumerate(self.stars):
            try:
                x, y, color = star
                x -= delta_x * self.parallax_factor
                y -= delta_y * self.parallax_factor
                y += star_speed_y * self.speed_multiplier
                star[0] = x % SCREEN_WIDTH
                star[1] = y % SCREEN_HEIGHT
            except (ValueError, IndexError):
                removed.append(i)

        # 移除损坏的星星
        for i in reversed(removed):
            self.stars.pop(i)

    def flicker(self, probability):
        """闪烁效果"""
        for star in self.stars:
            if len(star) != 3:
                continue
            if random.random() < probability:
                r, g, b = star[2]
                factor = random.uniform(0.5, 1.5)
                star[2] = [
                    min(255, max(20, int(c * factor)))
                    for c in (r, g, b)
                ]

    def draw(self, surface):
        """绘制星星层"""
        for star in self.stars:
            if len(star) == 3:
                x, y, color = star
                pygame.draw.circle(surface, color, (int(x), int(y)), int(self.size))


class Background(pygame.sprite.Sprite):
    """背景类 - 多层星空 + 视差效果 + 行星关卡"""

    # 层配置: (数量, 亮度范围, 视差因子, 速度倍率, 大小)
    LAYER_CONFIGS = [
        (208, (20, 80), 0.05, 0.3, 1),      # 背景层
        (156, (80, 150), 0.15, 0.8, 1.5),   # 中层
        (156, (150, 255), 0.2, 1.2, 1.95),  # 前景层
    ]

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        self.rect = self.image.get_rect()
        self.star_speed_y = 1.25

        # 创建三层星星
        self.layers = [
            StarLayer(cnt, bright, parallax, speed, sz)
            for cnt, bright, parallax, speed, sz in self.LAYER_CONFIGS
        ]

        # 行星图像
        self.selected_planet_image = None
        self.planet_position = [0, 0]
        self.show_planet_image = False

    def generate_layered_stars(self):
        """（兼容旧接口）"""
        pass

    def update(self, player_rect, delta_x, delta_y):
        """更新所有星星层和行星位置"""
        for layer in self.layers:
            layer.update(delta_x, delta_y, self.star_speed_y)

        # 更新行星位置
        if self.show_planet_image and self.selected_planet_image:
            self.planet_position[0] -= delta_x * 0.05
            self.planet_position[1] -= delta_y * 0.05

            iw = self.selected_planet_image.get_width()
            ih = self.selected_planet_image.get_height()
            if self.planet_position[0] > SCREEN_WIDTH:
                self.planet_position[0] = -iw
            elif self.planet_position[0] < -iw:
                self.planet_position[0] = SCREEN_WIDTH
            if self.planet_position[1] > SCREEN_HEIGHT:
                self.planet_position[1] = -ih
            elif self.planet_position[1] < -ih:
                self.planet_position[1] = SCREEN_HEIGHT

        # 闪烁（各层概率不同）
        self.layers[0].flicker(0.003)
        self.layers[1].flicker(0.006)
        self.layers[2].flicker(0.009)

        # 维护星星数量
        self._maintain_stars()

    def _maintain_stars(self):
        """损毁的星星自动补充"""
        configs = [
            (208, (20, 80)),
            (156, (80, 150)),
            (156, (150, 255)),
        ]
        for layer, (target, brightness_range) in zip(self.layers, configs):
            while len(layer.stars) < target:
                layer.stars.append([
                    random.randint(0, SCREEN_WIDTH - 1),
                    random.randint(0, SCREEN_HEIGHT - 1),
                    [random.randint(*brightness_range) for _ in range(3)],
                ])

    def set_selected_planet(self, planet_image):
        """设置选中的关卡行星图像"""
        if planet_image:
            scaled = pygame.transform.scale(
                planet_image,
                (planet_image.get_width() * 3, planet_image.get_height() * 3)
            )
            self.selected_planet_image = scaled
            max_x = SCREEN_WIDTH - scaled.get_width()
            max_y = SCREEN_HEIGHT - scaled.get_height()
            self.planet_position = [random.randint(0, max_x), random.randint(0, max_y)]
        else:
            self.selected_planet_image = None

    def set_show_planet_image(self, show):
        self.show_planet_image = show

    def draw(self, surface):
        """绘制背景"""
        self.image.fill((0, 0, 0, 0))

        # 背景层
        self.layers[0].draw(self.image)

        # 行星（在背景层和中层之间）
        if self.show_planet_image and self.selected_planet_image:
            darkened = self.selected_planet_image.copy()
            overlay = pygame.Surface(darkened.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 84))
            darkened.blit(overlay, (0, 0))
            self.image.blit(darkened, (int(self.planet_position[0]), int(self.planet_position[1])))

        # 中层 + 前景层
        self.layers[1].draw(self.image)
        self.layers[2].draw(self.image)

        surface.blit(self.image, (0, 0))
