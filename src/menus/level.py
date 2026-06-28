"""
=============================================================================
 关卡选择界面 — 行星关卡选择
=============================================================================
 所属功能块: 界面系统
 功能描述  : 展示可选关卡行星图像，玩家点击选择后进入对应关卡
=============================================================================
"""
import os
import sys
import math
import pygame
from pygame.locals import QUIT, KEYDOWN, K_SPACE, K_ESCAPE

from src.objects.player import Player
from src.config import *


class LevelSelectScreen:
    """
    关卡选择界面类
    管理关卡选择界面的显示和交互
    """

    def __init__(self, screen, player_instance, sounds):
        """
        初始化关卡选择界面
        
        Args:
            screen: Pygame屏幕对象
            player_instance: 玩家实例
            sounds: 音效字典
        """
        self.screen = screen
        self.player_instance = player_instance
        self.sounds = sounds

        # 按钮
        self.challenge_button = None
        self.return_button = None
        
        # 关卡图片
        self.planet_images = []
        self.selected_level = 0  # 当前选择的关卡（0表示未选择）
        self.level_rects = []  # 存储每个关卡图片的矩形区域
        self.level_hover_state = [0] * 4  # 存储每个关卡的悬停状态（用于动画）
        self.load_planet_images()

    def load_planet_images(self):
        """
        加载关卡图片
        """
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        planets_path = os.path.join(base_path, 'assets', 'images', 'Planets')
        
        # 加载4张行星图片
        for i in range(4):
            try:
                image_path = os.path.join(planets_path, f'{i}.png')
                image = pygame.image.load(image_path).convert_alpha()
                # 缩放图片到合适的大小
                image = pygame.transform.scale(image, (120, 120))
                self.planet_images.append(image)
            except pygame.error:
                # 如果加载失败，创建一个替代的圆形表面
                image = pygame.Surface((120, 120), pygame.SRCALPHA)
                pygame.draw.circle(image, (100, 150, 200), (60, 60), 60)
                self.planet_images.append(image)

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

    def handle_level_selection(self, pos):
        """
        处理关卡选择
        
        Args:
            pos (tuple): 鼠标点击位置坐标 (x, y)
        """
        # 检查是否点击了某个关卡图片
        for i, rect in enumerate(self.level_rects):
            if rect.collidepoint(pos):
                self.selected_level = i + 1  # 设置选中的关卡（1-4）
                self.sounds['button'].play()
                return True
        return False

    def create_outline_surface(self, image, outline_color=(255, 255, 0), outline_width=3):
        """
        为图像创建像素级描边效果
        
        Args:
            image: 原始图像
            outline_color: 描边颜色
            outline_width: 描边宽度
            
        Returns:
            pygame.Surface: 带描边效果的图像
        """
        # 获取原始图像的尺寸
        width, height = image.get_size()
        
        # 创建一个新的表面来容纳描边效果
        outlined_surface = pygame.Surface((width + outline_width * 2, height + outline_width * 2), pygame.SRCALPHA)
        
        # 创建描边遮罩
        mask = pygame.mask.from_surface(image)
        
        # 获取轮廓点
        outline_points = mask.outline()
        
        # 如果有轮廓点，则绘制描边
        if outline_points:
            # 在每个方向上绘制轮廓点以创建描边效果
            for offset_x in range(-outline_width, outline_width + 1):
                for offset_y in range(-outline_width, outline_width + 1):
                    # 只在边缘绘制以节省性能
                    if abs(offset_x) == outline_width or abs(offset_y) == outline_width:
                        offset_points = [(x + outline_width + offset_x, y + outline_width + offset_y) for x, y in outline_points]
                        pygame.draw.polygon(outlined_surface, outline_color, offset_points, outline_width)
        
        # 将原始图像绘制在描边表面的中心
        outlined_surface.blit(image, (outline_width, outline_width))
        
        return outlined_surface

    def draw_level_select_screen(self, background):
        """
        绘制关卡选择界面
        
        Args:
            background: 背景对象
            
        Returns:
            tuple: 返回挑战按钮和返回按钮
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
        small_font = pygame.font.Font(font_path, FONT_SIZES['tip'])
        
        # 绘制标题
        title_text = title_font.render('★ 关卡选择 ★', True, COLORS['white'])
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 80))

        # 在屏幕中央区域绘制关卡图片
        self.level_rects = []  # 重置关卡矩形列表
        if self.planet_images:
            # 计算图片排列位置，使其在区域内居中
            total_images_width = len(self.planet_images) * 120 + (len(self.planet_images) - 1) * 60  # 图片宽度 + 间距
            start_x = SCREEN_WIDTH // 2 - total_images_width // 2
            y_position = SCREEN_HEIGHT // 2 - 160  # 垂直居中
            
            # 绘制4张图片并排显示
            for i, image in enumerate(self.planet_images):
                x_position = start_x + i * (120 + 60)  # 图片宽度 + 间距
                
                # 创建关卡图片的矩形区域，用于点击检测
                level_rect = pygame.Rect(x_position, y_position, 120, 120)
                self.level_rects.append(level_rect)
                
                # 检查鼠标是否悬停在关卡图片上
                mouse_pos = pygame.mouse.get_pos()
                is_hovering = level_rect.collidepoint(mouse_pos)
                
                # 更新悬停状态动画
                if is_hovering:
                    self.level_hover_state[i] = min(1.0, self.level_hover_state[i] + 0.1)
                else:
                    self.level_hover_state[i] = max(0.0, self.level_hover_state[i] - 0.1)
                
                # 根据悬停状态计算缩放因子
                hover_scale = 1.0 + 0.15 * self.level_hover_state[i]
                scaled_size = int(120 * hover_scale)
                
                # 缩放图片
                scaled_image = pygame.transform.scale(image, (scaled_size, scaled_size))
                
                # 计算居中绘制位置（考虑缩放）
                draw_x = x_position + 60 - scaled_size // 2
                draw_y = y_position + 60 - scaled_size // 2
                
                # 如果这是选中的关卡，创建带描边效果的图像
                if self.selected_level == i + 1:
                    # 创建带描边效果的图像
                    outlined_image = self.create_outline_surface(scaled_image, COLORS['yellow'], 2)
                    # 调整绘制位置以适应描边
                    outline_offset = 2
                    self.screen.blit(outlined_image, (draw_x - outline_offset, draw_y - outline_offset))
                else:
                    self.screen.blit(scaled_image, (draw_x, draw_y))
                
                # 在每张图片下方绘制关卡编号
                level_text = text_font.render(f"星域 {i+1}", True, COLORS['white'])
                text_x = x_position + 60 - level_text.get_width() // 2  # 图片中心对齐
                text_y = y_position + 130 + int(10 * self.level_hover_state[i])  # 悬停时轻微上移
                self.screen.blit(level_text, (text_x, text_y))

        # 如果未选择关卡，显示提示信息
        if self.selected_level == 0:
            hint_text = small_font.render("请选择挑战的星域", True, COLORS['red'])
            hint_x = SCREEN_WIDTH // 2 - hint_text.get_width() // 2
            hint_y = SCREEN_HEIGHT // 2 - 245
            self.screen.blit(hint_text, (hint_x, hint_y))

        # 创建并绘制按钮（并排显示在底部）
        button_font = pygame.font.Font(font_path, 30)
        
        # 进入挑战按钮
        challenge_text = button_font.render("进入挑战", True, COLORS['white'])
        challenge_text_hover = button_font.render("进入挑战", True, COLORS['red'])
        challenge_text_width, challenge_text_height = challenge_text.get_size()
        
        # 返回菜单按钮
        return_text = button_font.render("退出游戏", True, COLORS['white'])
        return_text_hover = button_font.render("退出游戏", True, COLORS['red'])
        return_text_width, return_text_height = return_text.get_size()
        
        # 添加悬停动画效果
        mouse_pos = pygame.mouse.get_pos()
        
        # 计算按钮位置
        button_y = SCREEN_HEIGHT - challenge_text_height - 50
        total_width = challenge_text_width + return_text_width + 60  # 两个按钮加上间距
        start_x = SCREEN_WIDTH // 2 - total_width // 2
        
        # 进入挑战按钮位置
        challenge_button_x = start_x
        self.challenge_button = pygame.Rect(challenge_button_x - 20, button_y - 10, challenge_text_width + 40, challenge_text_height + 20)
        
        # 检查鼠标是否悬停在进入挑战按钮上，并添加缩放动画
        challenge_scale_factor = 1.0
        if self.challenge_button.collidepoint(mouse_pos):
            time = pygame.time.get_ticks()
            challenge_scale_factor = 1.0 + 0.1 * abs(math.sin(time * 0.005))
            scaled_text = pygame.transform.smoothscale(
                challenge_text_hover, 
                (int(challenge_text_width * challenge_scale_factor), int(challenge_text_height * challenge_scale_factor))
            )
            self.screen.blit(
                scaled_text, 
                (challenge_button_x + challenge_text_width/2 - scaled_text.get_width()/2, 
                 button_y + challenge_text_height/2 - scaled_text.get_height()/2)
            )
        else:
            self.screen.blit(challenge_text, (challenge_button_x, button_y))
        
        # 返回菜单按钮位置
        return_button_x = start_x + challenge_text_width + 60
        self.return_button = pygame.Rect(return_button_x - 20, button_y - 10, return_text_width + 40, return_text_height + 20)
        
        # 检查鼠标是否悬停在返回菜单按钮上，并添加缩放动画
        return_scale_factor = 1.0
        if self.return_button.collidepoint(mouse_pos):
            time = pygame.time.get_ticks()
            return_scale_factor = 1.0 + 0.1 * abs(math.sin(time * 0.005))
            scaled_text = pygame.transform.smoothscale(
                return_text_hover, 
                (int(return_text_width * return_scale_factor), int(return_text_height * return_scale_factor))
            )
            self.screen.blit(
                scaled_text, 
                (return_button_x + return_text_width/2 - scaled_text.get_width()/2, 
                 button_y + return_text_height/2 - scaled_text.get_height()/2)
            )
        else:
            self.screen.blit(return_text, (return_button_x, button_y))
        
        pygame.display.flip()
        return self.challenge_button, self.return_button