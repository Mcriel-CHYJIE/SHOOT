"""
=============================================================================
 配置常量模块 — 游戏参数配置
=============================================================================
 所属功能块: 核心引擎
 功能描述  : 定义游戏窗口、玩家、敌人、Boss、升级、生成、音效等全部可调参数
=============================================================================
"""
# ============================================================
# 屏幕设置
# ============================================================
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800

# ============================================================
# 玩家设置
# ============================================================
PLAYER_HEALTH = 100                    # 初始生命值
PLAYER_MAX_HEALTH = 100                # 最大生命值
PLAYER_INITIAL_SCORE = 20              # 初始分数
PLAYER_BULLET_SPEED = 10               # 子弹速度
PLAYER_BULLET_RANGE = 666              # 子弹射程
PLAYER_MAX_SPEED = 5                   # 最大移动速度
PLAYER_DECELERATION_RATE = 0.15        # 减速速率
PLAYER_ROTATION_SPEED = 8              # 旋转速度
PLAYER_SHOOT_COOLDOWN = 100            # 射击冷却（毫秒）

# ============================================================
# 敌人设置
# ============================================================
ENEMY_SPEED = 1.8                      # 普通敌人速度
SHOOTING_ENEMY_SPEED = 1.2            # 射击型敌人速度
SHOOTING_ENEMY_SHOOT_INTERVAL = 1500   # 射击间隔（毫秒）

# ============================================================
# Boss 设置
# ============================================================
BOSS_BASE_HEALTH = 1000
BOSS_HEALTH_PER_SPAWN = 500
BOSS_BASE_SHOOT_INTERVAL = 1500
BOSS_SHOOT_INTERVAL_DECREASE = 100
BOSS_MIN_SHOOT_INTERVAL = 500
BOSS_BASE_SPEED = 1.5
BOSS_SPEED_PER_SPAWN = 0.1
BOSS_MAX_SPEED = 3.2
BOSS_BASE_ROTATION_SPEED = 2.0
BOSS_ROTATION_SPEED_PER_SPAWN = 0.1
BOSS_MAX_ROTATION_SPEED = 4.0
BOSS_ENTER_SPEED = 2.0
BOSS_RAIL_DURATION = 10000             # 判定滑轨持续时间（毫秒）
BOSS_RAIL_SPEED = 0.75                 # 判定区域移动速度
BOSS_RAIL_SUCCESS_SPEED = 0.5          # 判定成功区域移动速度
BOSS_RAIL_SHAKE_DURATION = 500         # 抖动持续时间（毫秒）
BOSS_RAIL_SHAKE_INTENSITY = 5          # 抖动强度（像素）

# ============================================================
# 升级分数设置
# ============================================================
INITIAL_HP_SCORE = 648
INITIAL_SHOOT_SCORE = 1180
INITIAL_SP_SCORE = 450
SCORE_MULTIPLIER = 11 / 10

# ============================================================
# 敌人生成设置
# ============================================================
MAX_ENTITIES = 99
ENEMY_SPAWN_INTERVAL = 1999
INITIAL_ENEMY_SPAWN_RATE = 2
ENEMY_SPAWN_SPEED_THRESHOLD = 200
ENEMY_SPAWN_RATE_THRESHOLD = 400
MAX_ENEMY_SPAWN_SPEED_MULTIPLIER = 10
MAX_ENEMY_SPAWN_RATE_MULTIPLIER = 10
MIN_ENEMY_SPAWN_INTERVAL = 100
ENEMY_SPAWN_INTERVAL_DECREASE = 0.95

# ============================================================
# 奖励设置
# ============================================================
REWARD_SPAWN_CHANCE = 0.15

# ============================================================
# 敌人行为权重
# ============================================================
SHOOTING_ENEMY_WEIGHT = 2
NORMAL_ENEMY_WEIGHT = 8

# ============================================================
# 性能设置
# ============================================================
FPS = 60

# ============================================================
# 音效音量
# ============================================================
SOUND_VOLUMES = {
    'shoot_P': 0.1,
    'shoot_E': 0.015,
    'hit_E': 0.1,
    'hit_P': 0.1,
    'end': 0.2,
    'button': 0.05,
    'error': 0.1,
    'up': 0.1,
    'reward': 0.1,
}
BGM_VOLUME = 0.05

# ============================================================
# 字体大小
# ============================================================
FONT_SIZES = {
    'game_name': 20,
    'instruction': 30,
    'tip': 20,
    'score': 30,
    'upgrade_title': 36,
    'upgrade_description': 24,
    'pause_tip': 18,
    'version': 10,
    'enemy_count': 24,
    'reward_info': 20,
    'upgrade_effect': 28,
}

# ============================================================
# 颜色
# ============================================================
COLORS = {
    'white': (225, 225, 205),
    'black': (0, 0, 0),
    'red': (255, 50, 50),
    'yellow': (255, 250, 100),
    'pink': (200, 150, 100),
}
