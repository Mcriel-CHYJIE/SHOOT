# SHOOT — 移动版

Python Pygame 空间射击游戏的 Android 移植版。

## 操作方式

| 控制 | 操作 |
|------|------|
| **移动** | 左侧虚拟摇杆（拖拽） |
| **瞄准** | 右侧虚拟摇杆（拖拽） |
| **射击** | 右摇杆拖拽时自动射击 |
| **技能 Q** | 屏幕下方 "Q" 按钮 |
| **技能 E** | 屏幕下方 "E" 按钮 |
| **暂停** | 右上角 "暂停" 按钮 |
| **升级** | 右上角 "升级" 按钮 |

## 构建 APK

### 方法一：GitHub Actions（推荐，无需本地环境）

1. 将本项目推送到 GitHub 仓库
2. 进入仓库 Actions 页面
3. 手动触发 `Build SHOOT APK` workflow
4. 构建完成后下载 APK 产物

### 方法二：本地 WSL2 构建（Windows）

```bash
# 在 WSL2 Ubuntu 中
sudo apt install -y git zip unzip python3-pip openjdk-17-jdk autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
pip install --user buildozer cython
cd /path/to/SHOOT_Mobile
buildozer android debug
# APK 生成在 bin/ 目录
```

### 方法三：直接运行（电脑上测试）

```bash
pip install pygame-ce
python main.py
```

## 与原版的区别

- 添加双摇杆触摸控制（`src/mobile_input.py`）
- 自动缩放适配屏幕（`main.py`）
- Android 数据存储路径适配（`src/data_manager.py`）
- 使用 `pygame-ce` 社区版（更好的移动端兼容性）

## 技术栈

- Python 3.11
- pygame-ce ≥ 2.5.0
- buildozer（APK 打包）
- python-for-android（Android 适配）
