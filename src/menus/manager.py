"""
=============================================================================
 菜单管理器 — 统一界面调度
=============================================================================
 所属功能块: 界面系统
 功能描述  : 管理开始、升级、排行榜、设置、暂停、关卡选择、游戏结束等
             所有菜单界面的创建、状态同步与渲染调度
=============================================================================
"""
import os
import sys
import math
import pygame
from pygame.locals import QUIT, KEYDOWN, K_SPACE, K_ESCAPE
from src.objects.player import Player
from src.config import *

# 导入各个界面类
from src.menus.start import StartScreen
from src.menus.upgrade import UpgradeScreen
from src.menus.leaderboard import LeaderboardScreen
from src.menus.settings import SettingsScreen
from src.menus.pause import PauseScreen
from src.menus.level import LevelSelectScreen
from src.menus.gameover import GameOverScreen


class MenuManager:
    """
    菜单管理器类
    统一管理游戏中的所有菜单界面
    """

    def __init__(self, screen, player_instance, sounds):
        """
        初始化菜单管理器
        
        Args:
            screen: Pygame屏幕对象
            player_instance: 玩家实例
            sounds: 音效字典
        """
        self.sp_flash_red = None
        self.shoot_flash_red = None
        self.hp_flash_red = None
        self.screen = screen
        self.player_instance = player_instance
        self.sounds = sounds

        # 初始化各个界面
        self.start_screen = StartScreen(screen, player_instance, sounds)
        self.upgrade_screen = UpgradeScreen(screen, player_instance, sounds)
        self.leaderboard_screen = LeaderboardScreen(screen, player_instance, sounds)
        self.settings_screen = SettingsScreen(screen, player_instance, sounds)
        self.pause_screen = PauseScreen(screen, player_instance, sounds)
        self.level_screen = LevelSelectScreen(screen, player_instance, sounds)
        self.gameover_screen = GameOverScreen(screen, player_instance, sounds, self)
        
        # 按钮相关变量，用于在主循环中检测按钮点击
        self.upgrade_button = None
        self.pause_button = None
        self.start_button = None
        self.leaderboard_button = None
        self.settings_button = None
        self.hp_button = None
        self.shoot_button = None
        self.sp_button = None
        self.return_button = None
        
        # 升级分数相关变量（用于向后兼容）
        # 这些变量是为了保持与旧代码的兼容性而保留的
        self.initial_hp_score = INITIAL_HP_SCORE
        self.initial_shoot_score = INITIAL_SHOOT_SCORE
        self.initial_sp_score = INITIAL_SP_SCORE
        self.score_multiplier = SCORE_MULTIPLIER
        self.hp_score = self.initial_hp_score
        self.shoot_score = self.initial_shoot_score
        self.sp_score = self.initial_sp_score
        
        # 升级次数统计（用于向后兼容）
        self.upgrade_counts = {'HP': 0, 'SHOOT': 0, 'SP': 0}

    def draw_start_screen(self, background):
        """
        绘制开始界面
        
        Args:
            background: 背景对象
        """
        self.start_screen.draw_start_screen(background)
        # 同步按钮引用，以便主循环可以检测按钮点击
        self.start_button = self.start_screen.start_button
        self.leaderboard_button = self.start_screen.leaderboard_button
        self.settings_button = self.start_screen.settings_button

    def draw_upgrade_screen(self, background):
        """
        绘制升级界面
        
        Args:
            background: 背景对象
        """
        self.upgrade_screen.draw_upgrade_screen(background)
        # 同步按钮引用，以便主循环可以检测按钮点击
        self.hp_button = self.upgrade_screen.hp_button
        self.shoot_button = self.upgrade_screen.shoot_button
        self.sp_button = self.upgrade_screen.sp_button
        self.return_button = self.upgrade_screen.return_button
        self.upgrade_button = self.upgrade_screen.upgrade_button
        
        # 同步闪烁状态，用于在分数不足时显示红色警告
        self.hp_flash_red = self.upgrade_screen.hp_flash_red
        self.shoot_flash_red = self.upgrade_screen.shoot_flash_red
        self.sp_flash_red = self.upgrade_screen.sp_flash_red
        
        # 同步分数和升级次数
        self.hp_score = self.upgrade_screen.hp_score
        self.shoot_score = self.upgrade_screen.shoot_score
        self.sp_score = self.upgrade_screen.sp_score
        self.upgrade_counts = self.upgrade_screen.upgrade_counts

    def draw_leaderboard_screen(self, background, from_pause=False, from_gameover=False):
        """
        绘制排行榜界面
        
        Args:
            background: 背景对象
            from_pause (bool): 是否从暂停界面进入
            from_gameover (bool): 是否从游戏结束界面进入
            
        Returns:
            pygame.Rect: 返回按钮的矩形对象
        """
        return_button = self.leaderboard_screen.draw_leaderboard_screen(background, from_pause, from_gameover)
        return return_button

    def draw_settings_screen(self, background, from_pause=False):
        """
        绘制设置界面
        
        Args:
            background: 背景对象
            from_pause (bool): 是否从暂停界面进入
            
        Returns:
            pygame.Rect: 返回按钮的矩形对象
        """
        return_button = self.settings_screen.draw_settings_screen(background, from_pause)
        return return_button

    def draw_pause_screen(self, background):
        """
        绘制暂停界面
        
        Args:
            background: 背景对象
            
        Returns:
            tuple: 包含各个按钮的矩形对象
        """
        resume_button, menu_button, leaderboard_button, settings_button = self.pause_screen.draw_pause_screen(background)
        return resume_button, menu_button, leaderboard_button, settings_button

    def draw_level_select_screen(self, background):
        """
        绘制关卡选择界面
        
        Args:
            background: 背景对象
            
        Returns:
            tuple: 包含关卡按钮列表和返回按钮的矩形对象
        """
        level_buttons, return_button = self.level_screen.draw_level_select_screen(background)
        return level_buttons, return_button

    def draw_gameover_screen(self, background):
        """
        绘制游戏结束界面
        
        Args:
            background: 背景对象
        """
        self.gameover_screen.render_final_score(background)

    def render_text(self):
        """
        渲染文本信息
        """
        self.upgrade_screen.render_text()

    def draw_upgrade_button(self):
        """
        绘制升级按钮
        """
        self.upgrade_screen.draw_upgrade_button()
        self.upgrade_button = self.upgrade_screen.upgrade_button

    def draw_pause_button(self):
        """
        绘制暂停按钮
        """
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        font_path = os.path.join(base_path, 'assets', 'fonts', 'pixel_script.ttf')
        button_font = pygame.font.Font(font_path, 30)
        pause_text = button_font.render("暂停游戏", True, COLORS['white'])
        pause_text_hover = button_font.render("暂停游戏", True, COLORS['red'])
        text_width, text_height = pause_text.get_size()
        
        # 添加悬停动画效果
        mouse_pos = pygame.mouse.get_pos()
        button_x = SCREEN_WIDTH // 2 + text_width // 2 + 425  # 右下角位置
        button_y = SCREEN_HEIGHT - text_height - 25
        self.pause_button = pygame.Rect(button_x - 20, button_y - 10, text_width + 40, text_height + 20)
        
        # 检查鼠标是否悬停在按钮上，并添加缩放动画
        scale_factor = 1.0
        if self.pause_button.collidepoint(mouse_pos):
            # 计算缩放因子，创建脉动效果
            time = pygame.time.get_ticks()
            scale_factor = 1.0 + 0.1 * abs(math.sin(time * 0.005))
            scaled_text = pygame.transform.smoothscale(
                pause_text_hover, 
                (int(text_width * scale_factor), int(text_height * scale_factor))
            )
            self.screen.blit(
                scaled_text, 
                (button_x + text_width/2 - scaled_text.get_width()/2, 
                 button_y + text_height/2 - scaled_text.get_height()/2)
            )
        else:
            self.screen.blit(pause_text, (button_x, button_y))

    def handle_button_click(self):
        """
        处理按钮点击事件
        """
        self.upgrade_screen.handle_button_click()
        # 同步状态
        self.hp_flash_red = self.upgrade_screen.hp_flash_red
        self.shoot_flash_red = self.upgrade_screen.shoot_flash_red
        self.sp_flash_red = self.upgrade_screen.sp_flash_red
        self.hp_score = self.upgrade_screen.hp_score
        self.shoot_score = self.upgrade_screen.shoot_score
        self.sp_score = self.upgrade_screen.sp_score
        self.upgrade_counts = self.upgrade_screen.upgrade_counts

    def reset_upgrade_scores(self):
        """
        重置升级分数
        """
        self.upgrade_screen.reset_upgrade_scores()
        # 同步状态
        self.hp_score = self.upgrade_screen.hp_score
        self.shoot_score = self.upgrade_screen.shoot_score
        self.sp_score = self.upgrade_screen.sp_score
        self.upgrade_counts = self.upgrade_screen.upgrade_counts

    # 代理方法，用于访问子类的属性和方法
    def is_mouse_over_button(self, button):
        """
        检查鼠标是否悬停在按钮上
        
        Args:
            button: 按钮矩形对象
            
        Returns:
            bool: 如果鼠标悬停在按钮上返回True，否则返回False
        """
        if button is None:
            return False
        mouse_pos = pygame.mouse.get_pos()
        return button.collidepoint(mouse_pos)