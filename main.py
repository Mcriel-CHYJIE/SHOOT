# -*- coding: utf-8 -*-
"""
=============================================================================
 SHOOT 移动版 — 双摇杆触屏适配
=============================================================================
"""
import os
import sys
import pygame

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['SDL_VIDEO_CENTERED'] = '1'

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from src.mobile_input import TouchControls
import src.engine as eng
from src.game import handle_events, render_game

VIRTUAL_W, VIRTUAL_H = SCREEN_WIDTH, SCREEN_HEIGHT
_held_keys = set()


def _apply_controls(touch):
    """
    将双摇杆状态转换为持续按键 + 鼠标事件
    - 左摇杆 → WASD 按键
    - 右摇杆 → 鼠标瞄准位置 + 射击
    """
    # ── 左摇杆 → 移动按键 ──
    dx, dy = touch.get_movement()
    wanted = set()
    if dx < -0.3:  wanted.add(pygame.K_a)
    if dx > 0.3:   wanted.add(pygame.K_d)
    if dy < -0.3:  wanted.add(pygame.K_w)
    if dy > 0.3:   wanted.add(pygame.K_s)

    for k in wanted - _held_keys:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': k}))
    for k in _held_keys - wanted:
        pygame.event.post(pygame.event.Event(pygame.KEYUP, {'key': k}))
    _held_keys.clear()
    _held_keys.update(wanted)

    # ── 右摇杆 → 鼠标瞄准 + 射击 ──
    ax, ay = touch.get_aim_screen_pos()
    pygame.event.post(pygame.event.Event(pygame.MOUSEMOTION,
                     {'pos': (ax, ay), 'rel': (0, 0), 'buttons': (0, 0, 0)}))
    if touch.is_shooting():
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                         {'pos': (ax, ay), 'button': 1}))


def main():
    pygame.init()
    pygame.mixer.init()

    # 全屏模式（手机上）或窗口模式（桌面上）
    import platform
    info = pygame.display.Info()
    is_mobile = platform.system() != "Windows"
    if is_mobile:
        flags = pygame.FULLSCREEN | pygame.DOUBLEBUF
        sw, sh = max(info.current_w, 720), max(info.current_h, 800)
    else:
        flags = 0  # 窗口模式
        sw, sh = VIRTUAL_W, VIRTUAL_H
    
    if hasattr(pygame, 'SCALED'):
        flags |= pygame.SCALED
    screen = pygame.display.set_mode((sw, sh), flags)
    pygame.display.set_caption('SHOOT')

    # 缩放
    scale = min(sw / VIRTUAL_W, sh / VIRTUAL_H)
    vw, vh = int(VIRTUAL_W * scale), int(VIRTUAL_H * scale)
    ox, oy = (sw - vw) // 2, (sh - vh) // 2

    eng.init_game()
    touch = TouchControls(VIRTUAL_W, VIRTUAL_H)
    eng.state.running = True
    clock = pygame.time.Clock()

    while eng.state.running:
        # 1. 原始事件处理（触摸转译）
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                eng.state.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_AC_BACK:
                if eng.state.start_screen or eng.state.game_over:
                    eng.state.running = False
                else:
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN,
                                                         {'key': pygame.K_ESCAPE}))
                continue
            me = touch.handle_event(event)
            if me:
                for e in me:
                    pygame.event.post(e)

        # 2. 注入双摇杆状态
        _apply_controls(touch)

        # 3. 游戏逻辑更新
        handle_events()
        eng.update_player_and_entities()
        if eng.state.enemies_can_spawn:
            eng.spawn_enemies_and_rewards(pygame.time.get_ticks())
        eng.update_game_stats()
        if not eng.check_collisions():
            eng.state.game_over = True

        # 4. 渲染
        render_game()
        if not eng.state.game_paused and not eng.state.pause_screen \
                and not eng.state.start_screen and not eng.state.settings_screen \
                and not eng.state.leaderboard_screen and not eng.state.level_select_screen:
            touch.draw(eng.screen)

        # 5. 缩放输出
        scaled = pygame.transform.smoothscale(eng.screen, (vw, vh))
        screen.fill((0, 0, 0))
        screen.blit(scaled, (ox, oy))
        pygame.display.flip()
        clock.tick(FPS)

        eng.explosions[:] = [e for e in eng.explosions if e.get_current_frame()]
        if not eng.explosions:
            eng.state.player_explosion = False

    pygame.quit()


if __name__ == '__main__':
    main()
