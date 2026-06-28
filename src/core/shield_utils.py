"""
=============================================================================
 护盾绘制工具 — 护盾轮廓效果
=============================================================================
 所属功能块: 工具库
 功能描述  : 提取 Player、Boss、DyingBoss 中重复的护盾发光轮廓绘制逻辑
=============================================================================
"""
import pygame


def create_shield_surface(original_image, outline_color_outer, outline_color_inner,
                          flash_alpha=255, padding=6):
    """
    为原始图像创建带护盾轮廓效果的新表面
    在原始图像周围绘制多层渐变轮廓，形成护盾发光效果

    Args:
        original_image: 原始图像表面
        outline_color_outer: 外层轮廓颜色 (r, g, b)
        outline_color_inner: 内层轮廓颜色 (r, g, b)
        flash_alpha: 外层轮廓透明度 (0-255)
        padding: 护盾与原始图像的间距

    Returns:
        pygame.Surface: 带护盾效果的图像表面
    """
    shield_surface = pygame.Surface(
        (original_image.get_width() + padding * 2,
         original_image.get_height() + padding * 2),
        pygame.SRCALPHA
    )

    # 获取原始图像的边缘轮廓
    original_mask = pygame.mask.from_surface(original_image)
    outline_mask = original_mask.outline()

    if outline_mask:
        # 外层轮廓（较宽，透明度较低）
        for offset in range(4, 8):
            offset_outline = [
                (x + offset + padding // 2, y + offset + padding // 2)
                for x, y in outline_mask
            ]
            pygame.draw.lines(
                shield_surface,
                (*outline_color_outer, flash_alpha // 2),
                True, offset_outline, 3
            )

        # 内层轮廓（较窄，透明度较高）
        for offset in range(2, 4):
            offset_outline = [
                (x + offset + padding // 2, y + offset + padding // 2)
                for x, y in outline_mask
            ]
            pygame.draw.lines(
                shield_surface,
                (*outline_color_inner, int(flash_alpha * 0.7)),
                True, offset_outline, 2
            )

    # 将原始图像绘制到护盾内部
    shield_surface.blit(original_image, (padding, padding))
    return shield_surface


def calculate_shield_flash(timer, base_alpha=150, range_alpha=105):
    """
    计算护盾闪烁透明度
    使用正弦波产生流畅的闪烁效果

    Args:
        timer: 当前闪烁计时值
        base_alpha: 基础透明度
        range_alpha: 透明度变化范围

    Returns:
        int: 当前帧的透明度值
    """
    import math
    return base_alpha + int(range_alpha * abs(math.sin(timer * 0.3)))
