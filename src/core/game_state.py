"""
=============================================================================
 游戏状态管理 — 全局状态容器
=============================================================================
 所属功能块: 工具库
 功能描述  : 封装所有游戏全局状态变量，替代分散的 30+ 全局变量
=============================================================================
"""
import pygame
from src.core.resource_manager import load_image


class GameState:
    """游戏状态类 - 单一事实来源"""

    def __init__(self):
        # 基本运行状态
        self.running = True
        self.clock = pygame.time.Clock()

        # 界面状态
        self.start_screen = True
        self.level_select_screen = False
        self.leaderboard_screen = False
        self.settings_screen = False
        self.pause_screen = False
        self.game_over = False
        self.game_paused = False

        # 导航来源标记
        self.from_pause_to_leaderboard = False
        self.from_pause_to_settings = False
        self.from_gameover = False

        # 游戏内状态
        self.player_explosion = False
        self.END_sound_played = False
        self.enemies_can_spawn = False

        # 引导图片状态
        self.guide_image = None
        self.guide_image_loaded = False
        self.guide_start_time = 0
        self.guide_duration = 5000

        # 界面按钮（由菜单管理器在每个渲染帧更新）
        self.start_button = None
        self.leaderboard_button = None
        self.settings_button = None
        self.level_return_button = None
        self.challenge_button = None
        self.leaderboard_return_button = None
        self.settings_return_button = None
        self.pause_return_button = None
        self.pause_menu_button = None
        self.pause_leaderboard_button = None
        self.pause_settings_button = None
        self.level_buttons = []

    def reset_game_flags(self):
        """重置游戏相关标志（不重置界面状态）"""
        self.player_explosion = False
        self.END_sound_played = False
        self.game_over = False
        self.enemies_can_spawn = False

    def to_menu(self):
        """返回到主菜单"""
        self.start_screen = True
        self.level_select_screen = False
        self.leaderboard_screen = False
        self.settings_screen = False
        self.pause_screen = False
        self.game_over = False
        self.game_paused = False

    def start_gameplay(self):
        """进入游戏界面"""
        self.start_screen = False
        self.level_select_screen = False
        self.game_over = False
        self.game_paused = False
        self.pause_screen = False

    def load_guide_image(self):
        """加载引导图片（延迟加载）"""
        if not self.guide_image_loaded:
            try:
                self.guide_image = load_image('images', 'dm.png')
                self.guide_image_loaded = True
            except (pygame.error, FileNotFoundError):
                self.guide_image_loaded = True  # 标记以避免重复尝试
