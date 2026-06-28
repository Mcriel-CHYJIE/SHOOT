"""
=============================================================================
 暂停界面 — 游戏暂停菜单
=============================================================================
 所属功能块: 界面系统
 功能描述  : 提供继续游戏、排行榜、设置、返回主菜单（二次确认防误触）
=============================================================================
"""
import os
import sys
import math
import pygame
from pygame.locals import QUIT, KEYDOWN, K_SPACE, K_ESCAPE

from src.objects.player import Player
from src.config import *


class PauseScreen:
    """
    暂停界面类
    管理暂停界面的显示、按钮交互和统计数据展示
    """

    def __init__(self, screen, player_instance, sounds):
        """
        初始化暂停界面
        
        Args:
            screen: Pygame屏幕对象
            player_instance: 玩家实例
            sounds: 音效字典
        """
        self.screen = screen
        self.player_instance = player_instance
        self.sounds = sounds
        self.menu_confirm_state = False  # 添加确认状态，用于二次确认返回主菜单

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

    def draw_pause_screen(self, background):
        """
        绘制暂停界面
        
        Args:
            background: 背景对象
            
        Returns:
            tuple: 包含各个按钮的矩形对象
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
        tip_font = pygame.font.Font(font_path, FONT_SIZES['pause_tip'])
        
        # 绘制标题
        title_text = title_font.render('★ 游 戏 暂 停 ★', True, COLORS['white'])
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 80))
        
        # 显示暂停提示和统计数据
        from src.engine import stats
        # 按照新要求定义统计数据条目
        stat_entries = [
            f"当前积分数: {self.player_instance.score}",
            f"生命升级数: {stats['hp_upgrades']}",
            f"碰撞收集的奖励总数: {stats['rewards_collected']}",
            f"发射子弹数: {stats['bullets_fired']}",
            f"弹道升级数: {stats['shoot_upgrades']}",
            f"子弹摧毁的敌人总数: {stats['enemies_killed'] + stats['shooting_enemies_killed']}",
            f"损失生命值: {stats['health_lost']}",
            f"速度升级数: {stats['speed_upgrades']}",
            f"碰撞摧毁的敌人总数: {stats['enemies_collided']}"
        ]
        
        # 绘制统计数据条目（三行三列布局）
        y_offset = 200
        row_height = 50
        column_width = 255
        
        # 三行三列显示
        for row in range(3):
            for col in range(3):
                index = row * 3 + col
                if index < len(stat_entries):
                    entry_text = text_font.render(stat_entries[index], True, COLORS['white'])
                    x_pos = SCREEN_WIDTH // 2 - column_width + col * column_width - 150
                    self.screen.blit(entry_text, (x_pos, y_offset))
            y_offset += row_height

        # 绘制暂停提示
        pause_text1 = tip_font.render('底部为攒星进度槽，收集9颗星星能蓄满能量槽且可选择触发"Q"和"E"技能其一', True, COLORS['pink'],)
        self.screen.blit(pause_text1, (SCREEN_WIDTH // 2 - pause_text1.get_width() // 2, 450))
        pause_text1 = tip_font.render('"Q"技能释放特殊星星激活后能追踪敌人，"E"技能提供10s的能量罩BUFF', True, COLORS['pink'])
        self.screen.blit(pause_text1, (SCREEN_WIDTH // 2 - pause_text1.get_width() // 2, 475))
        pause_text2 = tip_font.render('BOSS出现时会有能量罩和出现能量干扰槽，能量罩存在时无法造成伤害', True, COLORS['pink'])
        self.screen.blit(pause_text2, (SCREEN_WIDTH // 2 - pause_text2.get_width() // 2, 525))
        pause_text2 = tip_font.render('需要在能量干扰槽按下"SPACE"键进行解除操作后才能对BOSS造成伤害', True, COLORS['pink'])
        self.screen.blit(pause_text2, (SCREEN_WIDTH // 2 - pause_text2.get_width() // 2, 550))
        pause_text2 = tip_font.render('BOSS的能量干扰槽需要正确判定才能解除能量罩，否则对BOSS进行加50血量', True, COLORS['pink'])
        self.screen.blit(pause_text2, (SCREEN_WIDTH // 2 - pause_text2.get_width() // 2, 575))


        # 创建并绘制按钮（改为两列两行布局）
        button_font = pygame.font.Font(font_path, 30)
        
        # 第一行按钮
        # 返回游戏按钮
        resume_text = button_font.render("返回游戏", True, COLORS['white'])
        resume_text_hover = button_font.render("返回游戏", True, COLORS['red'])
        resume_text_width, resume_text_height = resume_text.get_size()
        
        # 添加悬停动画效果
        mouse_pos = pygame.mouse.get_pos()
        resume_button_x = SCREEN_WIDTH // 2 + 30
        resume_button_y = SCREEN_HEIGHT - resume_text_height - 125
        resume_button = pygame.Rect(resume_button_x - 20, resume_button_y - 10, resume_text_width + 40, resume_text_height + 20)
        
        # 检查鼠标是否悬停在按钮上，并添加缩放动画
        scale_factor = 1.0
        if resume_button.collidepoint(mouse_pos):
            time = pygame.time.get_ticks()
            scale_factor = 1.0 + 0.1 * abs(math.sin(time * 0.005))
            scaled_text = pygame.transform.smoothscale(
                resume_text_hover, 
                (int(resume_text_width * scale_factor), int(resume_text_height * scale_factor))
            )
            self.screen.blit(
                scaled_text, 
                (resume_button_x + resume_text_width/2 - scaled_text.get_width()/2, 
                 resume_button_y + resume_text_height/2 - scaled_text.get_height()/2)
            )
        else:
            self.screen.blit(resume_text, (resume_button_x, resume_button_y))
        
        # 游戏排行按钮
        leaderboard_text = button_font.render("游戏排行", True, COLORS['white'])
        leaderboard_text_hover = button_font.render("游戏排行", True, COLORS['red'])
        lb_text_width, lb_text_height = leaderboard_text.get_size()
        
        lb_button_x = SCREEN_WIDTH // 2 - resume_text_width - 30
        lb_button_y = SCREEN_HEIGHT - lb_text_height - 125
        leaderboard_button = pygame.Rect(lb_button_x - 20, lb_button_y - 10, lb_text_width + 40, lb_text_height + 20)
        
        # 检查鼠标是否悬停在排行榜按钮上，并添加缩放动画
        lb_scale_factor = 1.0
        if leaderboard_button.collidepoint(mouse_pos):
            time = pygame.time.get_ticks()
            lb_scale_factor = 1.0 + 0.1 * abs(math.sin(time * 0.005))
            lb_scaled_text = pygame.transform.smoothscale(
                leaderboard_text_hover, 
                (int(lb_text_width * lb_scale_factor), int(lb_text_height * lb_scale_factor))
            )
            self.screen.blit(
                lb_scaled_text, 
                (lb_button_x + lb_text_width/2 - lb_scaled_text.get_width()/2, 
                 lb_button_y + lb_text_height/2 - lb_scaled_text.get_height()/2)
            )
        else:
            self.screen.blit(leaderboard_text, (lb_button_x, lb_button_y))
        
        # 第二行按钮
        # 游戏设置按钮
        settings_text = button_font.render("游戏设置", True, COLORS['white'])
        settings_text_hover = button_font.render("游戏设置", True, COLORS['red'])
        settings_text_width, settings_text_height = settings_text.get_size()
        
        settings_button_x = SCREEN_WIDTH // 2 - settings_text_width - 30
        settings_button_y = SCREEN_HEIGHT - settings_text_height - 50
        settings_button = pygame.Rect(settings_button_x - 20, settings_button_y - 10, settings_text_width + 40, settings_text_height + 20)
        
        # 检查鼠标是否悬停在设置按钮上，并添加缩放动画
        settings_scale_factor = 1.0
        if settings_button.collidepoint(mouse_pos):
            time = pygame.time.get_ticks()
            settings_scale_factor = 1.0 + 0.1 * abs(math.sin(time * 0.005))
            settings_scaled_text = pygame.transform.smoothscale(
                settings_text_hover, 
                (int(settings_text_width * settings_scale_factor), int(settings_text_height * settings_scale_factor))
            )
            self.screen.blit(
                settings_scaled_text, 
                (settings_button_x + settings_text_width/2 - settings_scaled_text.get_width()/2, 
                 settings_button_y + settings_text_height/2 - settings_scaled_text.get_height()/2)
            )
        else:
            self.screen.blit(settings_text, (settings_button_x, settings_button_y))
        
        # 返回主菜单按钮 - 根据确认状态显示不同文本
        if self.menu_confirm_state:
            # 处于确认状态时显示确认文本
            confirm_text = button_font.render("确认退出", True, COLORS['white'])
            confirm_text_hover = button_font.render("确认退出", True, COLORS['red'])
            
            # 确认按钮
            confirm_text_width, confirm_text_height = confirm_text.get_size()
            menu_button_x = SCREEN_WIDTH // 2 + 30
            menu_button_y = SCREEN_HEIGHT - confirm_text_height - 50
            menu_button = pygame.Rect(menu_button_x - 20, menu_button_y - 10, confirm_text_width + 40, confirm_text_height + 20)
            
            # 绘制确认按钮
            if menu_button.collidepoint(mouse_pos):
                time = pygame.time.get_ticks()
                scale_factor = 1.0 + 0.1 * abs(math.sin(time * 0.005))
                scaled_text = pygame.transform.smoothscale(
                    confirm_text_hover,  # 修复：使用悬停状态文本
                    (int(confirm_text_width * scale_factor), int(confirm_text_height * scale_factor))
                )
                self.screen.blit(
                    scaled_text, 
                    (menu_button_x + confirm_text_width/2 - scaled_text.get_width()/2, 
                     menu_button_y + confirm_text_height/2 - scaled_text.get_height()/2)
                )
            else:
                self.screen.blit(confirm_text, (menu_button_x, menu_button_y))
        else:
            # 正常状态显示退出游戏按钮
            menu_text = button_font.render("退出游戏", True, COLORS['white'])
            menu_text_hover = button_font.render("退出游戏", True, COLORS['red'])
            menu_text_width, menu_text_height = menu_text.get_size()
            
            menu_button_x = SCREEN_WIDTH // 2 + 30
            menu_button_y = SCREEN_HEIGHT - menu_text_height - 50
            menu_button = pygame.Rect(menu_button_x - 20, menu_button_y - 10, menu_text_width + 40, menu_text_height + 20)
            
            # 检查鼠标是否悬停在按钮上，并添加缩放动画
            menu_scale_factor = 1.0
            if menu_button.collidepoint(mouse_pos):
                time = pygame.time.get_ticks()
                menu_scale_factor = 1.0 + 0.1 * abs(math.sin(time * 0.005))
                menu_scaled_text = pygame.transform.smoothscale(
                    menu_text_hover, 
                    (int(menu_text_width * menu_scale_factor), int(menu_text_height * menu_scale_factor))
                )
                self.screen.blit(
                    menu_scaled_text, 
                    (menu_button_x + menu_text_width/2 - menu_scaled_text.get_width()/2, 
                     menu_button_y + menu_text_height/2 - menu_scaled_text.get_height()/2)
                )
            else:
                self.screen.blit(menu_text, (menu_button_x, menu_button_y))
        
        pygame.display.flip()
        return resume_button, menu_button, leaderboard_button, settings_button