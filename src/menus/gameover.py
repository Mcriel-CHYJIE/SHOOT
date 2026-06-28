"""
=============================================================================
 游戏结束界面 — 得分展示与操作
=============================================================================
 所属功能块: 界面系统
 功能描述  : 显示最终得分、击败敌人数等统计数据
             提供重新开始 / 排行榜 / 返回主菜单功能
=============================================================================
"""
import os
import sys
import math
import pygame
import random
from src.config import *


class GameOverScreen:
    """
    游戏结束界面类
    管理游戏结束界面的显示和交互
    """

    def __init__(self, screen, player_instance, sounds, menu_manager):
        """
        初始化游戏结束界面
        
        Args:
            screen: Pygame屏幕对象
            player_instance: 玩家实例
            sounds: 音效字典
            menu_manager: 菜单管理器实例
        """
        self.screen = screen
        self.player_instance = player_instance
        self.sounds = sounds
        self.menu_manager = menu_manager
        
        # 按钮相关变量
        self.restart_button = None
        self.leaderboard_button = None
        self.menu_button = None
        
        # 分数动画相关变量
        self.animation_start_time = None
        self.final_score = None
        self.current_animated_score = 0
        self.animation_complete = False

    def render_final_score(self, background):
        """
        渲染最终得分界面
        
        Args:
            background: 背景对象
        """
        # 填充背景并绘制背景图像
        self.screen.fill(COLORS['black'])
        background.update(None, 0, 0)
        background.draw(self.screen)
        
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        font_path = os.path.join(base_path, 'assets', 'fonts', 'pixel_script.ttf')
        font = pygame.font.Font(font_path, 100)
        
        # 保存游戏记录到排行榜
        self.save_game_record()
        
        # 计算最终分数（用于显示）
        upgrade_cost = (
            self.menu_manager.hp_score * self.menu_manager.upgrade_counts['HP'] + 
            self.menu_manager.shoot_score * self.menu_manager.upgrade_counts['SHOOT'] + 
            self.menu_manager.sp_score * self.menu_manager.upgrade_counts['SP']
        )
        
        final_score = self.player_instance.score + upgrade_cost
        if final_score == 20:
            final_score = 0
            
        # 初始化动画参数
        if self.final_score != final_score:
            self.final_score = final_score
            self.animation_start_time = pygame.time.get_ticks()
            self.current_animated_score = final_score  # 初始值设为最终分数
            self.animation_complete = False
        
        # 处理分数动画（随机跳动）
        if not self.animation_complete and self.animation_start_time is not None:
            elapsed_time = pygame.time.get_ticks() - self.animation_start_time
            
            # 动画持续时间（毫秒）
            animation_duration = 999
            
            if elapsed_time < animation_duration:
                # 在动画期间显示随机跳动的数字
                # 跳动范围随时间逐渐缩小
                progress = elapsed_time / animation_duration
                # 跳动范围从±50%逐渐缩小到0
                jump_range = int(self.final_score * 0.5 * (1 - progress))
                
                if jump_range > 0:
                    # 生成随机跳动的分数
                    random_offset = random.randint(-jump_range, jump_range)
                    self.current_animated_score = max(0, self.final_score + random_offset)
                else:
                    # 动画接近完成，显示最终分数
                    self.current_animated_score = self.final_score
            else:
                # 动画完成，显示最终分数
                self.current_animated_score = self.final_score
                self.animation_complete = True
        else:
            # 动画已完成，显示最终分数
            self.current_animated_score = self.final_score
        
        # 显示分数
        color = (255, 0, 0) if pygame.time.get_ticks() % 2000 < 1000 else (255, 255, 255)
        final_score_text = font.render('最终得分: ' + str(self.current_animated_score), True, color)
        text_rect = final_score_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 100))
        self.screen.blit(final_score_text, text_rect)
        
        # 绘制两个按钮：游戏排行、再次挑战
        button_font = pygame.font.Font(font_path, 30)
        
        # 游戏排行按钮
        leaderboard_text = button_font.render("游戏排行", True, COLORS['white'])
        leaderboard_text_hover = button_font.render("游戏排行", True, COLORS['red'])
        leaderboard_text_width, leaderboard_text_height = leaderboard_text.get_size()
        
        # 再次挑战按钮
        restart_text = button_font.render("再次挑战", True, COLORS['white'])
        restart_text_hover = button_font.render("再次挑战", True, COLORS['red'])
        restart_text_width, restart_text_height = restart_text.get_size()
        
        # 添加悬停动画效果
        mouse_pos = pygame.mouse.get_pos()
        
        # 计算按钮位置（两个按钮并排）
        total_width = leaderboard_text_width + restart_text_width + 60  # 间距60px
        start_x = SCREEN_WIDTH // 2 - total_width // 2
        
        # 游戏排行按钮位置
        leaderboard_button_x = start_x
        leaderboard_button_y = SCREEN_HEIGHT // 2 + 50
        self.leaderboard_button = pygame.Rect(leaderboard_button_x - 20, leaderboard_button_y - 10, leaderboard_text_width + 40, leaderboard_text_height + 20)
        
        # 再次挑战按钮位置
        restart_button_x = start_x + leaderboard_text_width + 60
        restart_button_y = SCREEN_HEIGHT // 2 + 50
        self.restart_button = pygame.Rect(restart_button_x - 20, restart_button_y - 10, restart_text_width + 40, restart_text_height + 20)
        
        # 绘制游戏排行按钮
        scale_factor = 1.0
        if self.leaderboard_button.collidepoint(mouse_pos):
            time = pygame.time.get_ticks()
            scale_factor = 1.0 + 0.1 * abs(math.sin(time * 0.005))
            scaled_text = pygame.transform.smoothscale(
                leaderboard_text_hover,
                (int(leaderboard_text_width * scale_factor), int(leaderboard_text_height * scale_factor))
            )
            self.screen.blit(
                scaled_text,
                (leaderboard_button_x + leaderboard_text_width/2 - scaled_text.get_width()/2,
                 leaderboard_button_y + leaderboard_text_height/2 - scaled_text.get_height()/2)
            )
        else:
            self.screen.blit(leaderboard_text, (leaderboard_button_x, leaderboard_button_y))
            
        # 绘制再次挑战按钮
        scale_factor = 1.0
        if self.restart_button.collidepoint(mouse_pos):
            time = pygame.time.get_ticks()
            scale_factor = 1.0 + 0.1 * abs(math.sin(time * 0.005))
            scaled_text = pygame.transform.smoothscale(
                restart_text_hover,
                (int(restart_text_width * scale_factor), int(restart_text_height * scale_factor))
            )
            self.screen.blit(
                scaled_text,
                (restart_button_x + restart_text_width/2 - scaled_text.get_width()/2,
                 restart_button_y + restart_text_height/2 - scaled_text.get_height()/2)
            )
        else:
            self.screen.blit(restart_text, (restart_button_x, restart_button_y))
        
        pygame.display.flip()
        
        # 不再在此处播放游戏结束音效，避免重复播放
        # 音效已在main/game_main.py中的游戏结束画面渲染时播放

    def save_game_record(self):
        """
        保存游戏记录到排行榜
        """
        # 计算升级消耗的分数
        upgrade_cost = (
            self.menu_manager.hp_score * self.menu_manager.upgrade_counts['HP'] + 
            self.menu_manager.shoot_score * self.menu_manager.upgrade_counts['SHOOT'] + 
            self.menu_manager.sp_score * self.menu_manager.upgrade_counts['SP']
        )
        
        # 计算最终分数
        final_score = self.player_instance.score + upgrade_cost
        
        # 如果最终分数是默认的20分，则不保存记录
        if final_score == 20:
            return
        
        # 保存游戏记录到排行榜
        from src.data_manager import add_game_record
        from src.engine import stats
        enemies_defeated = stats['enemies_killed'] + stats['shooting_enemies_killed'] + stats['enemies_collided']
        add_game_record(final_score, enemies_defeated)
        
    def handle_event(self, event):
        """
        处理游戏结束界面的事件
        
        Args:
            event: Pygame事件对象
            
        Returns:
            str: 点击的按钮类型 ('restart', 'leaderboard') 或 None
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 左键点击
            if self.restart_button and self.restart_button.collidepoint(event.pos):
                self.sounds['button'].play()
                return 'restart'
            elif self.leaderboard_button and self.leaderboard_button.collidepoint(event.pos):
                self.sounds['button'].play()
                return 'leaderboard'
            
        return None