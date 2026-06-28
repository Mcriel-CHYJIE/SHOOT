"""
=============================================================================
 游戏引擎模块 — 核心游戏逻辑
=============================================================================
 所属功能块: 核心引擎
 功能描述  : 游戏初始化、实体更新、碰撞检测、敌人/Boss 生成控制
             无模块级副作用（所有初始化需显式调用 init_game）
=============================================================================
"""
import os
import sys
import math
import random
import pygame

from src.config import *
from src.core.resource_manager import load_image_scaled, load_sound, load_font
from src.core.game_state import GameState
from src.objects.background import Background
from src.objects.enemies import Enemy, ShootingEnemy, DyingEnemy
from src.objects.boss import Boss, DyingBoss
from src.objects.player import Player
from src.objects.skill import SkillSystem
from src.objects.common import Bullet, Reward, Animation
from src.menus.manager import MenuManager
from src.audio.sound_manager import SoundManager
from src.data_manager import reset_last_record

# ──────────────────────────────────────────────
# 全局单例（由 init_game 创建）
# ──────────────────────────────────────────────
state: GameState = None
screen: pygame.Surface = None
clock: pygame.time.Clock = None
background: Background = None

bullets: pygame.sprite.Group = None
enemies: pygame.sprite.Group = None
rewards: pygame.sprite.Group = None
enemy_bullets: pygame.sprite.Group = None
bosses: pygame.sprite.Group = None
explosions: list = None

player_instance: Player = None
skill_system: SkillSystem = None
sound_manager: SoundManager = None
menu_manager: MenuManager = None

boss_spawn_count: int = 0
last_player_x: float = 0
last_player_y: float = 0
last_shoot_time: int = 0
last_enemy_spawn_time: int = 0
enemy_spawn_rate: int = INITIAL_ENEMY_SPAWN_RATE
enemy_spawn_interval: int = ENEMY_SPAWN_INTERVAL

stats: dict = None


def init_game():
    """初始化游戏引擎：创建屏幕、玩家、音效、菜单等"""
    global state, screen, clock, background
    global bullets, enemies, rewards, enemy_bullets, bosses, explosions
    global player_instance, skill_system, sound_manager, menu_manager
    global boss_spawn_count, last_player_x, last_player_y
    global last_shoot_time, last_enemy_spawn_time
    global enemy_spawn_rate, enemy_spawn_interval, stats

    pygame.init()
    pygame.mixer.init()

    state = GameState()
    clock = pygame.time.Clock()
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),
                                     pygame.DOUBLEBUF | pygame.HWSURFACE)
    pygame.display.set_caption('SHOOT')

    # 图标
    try:
        icon = load_image_scaled('images', 'SHOOT.png', scale_factor=1.0)
        pygame.display.set_icon(icon)
    except (pygame.error, FileNotFoundError):
        pass

    background = Background()

    # 对象组
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    rewards = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    bosses = pygame.sprite.Group()
    explosions = []

    boss_spawn_count = 0

    # 玩家
    player_instance = Player(bullets)
    player_instance.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    skill_system = SkillSystem(player_instance, bullets, enemy_bullets, enemies, bosses)

    last_player_x = player_instance.rect.x
    last_player_y = player_instance.rect.y
    last_shoot_time = 0
    last_enemy_spawn_time = 0
    enemy_spawn_rate = INITIAL_ENEMY_SPAWN_RATE
    enemy_spawn_interval = ENEMY_SPAWN_INTERVAL

    # 音效
    sounds = _initialize_sounds()
    sound_manager = SoundManager(sounds)

    # 菜单
    menu_manager = MenuManager(screen, player_instance, sounds)

    # 统计数据
    stats = {
        'bullets_fired': 0,
        'enemies_killed': 0,
        'shooting_enemies_killed': 0,
        'enemies_collided': 0,
        'rewards_collected': 0,
        'health_lost': 0,
        'hp_upgrades': 0,
        'shoot_upgrades': 0,
        'speed_upgrades': 0,
    }


def _initialize_sounds():
    """加载所有音效并设置音量"""
    sound_paths = {
        'shoot_P': ('sounds', 'shoot_P.wav'),
        'shoot_E': ('sounds', 'shoot_E.wav'),
        'hit_E': ('sounds', 'hit_E.mp3'),
        'hit_P': ('sounds', 'hit_P.mp3'),
        'end': ('sounds', 'END.wav'),
        'button': ('sounds', 'button.mp3'),
        'error': ('sounds', 'error.wav'),
        'up': ('sounds', 'up.mp3'),
        'reward': ('sounds', 'reward.mp3'),
    }
    sounds = {}
    for key, parts in sound_paths.items():
        try:
            s = load_sound(*parts)
            s.set_volume(SOUND_VOLUMES.get(key, 0.1))
            sounds[key] = s
        except pygame.error as e:
            print(f"加载音效 {key} 失败: {e}")
    return sounds


# ──────────────────────────────────────────────
# 游戏逻辑函数
# ──────────────────────────────────────────────

def update_player_and_entities():
    """更新玩家和所有游戏实体的状态"""
    global last_player_x, last_player_y

    player_instance.update()
    bullets.update()
    enemy_bullets.update()

    for enemy in enemies.copy():
        if isinstance(enemy, DyingEnemy):
            if enemy.update():
                enemies.remove(enemy)
        else:
            enemy.update(enemies)

    for boss in bosses.copy():
        if isinstance(boss, DyingBoss):
            if boss.update():
                bosses.remove(boss)
        else:
            boss.update(enemies)

    rewards.update()

    now = pygame.time.get_ticks()
    skill_system.update(now)

    # 相机跟随
    dx = (player_instance.rect.x - last_player_x) * 0.8
    dy = (player_instance.rect.y - last_player_y) * 0.8
    background.update(player_instance.rect, dx, dy)
    last_player_x = player_instance.rect.x
    last_player_y = player_instance.rect.y


def draw_entities():
    """绘制所有游戏实体"""
    screen.fill((0, 0, 0))
    background.draw(screen)

    player_instance.draw_trail(screen)
    screen.blit(player_instance.image, player_instance.rect)

    for b in bullets:
        screen.blit(b.image, b.rect)
    for eb in enemy_bullets:
        screen.blit(eb.image, eb.rect)
    for e in enemies:
        screen.blit(e.image, e.rect)
    for b in bosses:
        screen.blit(b.image, b.rect)
        if b.shield_active and not b.shield_temp_deactivated and b.rail_active:
            _draw_rail(screen, b)
    for r in rewards:
        screen.blit(r.image, r.rect)

    for exp in explosions[:]:
        frame = exp.get_current_frame()
        if frame:
            screen.blit(frame, exp.rect.topleft)
        else:
            explosions.remove(exp)

    skill_system.draw_energy_bar(screen)


def _draw_rail(screen, boss):
    """绘制 Boss 判定滑轨"""
    rail_w, rail_h = 350, 12
    rail_x = SCREEN_WIDTH // 2 - rail_w // 2
    rail_y = SCREEN_HEIGHT - 80

    shake = 0
    if boss.rail_shake_active:
        now = pygame.time.get_ticks()
        progress = min(1.0, (now - boss.rail_shake_timer) / boss.rail_shake_duration)
        intensity = boss.rail_shake_intensity * (1 - progress)
        shake = int(intensity * math.sin(now * 0.1))

    rail_x += shake

    # 滑轨背景
    pygame.draw.rect(screen, (50, 50, 50), (rail_x, rail_y, rail_w, rail_h), border_radius=15)

    # 成功区域
    sz_w = int(rail_w * (boss.rail_success_range / 100))
    sz_x = rail_x + int(rail_w * (boss.rail_success_position / 100)) - sz_w // 2
    sz_x = max(rail_x, min(sz_x, rail_x + rail_w - sz_w))
    pygame.draw.rect(screen, (255, 50, 50), (sz_x, rail_y, sz_w, rail_h), border_radius=15)

    # 指示器
    ind_x = rail_x + int(rail_w * (boss.rail_position / 100))
    ind_x = max(rail_x + 12, min(ind_x, rail_x + rail_w - 12))
    pygame.draw.circle(screen, (255, 250, 100), (ind_x, rail_y + rail_h // 2), 8)

    # 边框
    pygame.draw.rect(screen, (200, 200, 200), (rail_x, rail_y, rail_w, rail_h), 2, border_radius=15)


def play_explosion_animation(x, y):
    """在 (x, y) 处创建爆炸动画"""
    anim = Animation('explosion.png', (4, 4), 50)
    anim.rect.center = (x, y)
    return anim


def spawn_enemies_and_rewards(current_time):
    """生成敌人和奖励"""
    global last_enemy_spawn_time, boss_spawn_count

    if current_time - last_enemy_spawn_time < enemy_spawn_interval:
        return

    total = 0
    # Boss 生成条件
    threshold = int(200 * (1.75 ** boss_spawn_count))
    killed = stats['enemies_killed'] + stats['shooting_enemies_killed']
    if killed >= threshold and len(bosses) == 0:
        bosses.add(Boss(player_instance, enemy_bullets, boss_spawn_count))
        boss_spawn_count += 1

    # 普通敌人（无 Boss 时）
    if len(bosses) == 0:
        for _ in range(enemy_spawn_rate):
            if total >= MAX_ENTITIES:
                break
            etype = random.choices(
                [Enemy, ShootingEnemy],
                weights=[NORMAL_ENEMY_WEIGHT, SHOOTING_ENEMY_WEIGHT], k=1
            )[0]
            enemy = etype(player_instance, enemy_bullets) if etype == ShootingEnemy else etype(player_instance)
            side = random.choice(['top', 'left', 'right'])
            if side == 'top':
                enemy.rect.x = random.randint(0, SCREEN_WIDTH - enemy.rect.width)
                enemy.rect.y = random.randint(-32, 0)
            elif side == 'left':
                enemy.rect.x = random.randint(-32, 0)
                enemy.rect.y = random.randint(0, SCREEN_HEIGHT - enemy.rect.height)
            else:
                enemy.rect.x = random.randint(SCREEN_WIDTH, SCREEN_WIDTH + 32)
                enemy.rect.y = random.randint(0, SCREEN_HEIGHT - enemy.rect.height)
            enemies.add(enemy)
            total += 1

    # 奖励
    while total < MAX_ENTITIES and random.random() < REWARD_SPAWN_CHANCE:
        r = Reward(player_instance)
        r.rect.x = random.randint(0, SCREEN_WIDTH - r.rect.width)
        r.rect.y = random.randint(0, SCREEN_HEIGHT - r.rect.height)
        rewards.add(r)
        total += 1

    last_enemy_spawn_time = current_time


def update_game_stats():
    """根据击败敌人数调整生成速度和数量"""
    global enemy_spawn_rate, enemy_spawn_interval

    defeated = stats['enemies_killed'] + stats['shooting_enemies_killed']
    if defeated <= 0:
        return

    speed_mult = min(defeated // 25, MAX_ENEMY_SPAWN_SPEED_MULTIPLIER)
    enemy_spawn_interval = max(
        int(ENEMY_SPAWN_INTERVAL * (ENEMY_SPAWN_INTERVAL_DECREASE ** speed_mult)),
        MIN_ENEMY_SPAWN_INTERVAL
    )

    rate_mult = min(defeated // 50, MAX_ENEMY_SPAWN_RATE_MULTIPLIER)
    enemy_spawn_rate = INITIAL_ENEMY_SPAWN_RATE + rate_mult


def check_shoot(current_time):
    """检查并处理玩家射击"""
    global last_shoot_time

    if (player_instance.score <= 0 or
            not pygame.mouse.get_pressed()[0] or
            current_time - last_shoot_time < PLAYER_SHOOT_COOLDOWN or
            player_instance.entrance_animation_active):
        return

    # 避免点击按钮时射击
    mouse_pos = pygame.mouse.get_pos()
    menu_buttons = [
        menu_manager.start_button, menu_manager.upgrade_button,
        menu_manager.leaderboard_button, menu_manager.settings_button,
        menu_manager.hp_button, menu_manager.shoot_button,
        menu_manager.sp_button, menu_manager.pause_button,
        menu_manager.level_screen.challenge_button,
        menu_manager.level_screen.return_button,
    ]
    if any(b and b.collidepoint(mouse_pos) for b in menu_buttons):
        return

    count = player_instance.shoot(mouse_pos)
    if count:
        player_instance.score -= count
        last_shoot_time = current_time
        sound_manager.play_sound('shoot_P')
        stats['bullets_fired'] += count


def check_collisions():
    """碰撞检测，返回 False 表示玩家死亡"""
    alive_enemies = pygame.sprite.Group(
        e for e in enemies if not getattr(e, 'is_dead', False)
    )
    alive_bosses = pygame.sprite.Group(
        b for b in bosses if not getattr(b, 'is_dead', False)
    )

    # 玩家子弹 → 敌人
    for bullet, hits in pygame.sprite.groupcollide(bullets, alive_enemies, True, False).items():
        for enemy in hits:
            if enemy.take_damage(1):
                sound_manager.play_sound('hit_E')
                explosions.append(play_explosion_animation(enemy.rect.centerx, enemy.rect.centery))
                enemies.remove(enemy)
                enemies.add(DyingEnemy(enemy))
                player_instance.score += 10
                key = 'shooting_enemies_killed' if isinstance(enemy, ShootingEnemy) else 'enemies_killed'
                stats[key] += 1
            else:
                sound_manager.play_sound('hit_E')

    # 玩家子弹 → Boss
    for bullet in bullets:
        for boss in alive_bosses:
            if pygame.sprite.collide_mask(bullet, boss):
                bullet.kill()
                if boss.shield_active and not boss.shield_temp_deactivated:
                    continue
                if boss.take_damage(10):
                    sound_manager.play_sound('hit_E')
                    explosions.append(play_explosion_animation(boss.rect.centerx, boss.rect.centery))
                    bosses.remove(boss)
                    bosses.add(DyingBoss(boss))
                    player_instance.score += 1000
                    stats['enemies_killed'] += 1
                else:
                    sound_manager.play_sound('hit_E')
                    explosions.append(play_explosion_animation(bullet.rect.centerx, bullet.rect.centery))
                break

    # 敌人子弹 → 玩家
    player_group = pygame.sprite.Group(player_instance)
    if pygame.sprite.groupcollide(enemy_bullets, player_group, True, True):
        if not player_instance.shield_active:
            player_instance.health -= 1
            sound_manager.play_sound('hit_E')
            explosions.append(play_explosion_animation(player_instance.rect.centerx, player_instance.rect.centery))
            stats['health_lost'] += 1
            if player_instance.health <= 0:
                return False

    # 玩家 → 敌人碰撞
    dead_players = False
    for enemy in list(alive_enemies):
        if player_instance.collision_rect.colliderect(enemy.collision_rect):
            if player_instance.shield_active:
                continue
            sound_manager.play_sound('hit_E')
            explosions.append(play_explosion_animation(enemy.rect.centerx, enemy.rect.centery))
            hl = random.randint(2, 5)
            player_instance.health -= hl
            stats['health_lost'] += hl
            if not state.player_explosion:
                sound_manager.play_sound('hit_P')
                state.player_explosion = True
                explosions.append(play_explosion_animation(player_instance.rect.centerx, player_instance.rect.centery))
                stats['enemies_collided'] += 1
            enemy.kill()
            if player_instance.health <= 0:
                dead_players = True
                break
    if dead_players:
        return False

    # 玩家 → 奖励
    for reward in list(rewards):
        if getattr(reward, 'is_special', False):
            now = pygame.time.get_ticks()
            if hasattr(reward, 'creation_time') and hasattr(reward, 'invincible_duration'):
                if now - reward.creation_time < reward.invincible_duration:
                    continue
            continue
        if player_instance.collision_rect.colliderect(reward.collision_rect):
            explosions.append(play_explosion_animation(reward.rect.centerx, reward.rect.centery))
            skill_system.add_energy()
            player_instance.score += reward.score_value
            reward.explode()
            reward.kill()
            stats['rewards_collected'] += 1

    # 玩家子弹 → 特殊奖励
    for bullet in bullets:
        for reward in list(rewards):
            if getattr(reward, 'is_special', False):
                now = pygame.time.get_ticks()
                if hasattr(reward, 'creation_time') and hasattr(reward, 'invincible_duration'):
                    if now - reward.creation_time < reward.invincible_duration:
                        continue
                if bullet.rect.colliderect(reward.collision_rect):
                    bullet.kill()
                    reward.kill()
                    player_instance.score += reward.score_value
                    sound_manager.play_sound('reward')
                    explosions.append(play_explosion_animation(reward.rect.centerx, reward.rect.centery))
                    reward.explode()
                    stats['rewards_collected'] += 1

    # 玩家 → Boss 碰撞
    for boss in alive_bosses:
        if player_instance.collision_rect.colliderect(boss.collision_rect):
            if player_instance.shield_active:
                continue
            sound_manager.play_sound('hit_E')
            if not state.player_explosion:
                sound_manager.play_sound('hit_P')
                state.player_explosion = True
            player_instance.health -= 20
            stats['health_lost'] += 20
            if player_instance.health <= 0:
                return False

    return True


def render_gameplay_hud():
    """渲染游戏 HUD（分数 + 生命值）"""
    font = load_font('fonts', 'pixel_script.ttf', size=30)
    score_color = (255, 0, 0) if player_instance.score <= 10 else (255, 255, 255)
    health_display = max(0, player_instance.health)
    health_color = (255, 0, 0) if player_instance.health < 20 else (255, 255, 255)

    screen.blit(font.render(f'积分值: {player_instance.score}', True, score_color), (10, 10))
    screen.blit(font.render(f'生命值: {health_display}', True, health_color), (10, 50))


def reset_game():
    """重置游戏状态（重新开始）"""
    global boss_spawn_count, last_enemy_spawn_time, last_shoot_time, explosions
    global enemy_spawn_rate, enemy_spawn_interval

    player_instance.reset()
    enemies.empty()
    enemy_bullets.empty()
    bullets.empty()
    rewards.empty()
    bosses.empty()

    boss_spawn_count = 0
    explosions.clear()
    last_enemy_spawn_time = pygame.time.get_ticks()
    last_shoot_time = 0

    if menu_manager:
        menu_manager.reset_upgrade_scores()

    for k in stats:
        stats[k] = 0

    skill_system.energy = 0
    skill_system.is_q_skill_active = False
    skill_system.is_e_skill_active = False
    skill_system.last_q_skill_time = 0
    skill_system.last_e_skill_time = 0

    state.guide_image = None
    state.guide_image_loaded = False
    state.guide_start_time = 0
    state.enemies_can_spawn = False
    state.END_sound_played = False
    state.player_explosion = False

    reset_last_record()
