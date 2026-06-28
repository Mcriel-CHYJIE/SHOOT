"""
=============================================================================
 开始界面 — 主菜单
=============================================================================
 所属功能块: 界面系统
 功能描述  : 显示游戏标题 ASCII 艺术字、操作说明、版本信息
             提供开始游戏/排行榜/设置三个入口按钮
=============================================================================
"""
import math
import pygame
from pygame.locals import QUIT, KEYDOWN, K_SPACE, K_ESCAPE

from src.objects.player import Player
from src.config import *
from src.core.resource_manager import load_font

class StartScreen:
    """开始界面类 - 管理游戏开始界面的显示和交互"""

    def __init__(self, screen, player_instance, sounds):
        self.screen = screen
        self.player_instance = player_instance
        self.sounds = sounds
        self.start_button = None
        self.leaderboard_button = None
        self.settings_button = None
        self.button_png = None
        self.button_png_dark = None
        self.load_icon()

    def load_icon(self, icon_path="SHOOT.ico"):
        try:
            from src.core.resource_manager import load_image
            self.button_png = load_image('images', icon_path)
            self.button_png_dark = self.button_png.copy()
            self.button_png_dark.fill((150, 150, 150, 250), special_flags=pygame.BLEND_RGBA_MULT)
        except (pygame.error, FileNotFoundError):
            pass

    def is_mouse_over_button(self, button):
        if button is None:
            return False
        return button.collidepoint(pygame.mouse.get_pos())

    def draw_start_screen(self, background):
        """绘制开始界面"""
        instruction_font = load_font('fonts', 'pixel_script.ttf', size=FONT_SIZES['instruction'])
        tip_font = load_font('fonts', 'pixel_script.ttf', size=FONT_SIZES['tip'])
        version_font = load_font('fonts', 'pixel_script.ttf', size=FONT_SIZES['version'])
        button_font = load_font('fonts', 'pixel_script.ttf', size=36)

        self.screen.fill(COLORS['black'])
        background.update(None, 0, 0)
        background.draw(self.screen)

        # 绘制玩家飞船
        self.player_instance.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 75)
        self.player_instance.update_image()
        self.screen.blit(self.player_instance.image, self.player_instance.rect)

        # 标题 — "SHOOT"
        title_font = load_font('fonts', 'pixel_script.ttf', size=180)
        shoot_text = title_font.render('SHOOT', True, COLORS['white'])
        self.screen.blit(shoot_text, (SCREEN_WIDTH // 2 - shoot_text.get_width() // 2, 100))

        # 操作说明
        controls = instruction_font.render(
            '按"WASD"键或方向键以控制移动，移动鼠标瞄准并按下以进行射击', True, COLORS['white']
        )
        self.screen.blit(controls, (SCREEN_WIDTH // 2 - controls.get_width() // 2, 310))
        tip = tip_font.render('tip:控制无反应时请切换到英文输入法再进行操作', True, COLORS['white'])
        self.screen.blit(tip, (SCREEN_WIDTH // 2 - tip.get_width() // 2, 369))

        # 版本信息
        my_text = version_font.render("BY.@云Mcriel", True, COLORS['yellow'])
        self.screen.blit(my_text, (960, 272))
        v_text = version_font.render("V.1.3.1", True, COLORS['white'])
        self.screen.blit(v_text, (1240, 780))

        # 按钮工具：绘制带悬停动画的按钮
        mouse_pos = pygame.mouse.get_pos()

        def draw_button(text, y_offset, hover_color=COLORS['red']):
            text_surf = button_font.render(text, True, COLORS['white'])
            text_hover = button_font.render(text, True, hover_color)
            tw, th = text_surf.get_size()
            bx = SCREEN_WIDTH // 2 - tw // 2
            by = SCREEN_HEIGHT - th - y_offset
            btn_rect = pygame.Rect(bx - 20, by - 10, tw + 40, th + 20)

            if btn_rect.collidepoint(mouse_pos):
                scale = 1.0 + 0.1 * abs(math.sin(pygame.time.get_ticks() * 0.005))
                scaled = pygame.transform.smoothscale(
                    text_hover, (int(tw * scale), int(th * scale))
                )
                self.screen.blit(scaled, (bx + tw/2 - scaled.get_width()/2, by + th/2 - scaled.get_height()/2))
            else:
                self.screen.blit(text_surf, (bx, by))
            return btn_rect

        self.start_button = draw_button("开始游戏", 200)
        self.leaderboard_button = draw_button("游戏排行", 125)
        self.settings_button = draw_button("游戏设置", 50)
