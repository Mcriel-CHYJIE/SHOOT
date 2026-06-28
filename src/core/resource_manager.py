"""
=============================================================================
 资源管理器 — 统一资源加载
=============================================================================
 所属功能块: 工具库
 功能描述  : 集中管理图片、音效、字体等资源的加载与缓存
=============================================================================
"""
import os
import sys
import pygame

# 缓存已加载的资源，避免重复加载
_image_cache = {}
_sound_cache = {}
_font_cache = {}


def get_base_path():
    """
    获取资源基础路径（兼容 PyInstaller 打包）
    所有模块统一使用此函数，避免重复计算
    """
    return getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def get_asset_path(*parts):
    """获取资源文件完整路径"""
    return os.path.join(get_base_path(), 'assets', *parts)


def load_image(*parts, cache=True):
    """
    加载图片资源
    Args:
        parts: 路径组成部分，如 ('images', 'airship', '4.png')
        cache: 是否缓存（默认 True）
    Returns:
        pygame.Surface: 加载的图片表面
    """
    path = get_asset_path(*parts)
    if cache and path in _image_cache:
        return _image_cache[path].copy()

    try:
        image = pygame.image.load(path).convert_alpha()
        if cache:
            _image_cache[path] = image.copy()
        return image
    except pygame.error as e:
        print(f"无法加载图片: {path} - {e}")
        raise


def load_sound(*parts, cache=True):
    """
    加载音效资源
    Args:
        parts: 路径组成部分，如 ('sounds', 'shoot_P.wav')
        cache: 是否缓存（默认 True）
    Returns:
        pygame.mixer.Sound: 音效对象
    """
    path = get_asset_path(*parts)
    if cache and path in _sound_cache:
        return _sound_cache[path]

    try:
        sound = pygame.mixer.Sound(path)
        if cache:
            _sound_cache[path] = sound
        return sound
    except pygame.error as e:
        print(f"无法加载音效: {path} - {e}")
        raise


def load_font(*parts, size):
    """
    加载字体资源
    Args:
        parts: 路径组成部分，如 ('fonts', 'pixel_script.ttf')
        size: 字体大小
    Returns:
        pygame.font.Font: 字体对象
    """
    cache_key = (parts, size)
    if cache_key in _font_cache:
        return _font_cache[cache_key]

    path = get_asset_path(*parts)
    try:
        font = pygame.font.Font(path, size)
        _font_cache[cache_key] = font
        return font
    except pygame.error:
        # 回退到系统字体
        font = pygame.font.SysFont(None, size)
        _font_cache[cache_key] = font
        return font


def load_image_scaled(*parts, scale_factor=1.0, size=None, cache=True):
    """
    加载并按比例缩放图片
    Args:
        parts: 路径组成部分
        scale_factor: 缩放倍数
        size: 目标尺寸 (width, height)，优先于 scale_factor
        cache: 是否缓存
    Returns:
        pygame.Surface: 缩放后的图片
    """
    image = load_image(*parts, cache=cache)
    if size:
        return pygame.transform.scale(image, size)
    if scale_factor != 1.0:
        new_size = (int(image.get_width() * scale_factor), int(image.get_height() * scale_factor))
        return pygame.transform.scale(image, new_size)
    return image


def clear_cache():
    """清理所有资源缓存（游戏重启时调用）"""
    _image_cache.clear()
    _sound_cache.clear()
    _font_cache.clear()
