"""
=============================================================================
 排行榜界面 — 高分展示
=============================================================================
 所属功能块: 界面系统
 功能描述  : 显示历史高分记录排名，支持从游戏结束/暂停界面进入
=============================================================================
"""
import os
import sys
import math
import pygame
from pygame.locals import QUIT, KEYDOWN, K_SPACE, K_ESCAPE

from src.objects.player import Player
from src.config import *
from src.data_manager import get_leaderboard_data


class LeaderboardScreen:

    def __init__(self, screen, player_instance, sounds):

        self.screen = screen
        self.player_instance = player_instance
        self.sounds = sounds

    def is_mouse_over_button(self, button):

        if button is None:
            return False
        mouse_pos = pygame.mouse.get_pos()
        return button.collidepoint(mouse_pos)

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
        title_text = title_font.render('★ 游 戏 排 行 ★', True, COLORS['white'])
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 80))
        
        # 显示排行榜内容
        leaderboard_data = get_leaderboard_data()
        
        if not leaderboard_data:
            # 如果没有排行榜数据
            no_data_text = text_font.render("暂无排行榜数据", True, COLORS['white'])
            self.screen.blit(no_data_text, (SCREEN_WIDTH // 2 - no_data_text.get_width() // 2, 250))
        else:
            # 定义列位置，使得分列在正中间
            rank_x = SCREEN_WIDTH // 2 - 220  # 排行列
            score_x = SCREEN_WIDTH // 2 - 15   # 得分列
            enemies_x = SCREEN_WIDTH // 2 + 200  # 击败数列
            
            # 绘制表头
            header_font = pygame.font.Font(font_path, FONT_SIZES['upgrade_description'])
            rank_header = header_font.render("排名", True, COLORS['white'])
            score_header = header_font.render("得分", True, COLORS['white'])
            enemies_header = header_font.render("击败数", True, COLORS['white'])
            
            self.screen.blit(rank_header, (rank_x, 150))
            self.screen.blit(score_header, (score_x, 150))
            self.screen.blit(enemies_header, (enemies_x, 150))
            
            # 绘制排行榜条目（只显示前5名）
            y_offset = 230
            for i, entry in enumerate(leaderboard_data[:5]):
                # 根据排名设置颜色
                if i == 0:
                    color = (255, 215, 0)  # 金色
                elif i == 1:
                    color = (192, 192, 192)  # 银色
                elif i == 2:
                    color = (205, 127, 50)  # 铜色
                else:
                    color = COLORS['white']

                # 创建文本表面
                rank_text = text_font.render(str(i + 1), True, color)
                score_text = text_font.render(str(entry["score"]), True, color)
                enemies_text = text_font.render(str(entry["enemies"]), True, color)

                # 绘制条目，严格对齐表头列
                self.screen.blit(rank_text, (rank_x + 13, y_offset))
                self.screen.blit(score_text, (score_x - 3, y_offset))
                self.screen.blit(enemies_text, (enemies_x + 3, y_offset))
                
                y_offset += 50
        
        # 创建并绘制返回按钮
        button_font = pygame.font.Font(font_path, 30)
        # 根据来源决定按钮文本
        if from_pause:
            return_text_content = "返回游戏"
        elif from_gameover:
            return_text_content = "返回结算"
        else:
            return_text_content = "返回菜单"
                
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
