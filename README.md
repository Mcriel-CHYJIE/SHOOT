<p align="center">
  <img src="assets/images/SHOOT.png" alt="SHOOT" width="128"/>
</p>

<h1 align="center">SHOOT</h1>

<p align="center">
  <em>太空射击游戏 — Pygame 2D 卷轴射击</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/pygame-2.5.0%2B-brightgreen" alt="pygame">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey" alt="Platform">
</p>

---

## 📋 概述

SHOOT 是一款基于 Pygame 开发的 2D 太空射击游戏。玩家操控飞船在星空中移动，通过鼠标瞄准射击敌人，积累积分强化自身属性，挑战不断升级的敌人和强大的 Boss。

- **玩法**：击败敌人 → 获取积分 → 升级属性 → 挑战 Boss
- **特色**：技能系统、Boss 判定滑轨、动态难度、多层视差星空
- **运行**：桌面原生运行

---

## 🚀 快速开始

### 环境要求

- Python >= 3.10
- pygame >= 2.5.0

### 安装与运行

```bash
# 克隆项目
git clone https://github.com/your/project.git
cd shoot

# 安装依赖
pip install pygame

# 启动游戏
python main.py

# 或
python -m src
```

> **提示**：Windows 用户请确保使用英文输入法，否则 WASD 控制可能无响应。

---

## 🎮 操作方式

| 操作 | 按键 | 说明 |
|------|------|------|
| **移动** | `W` `A` `S` `D` / 方向键 | 八方向移动，带惯性减速 |
| **瞄准** | 鼠标 | 屏幕内任意位置 |
| **射击** | 鼠标左键 | 消耗 1 积分/发，可升级散射 |
| **Q 技能** | `Q` | 满能量时释放，散射 10 个特殊奖励 |
| **E 技能** | `E` | 满能量时释放，护盾 + 弹道翻倍 + 回血 25 |
| **Boss 判定** | `空格` | 滑轨判定成功则解除 Boss 护盾 5 秒 |
| **暂停** | 点击「暂停游戏」按钮 | 暂停后可在菜单操作 |
| **升级** | 点击「升级」按钮 | 打开属性升级面板 |

---

## ✨ 核心机制

### 🧬 积分与升级

初始积分 20，击败普通敌人 +10，Boss +1000。

消耗积分可提升三项属性，每次升级后成本按 ×1.1 递增：

| 属性 | 初始成本 | 效果 |
|------|---------|------|
| **HP** | 648 | 最大生命值 +50 |
| **射击** | 1180 | 子弹散射 +1 发 |
| **SP** | 450 | 移动速度提升 |

### ⚡ 技能系统

收集奖励可积累能量条（上限 9 格）。满能量后可释放技能：

- **Q 技能**：散射 10 个特殊奖励，碰撞或射击后爆炸产生追踪弹
- **E 技能**：激活护盾（免疫伤害）+ 散射弹道 +2 + 立即回血 25

### 👾 敌人与 Boss

- **普通敌人**：追踪、躲避、侧移三种 AI 行为随机切换
- **射击型敌人**：保持最佳距离绕行射击
- **Boss**：多种移动/射击模式，具有突进攻击和保护罩
  - **判定滑轨**：Boss 出场后激活，按空格在滑块对准绿色区域时判定成功
  - **动态难度**：Boss 随出现次数增强（血量 +500，射速加快，移动更快）

### 📈 动态难度

游戏难度随击败敌人数自动调整：

| 击败敌人 | 效果 |
|---------|------|
| 每 25 个 | 生成间隔 -5%（最快 100ms）|
| 每 50 个 | 每次生成数量 +1（最多 +10）|
| 200/350/... | Boss 出现（×1.75 递增）|

---

## 📁 项目结构

```
shoot/
├── main.py                      # 游戏入口
├── pyproject.toml               # 项目元数据与构建配置
│
├── assets/                      # 静态资源
│   ├── fonts/
│   │   └── pixel_script.ttf     # 像素风格字体
│   ├── images/                  # 精灵图与图标
│   │   ├── airship/             # 飞船素材（玩家/敌人/Boss）
│   │   ├── Bullet/              # 子弹精灵图
│   │   ├── SHOOT.png            # 游戏图标
│   │   ├── dm.png               # 引导角色
│   │   ├── reward.png           # 普通奖励
│   │   ├── specialreward.png    # 特殊奖励
│   │   └── explosion.png        # 爆炸动画精灵图
│   └── sounds/                  # 音效文件
│
├── docs/
│   └── README.md                # 文档（被 pyproject.toml 引用）
│
└── src/                         # Python 源码包
    ├── __init__.py
    ├── __main__.py              # python -m 入口
    │
    ├── config.py                # 游戏常量配置
    ├── data_manager.py          # 数据持久化（排行榜）
    ├── engine.py                # 核心引擎（初始化/碰撞/生成）
    ├── game.py                  # 主循环（事件/渲染调度）
    │
    ├── core/                    # 工具库
    │   ├── resource_manager.py  # 统一资源加载与缓存
    │   ├── game_state.py        # 全局状态封装
    │   ├── shield_utils.py      # 护盾轮廓绘制
    │   └── art.py               # ASCII 艺术字
    │
    ├── objects/                 # 游戏实体
    │   ├── player.py            # 玩家飞船
    │   ├── enemies.py           # 敌人 AI（含 DyingEnemy）
    │   ├── boss.py              # Boss 机制（含 DyingBoss）
    │   ├── common.py            # 子弹/追踪弹/奖励/动画
    │   ├── skill.py             # 技能系统 & 特殊奖励
    │   └── background.py        # 三层视差星空背景
    │
    ├── audio/
    │   └── sound_manager.py     # 音效播放管理
    │
    └── menus/                   # 界面系统
        ├── manager.py           # 菜单调度器
        ├── start.py             # 开始界面
        ├── level.py             # 关卡选择
        ├── upgrade.py           # 属性升级
        ├── pause.py             # 暂停菜单
        ├── leaderboard.py       # 排行榜
        ├── settings.py          # 设置
        └── gameover.py          # 游戏结束
```

---

## 🛠️ 开发说明

### 依赖管理

项目使用 `pyproject.toml` 声明依赖（[PEP 621](https://peps.python.org/pep-0621/)）：

```bash
pip install pygame
```

### 项目架构

```
用户输入 → game.py（事件处理）
              ↓
         engine.py（游戏逻辑：更新/碰撞/生成）
              ↓
         objects/*（实体状态更新）
              ↓
         menus/* / engine.draw_entities（渲染输出）
```

- `engine.py` 无模块级副作用，需显式调用 `init_game()` 初始化
- `config.py` 仅含常量，无执行代码
- `game_state.py` 封装全局状态，替代散落的全局变量

---

## 📄 许可

MIT License © 2024

---

<p align="center">
  <sub>Built with <a href="https://www.pygame.org/">Pygame</a> · 太空见 ☄️</sub>
</p>
