[app]

# 应用名称
title = SHOOT
package.name = shoot
package.domain = org.shootgame

# 版本
source.dir = .
source.include_exts = py,png,jpg,jpeg,gif,svg,wav,mp3,ogg,ttf,json,txt
source.exclude_exts = spec
source.exclude_dirs = tests, bin, .git, __pycache__
source.exclude_patterns = buildozer.spec

# 构建需求
requirements = python3, pygame-ce

# 权限
android.permissions = VIBRATE

# Android 特有
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a
android.entrypoint = main.py
android.wakelock = True
android.fullscreen = 1
android.portrait = 0
android.allow_back = True

# 图标（可选，默认使用 pygame 图标）
# android.icon = assets/images/SHOOT.png

# 预设方向
orientation = landscape

# 应用元数据
osx.package_name = SHOOT
osx.bundle_identifier = org.shootgame.shoot
