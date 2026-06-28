"""
=============================================================================
 设置界面 — 游戏选项配置
=============================================================================
 所属功能块: 界面系统
 功能描述  : 提供主音量滑条控制、背景音乐开关等设置
=============================================================================
"""
import os
import sys
import math
import pygame
from pygame.locals import QUIT, KEYDOWN, K_SPACE, K_ESCAPE
import pygame.mixer

from src.objects.player import Player
from src.config import *
from src.data_manager import get_settings, save_settings


class SettingsScreen:
    """
    设置界面类
    管理游戏设置界面的显示和音量控制功能
    """

    def __init__(self, screen, player_instance, sounds):
        """
        初始化设置界面
        
        Args:
            screen: Pygame屏幕对象
            player_instance: 玩家实例
            sounds: 音效字典
        """
        self.screen = screen
        self.player_instance = player_instance
        self.sounds = sounds
        
        # 保存原始音效音量值，用于计算实际音量
        self.original_sound_volumes = {key: SOUND_VOLUMES[key] for key in SOUND_VOLUMES}
        
        # 音量控制相关
        # 默认将音量设置为最大值
        pygame.mixer.music.set_volume(BGM_VOLUME)
        
        # 从保存的设置中加载音量，如果没有则使用默认值
        saved_settings = get_settings()
        self.music_volume = saved_settings.get("music_volume", 1.0)  # 滑块位置比例设为1.0 (100%)
        self.sounds_volume = saved_settings.get("sounds_volume", 1.0)  # 音效音量比例设为1.0 (100%)
        
        # 应用保存的音量设置
        pygame.mixer.music.set_volume(self.music_volume * BGM_VOLUME)
        self.apply_sounds_volume()
        
        self.slider_rect = None
        self.slider_knob_rect = None
        self.sounds_slider_rect = None
        self.sounds_slider_knob_rect = None
        self.dragging_slider = False
        self.dragging_sounds_slider = False

    def apply_sounds_volume(self):
        """
        应用音效音量设置
        根据音效音量滑块位置调整所有音效的实际音量
        """
        # 更新所有音效的音量，基于SOUND_VOLUMES中的值作为100%
        for key, sound in self.sounds.items():
            sound.set_volume(self.sounds_volume * self.original_sound_volumes[key])

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

    # 添加处理鼠标事件的方法
    def handle_mouse_event(self, event):
        """
        处理鼠标事件，主要用于音量滑块控制
        
        Args:
            event: Pygame事件对象
        """
        volume_changed = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 检查是否点击了背景音乐滑块按钮
            if self.slider_knob_rect and self.slider_knob_rect.collidepoint(event.pos):
                self.dragging_slider = True
            # 检查是否点击了音效音量滑块按钮
            elif self.sounds_slider_knob_rect and self.sounds_slider_knob_rect.collidepoint(event.pos):
                self.dragging_sounds_slider = True
            # 检查是否点击了背景音乐滑块轨道
            elif self.slider_rect and self.slider_rect.collidepoint(event.pos):
                # 直接跳转到点击位置，确保滑块不会超出滑轨边界
                mouse_x = event.pos[0]
                # 限制鼠标位置在滑轨范围内
                relative_x = max(0, min(self.slider_rect.width - 10, mouse_x - self.slider_rect.left))
                # 计算音量比例，考虑滑块宽度，确保滑块不会超出边界
                self.music_volume = max(0, min(1, relative_x / (self.slider_rect.width - 10)))
                pygame.mixer.music.set_volume(self.music_volume * BGM_VOLUME)  # 应用实际音量
                volume_changed = True
            # 检查是否点击了音效音量滑块轨道
            elif self.sounds_slider_rect and self.sounds_slider_rect.collidepoint(event.pos):
                # 直接跳转到点击位置，确保滑块不会超出滑轨边界
                mouse_x = event.pos[0]
                # 限制鼠标位置在滑轨范围内
                relative_x = max(0, min(self.sounds_slider_rect.width, mouse_x - self.sounds_slider_rect.left))
                # 计算音量比例，考虑滑块宽度，确保滑块不会超出边界
                self.sounds_volume = max(0, min(1, relative_x / self.sounds_slider_rect.width))
                # 更新所有音效的音量，基于SOUND_VOLUMES中的值作为100%
                self.apply_sounds_volume()
                volume_changed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging_slider = False
            self.dragging_sounds_slider = False
            # 保存音量设置
            if self.dragging_slider or self.dragging_sounds_slider:
                volume_changed = True
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_slider and self.slider_rect:
                # 根据鼠标位置更新背景音乐音量，确保滑块不会超出滑轨边界
                mouse_x = event.pos[0]
                # 限制鼠标位置在滑轨范围内，考虑滑块宽度
                slider_width = 20  # 新的滑块宽度
                relative_x = max(0, min(self.slider_rect.width - slider_width, mouse_x - self.slider_rect.left))
                # 计算音量比例
                self.music_volume = max(0, min(1, relative_x / (self.slider_rect.width - slider_width)))
                pygame.mixer.music.set_volume(self.music_volume * BGM_VOLUME)  # 应用实际音量
                volume_changed = True
            elif self.dragging_sounds_slider and self.sounds_slider_rect:
                # 根据鼠标位置更新音效音量，确保滑块不会超出滑轨边界
                mouse_x = event.pos[0]
                # 定义音效滑块宽度为20px，与背景音乐滑块宽度一致
                sounds_slider_width = 20
                # 限制鼠标位置在滑轨范围内，考虑滑块宽度
                relative_x = max(0, min(self.sounds_slider_rect.width - sounds_slider_width, mouse_x - self.sounds_slider_rect.left))
                # 计算音量比例
                self.sounds_volume = max(0, min(1, relative_x / (self.sounds_slider_rect.width - sounds_slider_width)))
                # 更新所有音效的音量，基于SOUND_VOLUMES中的值作为100%
                self.apply_sounds_volume()
                volume_changed = True
        
        # 如果音量发生了变化，保存设置
        if volume_changed:
            settings = {
                "music_volume": self.music_volume,
                "sounds_volume": self.sounds_volume
            }
            save_settings(settings)

    def draw_settings_screen(self, background, from_pause=False):
        """
        绘制设置界面
        
        Args:
            background: 背景对象
            from_pause (bool): 是否从暂停界面进入
            
        Returns:
            pygame.Rect: 返回按钮的矩形对象
        """
        # 填充背景并绘制背景图像
        self.screen.fill(COLORS['black'])
        background.update(None, 0, 0)
        background.draw(self.screen)
        
        # 加载字体文件
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        font_path = os.path.join(base_path, 'assets', 'fonts', 'pixel_script.ttf')
        title_font = pygame.font.Font(font_path, FONT_SIZES['upgrade_title'])
        text_font = pygame.font.Font(font_path, FONT_SIZES['upgrade_description'])
        
        # 绘制标题
        title_text = title_font.render('★ 游 戏 设 置 ★', True, COLORS['white'])
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 80))
        
        # 显示设置选项
        settings_entries = ["背景音乐音量：", "游戏音效音量："]
        
        # 绘制设置条目
        y_offset = 200
        for entry in settings_entries:
            # 绘制音量控制滑块
            if entry == "背景音乐音量：":
                # 文本与滑轨并排显示
                entry_text = text_font.render(entry, True, COLORS['white'])
                # 将文本放置在滑轨左侧
                self.screen.blit(entry_text, (SCREEN_WIDTH // 2 - 250, y_offset))
                
                # 滑块轨道
                slider_x = SCREEN_WIDTH // 2 - 75
                slider_y = y_offset + entry_text.get_height() // 2 - 5
                self.slider_rect = pygame.Rect(slider_x, slider_y, 250, 15)
                # 使用圆角矩形绘制滑轨，半径为5像素
                pygame.draw.rect(self.screen, COLORS['white'], self.slider_rect, border_radius=5)
                
                # 滑块按钮
                # 根据music_volume(0-1)计算实际位置，确保滑块不会超出滑轨边界
                slider_width = 15  # 新的滑块宽度
                knob_x = slider_x + int(self.music_volume * (self.slider_rect.width - slider_width))
                # 滑块按钮高度为23，并保持在同一垂直位置
                slider_knob_height = 23
                # 调整滑块垂直位置，使其居中对齐滑轨
                knob_y = slider_y - (slider_knob_height - 15) // 2
                self.slider_knob_rect = pygame.Rect(knob_x, knob_y, slider_width, slider_knob_height)
                # 使用圆角矩形绘制滑块按钮，半径为5像素使其呈圆形
                pygame.draw.rect(self.screen, COLORS['red'], self.slider_knob_rect, border_radius=5)
                
                # 显示音量百分比
                volume_text = text_font.render(f"{int(self.music_volume * 100)}%", True, COLORS['white'])
                self.screen.blit(volume_text, (SCREEN_WIDTH // 2 + 200, y_offset))
                
            elif entry == "游戏音效音量：":
                # 文本与滑轨并排显示
                entry_text = text_font.render(entry, True, COLORS['white'])
                # 将文本放置在滑轨左侧
                self.screen.blit(entry_text, (SCREEN_WIDTH // 2 - 250, y_offset))
                
                # 滑块轨道
                slider_x = SCREEN_WIDTH // 2 - 75
                slider_y = y_offset + entry_text.get_height() // 2 - 5
                self.sounds_slider_rect = pygame.Rect(slider_x, slider_y, 250, 15)
                # 使用圆角矩形绘制滑轨，半径为5像素
                pygame.draw.rect(self.screen, COLORS['white'], self.sounds_slider_rect, border_radius=5)
                
                # 滑块按钮
                # 根据sounds_volume(0-1)计算实际位置，确保滑块不会超出滑轨边界
                # 定义音效滑块宽度为15px，与背景音乐滑块宽度一致
                sounds_slider_width = 15
                # 计算滑块位置
                knob_x = slider_x + int(self.sounds_volume * (self.sounds_slider_rect.width - sounds_slider_width))
                # 滑块按钮高度为23，并保持在同一垂直位置
                sounds_slider_knob_height = 23
                # 调整滑块垂直位置，使其居中对齐滑轨
                knob_y = slider_y - (sounds_slider_knob_height - 15) // 2
                self.sounds_slider_knob_rect = pygame.Rect(knob_x, knob_y, sounds_slider_width, sounds_slider_knob_height)
                # 使用圆角矩形绘制滑块按钮，半径为5像素使其呈圆形
                pygame.draw.rect(self.screen, COLORS['red'], self.sounds_slider_knob_rect, border_radius=5)
                
                # 显示音量百分比
                volume_text = text_font.render(f"{int(self.sounds_volume * 100)}%", True, COLORS['white'])
                self.screen.blit(volume_text, (SCREEN_WIDTH // 2 + 200, y_offset))
            
            y_offset += 100
        
        # 创建并绘制返回按钮
        button_font = pygame.font.Font(font_path, 30)
        # 根据来源决定按钮文本
        return_text_content = "返回游戏" if from_pause else "返回菜单"
        return_text = button_font.render(return_text_content, True, COLORS['white'])
        return_text_hover = button_font.render(return_text_content, True, COLORS['red'])
        text_width, text_height = return_text.get_size()
        
        # 添加悬停动画效果
        mouse_pos = pygame.mouse.get_pos()
        button_x = SCREEN_WIDTH // 2 - text_width // 2
        button_y = SCREEN_HEIGHT - text_height - 50
        return_button = pygame.Rect(button_x - 20, button_y - 10, text_width + 40, text_height + 20)
        
        # 检查鼠标是否悬停在按钮上，并添加缩放动画
        scale_factor = 1.0
        if return_button.collidepoint(mouse_pos):
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
        
        pygame.display.flip()
        return return_button