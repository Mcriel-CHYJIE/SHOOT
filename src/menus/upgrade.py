"""
=============================================================================
 升级界面 — 玩家属性升级
=============================================================================
 所属功能块: 界面系统
 功能描述  : 消耗积分升级 HP/射击/SP，包含成本递增、分数不足闪烁提示
=============================================================================
"""
import os
import sys
import pygame
import math
from pygame.locals import QUIT, KEYDOWN, K_SPACE, K_ESCAPE, MOUSEBUTTONDOWN, MOUSEBUTTONUP

from src.objects.player import Player
from src.config import *


class UpgradeScreen:
    """
    升级界面类
    管理玩家属性升级界面的显示和交互
    """

    def __init__(self, screen, player_instance, sounds):
        """
        初始化升级界面
        
        Args:
            screen: Pygame屏幕对象
            player_instance: 玩家实例
            sounds: 音效字典
        """
        self.screen = screen
        self.player_instance = player_instance
        self.sounds = sounds
        
        # 按钮相关变量
        self.upgrade_button = None
        self.return_button = None
        self.hp_button = None
        self.shoot_button = None
        self.sp_button = None
        self.button_png = None
        self.button_png_dark = None
        self.hp_flash_red = False
        self.shoot_flash_red = False
        self.sp_flash_red = False
        
        # 升级分数相关变量
        self.initial_hp_score = INITIAL_HP_SCORE
        self.initial_shoot_score = INITIAL_SHOOT_SCORE
        self.initial_sp_score = INITIAL_SP_SCORE
        self.score_multiplier = SCORE_MULTIPLIER
        self.hp_score = self.initial_hp_score
        self.shoot_score = self.initial_shoot_score
        self.sp_score = self.initial_sp_score
        
        # 升级次数统计
        self.upgrade_counts = {'HP': 0, 'SHOOT': 0, 'SP': 0}
        
        self.load_icon()

    def load_icon(self, icon_path="SHOOT.ico"):
        """
        加载图标
        
        Args:
            icon_path (str): 图标文件路径
        """
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        icon_path = os.path.join(base_path, 'assets', 'images', icon_path)
        try:
            if os.path.exists(icon_path):
                self.button_png = pygame.image.load(icon_path)
                self.button_png_dark = self.button_png.copy()
                self.button_png_dark.fill((150, 150, 150, 250), special_flags=pygame.BLEND_RGBA_MULT)
            else:
                # 如果图标文件不存在，创建一个简单的替代图形
                self.create_default_icon()
        except pygame.error:
            # 如果加载图标失败，创建一个简单的替代图形
            self.create_default_icon()
    
    def create_default_icon(self):
        """
        创建默认图标
        当无法加载图标文件时使用
        """
        self.button_png = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.circle(self.button_png, (100, 150, 200), (32, 32), 30)
        pygame.draw.circle(self.button_png, (200, 255, 255), (32, 32), 25)
        
        self.button_png_dark = self.button_png.copy()
        self.button_png_dark.fill((100, 100, 100, 200), special_flags=pygame.BLEND_RGBA_MULT)

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

    def draw_button(self, button, icon, icon_dark):
        """
        绘制按钮
        
        Args:
            button: 按钮矩形对象
            icon: 按钮图标表面
            icon_dark: 按钮暗色图标表面
        """
        if self.is_mouse_over_button(button):
            self.screen.blit(icon_dark, button.topleft)
        else:
            self.screen.blit(icon, button.topleft)

    def create_button(self, x, y, icon, icon_dark):
        """
        创建按钮
        
        Args:
            x (int): 按钮x坐标
            y (int): 按钮y坐标
            icon: 按钮图标表面
            icon_dark: 按钮暗色图标表面
            
        Returns:
            pygame.Rect: 按钮矩形对象
        """
        icon_width, icon_height = icon.get_size()
        button = pygame.Rect(x, y, icon_width, icon_height)
        self.draw_button(button, icon, icon_dark)
        return button

    def draw_upgrade_screen(self, background):
        """
        绘制升级界面
        
        Args:
            background: 背景对象
        """
        # 填充背景并绘制背景图像
        self.screen.fill(COLORS['black'])
        background.update(None, 0, 0)
        background.draw(self.screen)
        
        # 加载字体文件
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        font_path = os.path.join(base_path, 'assets', 'fonts', 'pixel_script.ttf')
        font = pygame.font.Font(font_path, FONT_SIZES['upgrade_title'])
        
        # 绘制标题
        upgrade_text = font.render('★ 属 性 升 级 ★', True, COLORS['white'])
        self.screen.blit(upgrade_text, (SCREEN_WIDTH // 2 - upgrade_text.get_width() // 2, 80))
        
        # 如果图标已加载，则绘制升级按钮
        if self.button_png:
            icon_width, icon_height = self.button_png.get_size()
            buttons = ['HP', 'SHOOT', 'SP']
            descriptions = {
                'HP': '生命值+50',
                'SHOOT': '射击弹道+1',
                'SP': '移动速度+0.1'
            }
            
            # 计算按钮位置以居中显示
            total_width = sum(icon_width for _ in buttons) + sum(250 for _ in range(len(buttons) - 1))
            start_x = SCREEN_WIDTH // 2 - total_width // 2
            
            # 创建三个属性升级按钮
            for i, attr in enumerate(buttons):
                x = start_x + (icon_width + 250) * i
                y = 250
                if attr == 'HP':
                    self.hp_button = self.create_button(x, y, self.button_png, self.button_png_dark)
                elif attr == 'SHOOT':
                    self.shoot_button = self.create_button(x, y, self.button_png, self.button_png_dark)
                elif attr == 'SP':
                    self.sp_button = self.create_button(x, y, self.button_png, self.button_png_dark)
                    
            # 绘制按钮描述文本
            text_font = pygame.font.Font(font_path, FONT_SIZES['upgrade_description'])
            text_color = COLORS['white']
            for i, attr in enumerate(buttons):
                x = start_x + (icon_width + 250) * i
                y = 350
                description = descriptions[attr]
                description_text = text_font.render(description, True, text_color)
                self.screen.blit(description_text, (x + icon_width // 2 - description_text.get_width() // 2, y))
                
                # 绘制升级所需分数和已升级次数
                score_text = text_font.render(
                    f"升级所需: {getattr(self, attr.lower() + '_score', 0)}", 
                    True, 
                    text_color if not (attr == 'HP' and self.hp_flash_red or 
                                      attr == 'SHOOT' and self.shoot_flash_red or 
                                      attr == 'SP' and self.sp_flash_red) else COLORS['red']
                )
                count_text = text_font.render(f"已升级次数: {self.upgrade_counts[attr]}", True, text_color)
                self.screen.blit(score_text, (x + icon_width // 2 - score_text.get_width() // 2, y + 50))
                self.screen.blit(count_text, (x + icon_width // 2 - count_text.get_width() // 2, y + 80))
                
        # 创建并绘制返回按钮（改为文字按钮样式）
        button_font = pygame.font.Font(font_path, 30)
        return_text = button_font.render("返回游戏", True, COLORS['white'])
        return_text_hover = button_font.render("返回游戏", True, COLORS['red'])
        text_width, text_height = return_text.get_size()
        
        # 添加悬停动画效果
        mouse_pos = pygame.mouse.get_pos()
        button_x = SCREEN_WIDTH // 2 - text_width // 2 - 550
        button_y = SCREEN_HEIGHT - text_height - 25
        self.return_button = pygame.Rect(button_x - 20, button_y - 10, text_width + 40, text_height + 20)
        
        # 检查鼠标是否悬停在按钮上，并添加缩放动画
        scale_factor = 1.0
        if self.return_button.collidepoint(mouse_pos):
            # 计算缩放因子，创建脉动效果
            time = pygame.time.get_ticks()
            scale_factor = 1.0 + 0.1 * abs(math.sin(time * 0.005))
            scaled_text = pygame.transform.smoothscale(
                return_text_hover, 
                (int(text_width * scale_factor), int(text_height * scale_factor))
            )
            self.screen.blit(
                scaled_text, 
                (button_x + text_width/2 - scaled_text.get_width()/2, 
                 button_y + text_height/2 - scaled_text.get_height()/2)
            )
        else:
            self.screen.blit(return_text, (button_x, button_y))
            
        self.render_text()
        # 重置闪烁标志
        self.hp_flash_red = False
        self.shoot_flash_red = False
        self.sp_flash_red = False
        pygame.display.flip()

    def render_text(self):
        """
        渲染文本信息
        """
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        font_path = os.path.join(base_path, 'assets', 'fonts', 'pixel_script.ttf')
        font = pygame.font.Font(font_path, 30)
        
        # 根据分数值设置颜色（低分时显示红色）
        if self.player_instance.score <= 10: 
            score_color = (255, 0, 0)
        else: 
            score_color = (255, 255, 255)
        score_text = font.render('积分值: ' + str(self.player_instance.score), True, score_color)
        
        # 根据生命值设置颜色（低生命值时显示红色）
        # 修改：当生命值为负数时显示为0
        display_health = max(0, self.player_instance.health)
        if self.player_instance.health < 20:  
            health_color = (255, 0, 0)
        else: 
            health_color = (255, 255, 255)
        health_text = font.render('生命值: ' + str(display_health), True, health_color)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(health_text, (10, 50))

    def draw_upgrade_button(self):
        """
        绘制升级按钮
        """
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        font_path = os.path.join(base_path, 'assets', 'fonts', 'pixel_script.ttf')
        button_font = pygame.font.Font(font_path, 30)
        upgrade_text = button_font.render("升级菜单", True, COLORS['white'])
        upgrade_text_hover = button_font.render("升级菜单", True, COLORS['red'])
        text_width, text_height = upgrade_text.get_size()
        
        # 添加悬停动画效果
        mouse_pos = pygame.mouse.get_pos()
        button_x = SCREEN_WIDTH // 2 - text_width // 2 - 550
        button_y = SCREEN_HEIGHT - text_height - 25
        self.upgrade_button = pygame.Rect(button_x - 20, button_y - 10, text_width + 40, text_height + 20)
        
        # 检查鼠标是否悬停在按钮上，并添加缩放动画
        scale_factor = 1.0
        if self.upgrade_button.collidepoint(mouse_pos):
            # 计算缩放因子，创建脉动效果
            time = pygame.time.get_ticks()
            scale_factor = 1.0 + 0.1 * abs(math.sin(time * 0.005))
            scaled_text = pygame.transform.smoothscale(
                upgrade_text_hover, 
                (int(text_width * scale_factor), int(text_height * scale_factor))
            )
            self.screen.blit(
                scaled_text, 
                (button_x + text_width/2 - scaled_text.get_width()/2, 
                 button_y + text_height/2 - scaled_text.get_height()/2)
            )
        else:
            self.screen.blit(upgrade_text, (button_x, button_y))

    def handle_button_click(self):
        """
        处理按钮点击事件
        """
        from src.engine import stats, sound_manager
        
        # 处理HP升级按钮点击
        if self.hp_button and self.is_mouse_over_button(self.hp_button) and pygame.mouse.get_pressed()[0]:
            if self.player_instance.score >= self.hp_score:
                self.player_instance.health += 50
                self.player_instance.score -= self.hp_score
                sound_manager.play_sound('up')  # 使用音效管理器播放音效
                self.hp_score = int(self.hp_score * self.score_multiplier)
                self.upgrade_counts['HP'] += 1
                stats['hp_upgrades'] += 1  # 更新HP升级统计
            else:
                sound_manager.play_sound('error')  # 使用音效管理器播放音效
                self.hp_flash_red = True
                
        # 处理射击升级按钮点击
        elif self.shoot_button and self.is_mouse_over_button(self.shoot_button) and pygame.mouse.get_pressed()[0]:
            if self.player_instance.score >= self.shoot_score:
                self.player_instance.extra_bullets += 1
                self.player_instance.score -= self.shoot_score
                sound_manager.play_sound('up')  # 使用音效管理器播放音效
                self.shoot_score = int(self.shoot_score * self.score_multiplier)
                self.upgrade_counts['SHOOT'] += 1
                stats['shoot_upgrades'] += 1  # 更新射击升级统计
            else:
                sound_manager.play_sound('error')  # 使用音效管理器播放音效
                self.shoot_flash_red = True
                
        # 处理速度升级按钮点击
        elif self.sp_button and self.is_mouse_over_button(self.sp_button) and pygame.mouse.get_pressed()[0]:
            if self.player_instance.score >= self.sp_score:
                self.player_instance.max_speed += 0.5
                self.player_instance.score -= self.sp_score
                sound_manager.play_sound('up')  # 使用音效管理器播放音效
                self.sp_score = int(self.sp_score * self.score_multiplier)
                self.upgrade_counts['SP'] += 1
                stats['speed_upgrades'] += 1  # 更新速度升级统计
            else:
                sound_manager.play_sound('error')  # 使用音效管理器播放音效
                self.sp_flash_red = True

    def reset_upgrade_scores(self):
        """
        重置升级分数
        """
        self.hp_score = self.initial_hp_score
        self.shoot_score = self.initial_shoot_score
        self.sp_score = self.initial_sp_score
        self.upgrade_counts = {'HP': 0, 'SHOOT': 0, 'SP': 0}