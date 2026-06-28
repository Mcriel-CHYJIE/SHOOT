"""
=============================================================================
 主循环模块 — 事件处理与界面渲染调度
=============================================================================
 所属功能块: 核心引擎
 功能描述  : 处理用户输入事件、根据游戏状态调度界面渲染
             包含引导画面、按钮交互、游戏主循环控制
=============================================================================
"""
import sys
import os
import pygame

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from src.core.resource_manager import load_font
from src.data_manager import (
    load_settings, save_all_data, add_game_record,
    get_leaderboard_data, save_settings, get_settings, reset_last_record,
)

# 导入 engine 模块（非变量导入，确保 init_game 后的状态变化能被正确获取）
import src.engine as eng


def handle_events():
    """处理游戏事件"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            eng.player_instance.should_play_entrance_animation = False
            eng.state.running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and eng.state.game_over:
                eng.state.start_screen = True
                eng.state.game_over = False
                eng.state.END_sound_played = False
                eng.player_instance.should_play_entrance_animation = False
                eng.menu_manager.level_screen.selected_level = 0
                eng.reset_game()
                try:
                    eng.sound_manager.stop_all_sounds()
                except:
                    pygame.mixer.stop()

            elif (event.key == pygame.K_SPACE and not eng.state.game_over
                  and not eng.state.start_screen and not eng.state.leaderboard_screen
                  and not eng.state.settings_screen and not eng.state.pause_screen
                  and not eng.state.level_select_screen):
                for boss in eng.bosses:
                    if boss.rail_active:
                        if abs(boss.rail_position - boss.rail_success_position) <= boss.rail_success_range / 2:
                            boss.shield_temp_deactivated = True
                            boss.shield_deactivation_time = pygame.time.get_ticks()
                            eng.sound_manager.play_sound('up')
                            boss.rail_active = False
                        else:
                            boss.rail_shake_active = True
                            boss.rail_shake_timer = pygame.time.get_ticks()
                            eng.sound_manager.play_sound('error')
                            boss.health += 50
                            boss.max_health += 50

            elif (event.key == pygame.K_q and not eng.state.game_over
                  and not eng.state.start_screen and not eng.state.leaderboard_screen
                  and not eng.state.settings_screen and not eng.state.pause_screen
                  and not eng.state.level_select_screen):
                eng.skill_system.use_q_skill(pygame.time.get_ticks())

            elif (event.key == pygame.K_e and not eng.state.game_over
                  and not eng.state.start_screen and not eng.state.leaderboard_screen
                  and not eng.state.settings_screen and not eng.state.pause_screen
                  and not eng.state.level_select_screen):
                eng.skill_system.use_e_skill(pygame.time.get_ticks())

        elif not eng.state.game_over and event.type == pygame.MOUSEBUTTONDOWN:
            _handle_mouse_click(event.pos)

        elif eng.state.game_over and eng.menu_manager.gameover_screen:
            action = eng.menu_manager.gameover_screen.handle_event(event)
            if action == 'restart':
                eng.state.start_screen = False
                eng.state.level_select_screen = True
                eng.state.game_over = False
                eng.state.END_sound_played = False
                eng.player_instance.should_play_entrance_animation = True
                eng.menu_manager.level_screen.selected_level = 0
                eng.reset_game()
            elif action == 'leaderboard':
                eng.state.game_over = False
                eng.state.leaderboard_screen = True
                eng.state.from_gameover = True
            elif action == 'menu':
                eng.state.start_screen = True
                eng.state.game_over = False
                eng.state.END_sound_played = False
                eng.player_instance.should_play_entrance_animation = False
                eng.menu_manager.level_screen.selected_level = 0
                eng.reset_game()
                try:
                    eng.sound_manager.stop_all_sounds()
                except:
                    pygame.mixer.stop()

        if eng.state.settings_screen and eng.menu_manager.settings_screen:
            eng.menu_manager.settings_screen.handle_mouse_event(event)


def _handle_mouse_click(pos):
    """根据当前界面分发点击事件"""
    if eng.state.start_screen:
        _handle_start_click(pos)
    elif eng.state.level_select_screen:
        _handle_level_select_click(pos)
    elif eng.state.leaderboard_screen:
        _handle_leaderboard_click(pos)
    elif eng.state.settings_screen:
        _handle_settings_click(pos)
    elif eng.state.pause_screen:
        _handle_pause_click(pos)
    else:
        _handle_game_click(pos)


def _handle_start_click(pos):
    if eng.menu_manager.start_button and eng.menu_manager.start_button.collidepoint(pos):
        eng.sound_manager.play_sound('button')
        eng.state.start_screen = False
        eng.state.level_select_screen = True
        eng.state.guide_start_time = 0
        eng.state.guide_image_loaded = False
        eng.state.guide_image = None
        eng.state.enemies_can_spawn = False
        eng.reset_game()
    elif eng.menu_manager.leaderboard_button and eng.menu_manager.leaderboard_button.collidepoint(pos):
        eng.sound_manager.play_sound('button')
        eng.state.start_screen = False
        eng.state.leaderboard_screen = True
        eng.state.from_pause_to_leaderboard = False
    elif eng.menu_manager.settings_button and eng.menu_manager.settings_button.collidepoint(pos):
        eng.sound_manager.play_sound('button')
        eng.state.start_screen = False
        eng.state.settings_screen = True
        eng.state.from_pause_to_settings = False


def _handle_level_select_click(pos):
    if eng.menu_manager.level_screen.handle_level_selection(pos):
        return
    if eng.state.level_return_button and eng.state.level_return_button.collidepoint(pos):
        eng.sound_manager.play_sound('button')
        eng.menu_manager.level_screen.selected_level = 0
        eng.state.level_select_screen = False
        eng.state.start_screen = True
        return
    if eng.state.challenge_button and eng.state.challenge_button.collidepoint(pos):
        if eng.menu_manager.level_screen.selected_level > 0:
            eng.sound_manager.play_sound('button')
            eng.player_instance.should_play_entrance_animation = True
            eng.reset_game()
            eng.state.level_select_screen = False
            idx = eng.menu_manager.level_screen.selected_level - 1
            if idx < len(eng.menu_manager.level_screen.planet_images):
                eng.background.set_selected_planet(eng.menu_manager.level_screen.planet_images[idx])
        else:
            eng.sound_manager.play_sound('error')


def _handle_leaderboard_click(pos):
    if eng.state.leaderboard_return_button and eng.state.leaderboard_return_button.collidepoint(pos):
        eng.sound_manager.play_sound('button')
        eng.state.leaderboard_screen = False
        if eng.state.from_pause_to_leaderboard:
            eng.state.pause_screen = True
            eng.state.from_pause_to_leaderboard = False
        elif eng.state.from_gameover:
            eng.state.game_over = True
            eng.state.from_gameover = False
        else:
            eng.state.start_screen = True


def _handle_settings_click(pos):
    if eng.state.settings_return_button and eng.state.settings_return_button.collidepoint(pos):
        eng.sound_manager.play_sound('button')
        eng.state.settings_screen = False
        if eng.state.from_pause_to_settings:
            eng.state.pause_screen = True
            eng.state.from_pause_to_settings = False
        else:
            eng.state.start_screen = True


def _handle_pause_click(pos):
    if eng.state.pause_return_button and eng.state.pause_return_button.collidepoint(pos):
        eng.sound_manager.play_sound('button')
        eng.state.pause_screen = False
        eng.state.game_paused = False
        eng.menu_manager.pause_screen.menu_confirm_state = False
        pygame.time.delay(100)
    elif eng.state.pause_leaderboard_button and eng.state.pause_leaderboard_button.collidepoint(pos):
        eng.sound_manager.play_sound('button')
        eng.state.pause_screen = False
        eng.state.leaderboard_screen = True
        eng.menu_manager.pause_screen.menu_confirm_state = False
        eng.state.from_pause_to_leaderboard = True
    elif eng.state.pause_settings_button and eng.state.pause_settings_button.collidepoint(pos):
        eng.sound_manager.play_sound('button')
        eng.state.pause_screen = False
        eng.state.settings_screen = True
        eng.menu_manager.pause_screen.menu_confirm_state = False
        eng.state.from_pause_to_settings = True
    elif (hasattr(eng.menu_manager.pause_screen, 'menu_confirm_state')
          and eng.menu_manager.pause_screen.menu_confirm_state
          and eng.state.pause_menu_button and eng.state.pause_menu_button.collidepoint(pos)):
        eng.sound_manager.play_sound('button')
        eng.state.pause_screen = False
        eng.state.start_screen = True
        eng.menu_manager.pause_screen.menu_confirm_state = False
        eng.player_instance.should_play_entrance_animation = False
        eng.player_instance.direction = 0
        eng.player_instance.target_direction = 0
        eng.menu_manager.level_screen.selected_level = 0
    elif eng.state.pause_menu_button and eng.state.pause_menu_button.collidepoint(pos):
        eng.sound_manager.play_sound('button')
        eng.menu_manager.pause_screen.menu_confirm_state = True


def _handle_game_click(pos):
    eng.menu_manager.handle_button_click()
    if not eng.state.game_paused and not eng.state.pause_screen:
        if eng.menu_manager.upgrade_button and eng.menu_manager.upgrade_button.collidepoint(pos):
            eng.sound_manager.play_sound('button')
            eng.state.game_paused = True
        elif eng.menu_manager.pause_button and eng.menu_manager.pause_button.collidepoint(pos):
            eng.sound_manager.play_sound('button')
            eng.state.pause_screen = True
            eng.state.game_paused = True
    elif eng.state.game_paused and not eng.state.pause_screen:
        if eng.menu_manager.return_button and eng.menu_manager.return_button.collidepoint(pos):
            eng.sound_manager.play_sound('button')
            eng.state.game_paused = False
            pygame.time.delay(100)


# ──────────────────────────────────────────────
# 渲染
# ──────────────────────────────────────────────

def render_game():
    """根据当前界面状态渲染画面"""
    if eng.state.start_screen:
        eng.background.set_show_planet_image(False)
        eng.menu_manager.draw_start_screen(eng.background)
    elif eng.state.level_select_screen:
        eng.background.set_show_planet_image(False)
        _render_level_select()
    elif eng.state.leaderboard_screen:
        eng.background.set_show_planet_image(False)
        _render_leaderboard()
    elif eng.state.settings_screen:
        eng.background.set_show_planet_image(False)
        _render_settings()
    elif eng.state.pause_screen:
        eng.background.set_show_planet_image(False)
        _render_pause()
    elif not eng.state.game_over:
        eng.background.set_show_planet_image(True)
        _render_gameplay()
    else:
        eng.background.set_show_planet_image(False)
        _play_end_sound_once()
        eng.menu_manager.draw_gameover_screen(eng.background)


def _play_end_sound_once():
    if not eng.state.END_sound_played:
        try:
            eng.sound_manager.play_sound('end')
        except Exception:
            pass
        eng.state.END_sound_played = True


def _render_level_select():
    challenge_btn, ret_btn = eng.menu_manager.draw_level_select_screen(eng.background)
    eng.state.challenge_button = challenge_btn
    eng.state.level_return_button = ret_btn


def _render_leaderboard():
    eng.state.leaderboard_return_button = eng.menu_manager.draw_leaderboard_screen(
        eng.background, eng.state.from_pause_to_leaderboard, eng.state.from_gameover
    )


def _render_settings():
    eng.state.settings_return_button = eng.menu_manager.draw_settings_screen(
        eng.background, eng.state.from_pause_to_settings
    )


def _render_pause():
    (eng.state.pause_return_button, eng.state.pause_menu_button,
     eng.state.pause_leaderboard_button, eng.state.pause_settings_button) = \
        eng.menu_manager.draw_pause_screen(eng.background)


def _render_gameplay():
    """渲染游戏进行界面"""
    now = pygame.time.get_ticks()
    if eng.state.guide_start_time == 0:
        eng.state.guide_start_time = now

    if not eng.state.enemies_can_spawn and now - eng.state.guide_start_time >= eng.state.guide_duration:
        eng.state.enemies_can_spawn = True

    if not eng.state.game_paused:
        eng.update_player_and_entities()
        eng.draw_entities()
        eng.check_shoot(now)

        if eng.state.enemies_can_spawn:
            eng.spawn_enemies_and_rewards(now)

        eng.update_game_stats()

        if not eng.check_collisions():
            eng.state.game_over = True

        eng.render_gameplay_hud()
        eng.menu_manager.draw_upgrade_button()
        eng.menu_manager.draw_pause_button()

        if now - eng.state.guide_start_time < eng.state.guide_duration:
            _draw_game_guide()
    else:
        eng.background.set_show_planet_image(False)
        eng.menu_manager.draw_upgrade_screen(eng.background)


def _draw_game_guide():
    """绘制引导图片 + 聊天气泡 + 逐字动画"""
    eng.state.load_guide_image()
    if not eng.state.guide_image:
        return

    screen = eng.screen
    now = pygame.time.get_ticks()
    elapsed = now - eng.state.guide_start_time
    fade_duration = 1000
    alpha = 255
    if elapsed > eng.state.guide_duration - fade_duration:
        alpha = max(0, 255 - int(255 * (elapsed - (eng.state.guide_duration - fade_duration)) / fade_duration))

    # 聊天气泡
    bubble_w, bubble_h = 500, 100
    bubble_x = 250 + eng.state.guide_image.get_width() + 10
    bubble_y = SCREEN_HEIGHT - bubble_h - 75

    if alpha < 255:
        bub = pygame.Surface((bubble_w, bubble_h), pygame.SRCALPHA)
        pygame.draw.rect(bub, (200, 200, 200, alpha), (0, 0, bubble_w, bubble_h), 1, border_radius=15)
        screen.blit(bub, (bubble_x, bubble_y))
    else:
        pygame.draw.rect(screen, (200, 200, 200), (bubble_x, bubble_y, bubble_w, bubble_h), 1, border_radius=15)

    # 引导图
    img_x, img_y = 400, SCREEN_HEIGHT - eng.state.guide_image.get_height() - 80
    if alpha < 255:
        copy = eng.state.guide_image.copy()
        temp = pygame.Surface(copy.get_size(), pygame.SRCALPHA)
        temp.fill((255, 255, 255, alpha))
        copy.blit(temp, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(copy, (img_x, img_y))
    else:
        screen.blit(eng.state.guide_image, (img_x, img_y))

    # 文字
    try:
        font = load_font('fonts', 'pixel_script.ttf', size=18)
    except (pygame.error, FileNotFoundError):
        font = pygame.font.SysFont(None, 18)

    texts = ["", "挑战击败更多敌人数量以拿到最高分", "通过升级菜单以消耗积分来提升属性", ""]
    total_chars = sum(len(t) for t in texts)
    shown = min(int((elapsed / 1000.0) * 15), total_chars)

    char_count = 0
    for line in texts:
        if char_count >= shown:
            continue
        display_text = line if char_count + len(line) <= shown else line[:shown - char_count]
        char_count += len(line)
        text_surf = font.render(display_text, True, 'white')
        if alpha < 255:
            copy = text_surf.copy()
            temp = pygame.Surface(copy.get_size(), pygame.SRCALPHA)
            temp.fill((255, 255, 255, alpha))
            copy.blit(temp, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(copy, (bubble_x + 150, bubble_y + 10 + texts.index(line) * 20))
        else:
            screen.blit(text_surf, (bubble_x + 150, bubble_y + 10 + texts.index(line) * 20))


# ──────────────────────────────────────────────
# 主函数
# ──────────────────────────────────────────────

def main():
    """游戏入口"""
    eng.init_game()

    eng.state.from_pause_to_leaderboard = False
    eng.state.from_pause_to_settings = False
    eng.state.from_gameover = False
    eng.state.guide_start_time = 0
    eng.state.enemies_can_spawn = False
    eng.state.level_select_screen = False
    eng.state.level_return_button = None
    eng.state.level_buttons = []
    eng.state.challenge_button = None

    while eng.state.running:
        handle_events()
        render_game()
        pygame.display.flip()
        eng.clock.tick(FPS)

        eng.explosions[:] = [e for e in eng.explosions if e.get_current_frame()]
        if not eng.explosions:
            eng.state.player_explosion = False

    pygame.quit()
