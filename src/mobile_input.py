"""
=============================================================================
 移动输入模块 — 双摇杆触摸控制
=============================================================================
 所属功能块: 工具库
 功能描述  : 左侧摇杆控制移动，右侧摇杆控制瞄准/射击
=============================================================================
"""
import math
import pygame

# ── 布局常量 ──────────────────────────────────────────────
JOYSTICK_RADIUS = 60
KNOB_RADIUS = 25
JOYSTICK_MARGIN = 90
ALPHA = 120

SKILL_RADIUS = 30
BTN_SIZE = (110, 40)


class TouchControls:
    """双摇杆触摸控制器"""

    def __init__(self, screen_w, screen_h):
        self.sw = screen_w
        self.sh = screen_h

        # ── 左侧摇杆（移动） ────────────────────────────
        self.lx = JOYSTICK_MARGIN + JOYSTICK_RADIUS
        self.ly = self.sh - JOYSTICK_MARGIN - JOYSTICK_RADIUS
        self.l_dx = 0.0
        self.l_dy = 0.0
        self.l_touch = None

        # ── 右侧摇杆（瞄准+射击） ─────────────────────
        self.rx = self.sw - JOYSTICK_MARGIN - JOYSTICK_RADIUS
        self.ry = self.sh - JOYSTICK_MARGIN - JOYSTICK_RADIUS
        self.r_dx = 0.0
        self.r_dy = 0.0
        self.r_touch = None

        # 右摇杆抬起时作为自瞄准参考点
        self.aim_x = self.sw // 2
        self.aim_y = self.sh // 2

        # ── 技能按钮（左右摇杆中间偏上） ──────────────
        cx = self.sw // 2
        self.q_center = (cx - 90, self.sh - JOYSTICK_MARGIN - 20)
        self.e_center = (cx + 90, self.sh - JOYSTICK_MARGIN - 20)
        self.q_pressed = False
        self.e_pressed = False

        # ── 菜单按钮（右上角） ─────────────────────────
        self.pause_rect = pygame.Rect(self.sw - 130, 10, BTN_SIZE[0], BTN_SIZE[1])
        self.upgrade_rect = pygame.Rect(self.sw - 130, 55, BTN_SIZE[0], BTN_SIZE[1])

        # 手指跟踪
        self.fingers = {}

    def handle_event(self, event):
        """处理触摸事件，返回需注入的事件列表"""
        if event.type == pygame.FINGERDOWN:
            tx = event.x * self.sw
            ty = event.y * self.sh
            fid = event.finger_id

            # ── 左摇杆 ──
            if math.hypot(tx - self.lx, ty - self.ly) < JOYSTICK_RADIUS * 2.0:
                self.l_touch = fid
                self.fingers[fid] = 'left'
                self._update_joystick(tx, ty, 'left')
                return []

            # ── 右摇杆 ──
            if math.hypot(tx - self.rx, ty - self.ry) < JOYSTICK_RADIUS * 2.0:
                self.r_touch = fid
                self.fingers[fid] = 'right'
                self._update_joystick(tx, ty, 'right')
                return []

            # ── Q 技能 ──
            if math.hypot(tx - self.q_center[0], ty - self.q_center[1]) < SKILL_RADIUS * 1.5:
                self.q_pressed = True
                self.fingers[fid] = 'q'
                return [pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_q})]

            # ── E 技能 ──
            if math.hypot(tx - self.e_center[0], ty - self.e_center[1]) < SKILL_RADIUS * 1.5:
                self.e_pressed = True
                self.fingers[fid] = 'e'
                return [pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_e})]

            # ── 暂停/升级按钮 ──
            if self.pause_rect.collidepoint(tx, ty):
                self.fingers[fid] = 'pause'
                return [pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                           {'pos': (int(tx), int(ty)), 'button': 1})]
            if self.upgrade_rect.collidepoint(tx, ty):
                self.fingers[fid] = 'upgrade'
                return [pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                           {'pos': (int(tx), int(ty)), 'button': 1})]

            # ── 屏幕其他区域 → 右摇杆触发（快速瞄准该点） ──
            # 设置右摇杆方向指向触摸点
            dx = tx - self.rx
            dy = ty - self.ry
            dist = math.hypot(dx, dy)
            if dist > 10:
                self.r_dx = dx / JOYSTICK_RADIUS
                self.r_dy = dy / JOYSTICK_RADIUS
            self.fingers[fid] = 'aim'
            return []

        elif event.type == pygame.FINGERUP:
            fid = event.finger_id
            if fid == self.l_touch:
                self.l_touch = None
                self.l_dx = 0.0
                self.l_dy = 0.0
            if fid == self.r_touch:
                self.r_touch = None
                self.r_dx = 0.0
                self.r_dy = 0.0
            self.fingers.pop(fid, None)
            return []

        elif event.type == pygame.FINGERMOTION:
            tx = event.x * self.sw
            ty = event.y * self.sh
            fid = event.finger_id

            role = self.fingers.get(fid)
            if role == 'left':
                self._update_joystick(tx, ty, 'left')
            elif role in ('right', 'aim'):
                self._update_joystick(tx, ty, 'right')
            return []

        return None

    def _update_joystick(self, tx, ty, side):
        max_r = JOYSTICK_RADIUS
        if side == 'left':
            dx = tx - self.lx
            dy = ty - self.ly
        else:
            dx = tx - self.rx
            dy = ty - self.ry
        dist = math.hypot(dx, dy)
        if dist > max_r:
            dx = dx / dist * max_r
            dy = dy / dist * max_r
        if side == 'left':
            self.l_dx = dx / max_r
            self.l_dy = dy / max_r
        else:
            self.r_dx = dx / max_r
            self.r_dy = dy / max_r

    def get_movement(self):
        """返回 (dx, dy) 范围 -1~1，左侧摇杆"""
        return self.l_dx, self.l_dy

    def get_aim(self):
        """返回瞄准方向 (dx, dy)，右侧摇杆"""
        return self.r_dx, self.r_dy

    def is_shooting(self):
        """右摇杆有动作时视为射击"""
        return abs(self.r_dx) > 0.15 or abs(self.r_dy) > 0.15

    def get_aim_screen_pos(self):
        """返回游戏画面中的瞄准位置"""
        cx, cy = self.sw // 2, self.sh // 2
        return (int(cx + self.r_dx * 300), int(cy + self.r_dy * 300))

    def draw(self, surface):
        """绘制双摇杆 + 技能 + 菜单按钮"""
        # ── 左摇杆 ──
        self._draw_joystick(surface, self.lx, self.ly, self.l_dx, self.l_dy,
                            (255, 255, 255))

        # ── 右摇杆 ──
        self._draw_joystick(surface, self.rx, self.ry, self.r_dx, self.r_dy,
                            (255, 180, 100))

        # ── Q 技能 ──
        qcol = (255, 220, 100, 200) if self.q_pressed else (255, 220, 100, ALPHA)
        pygame.draw.circle(surface, qcol, self.q_center, SKILL_RADIUS, 3)
        self._draw_text(surface, "Q", self.q_center[0], self.q_center[1], 20)

        # ── E 技能 ──
        ecol = (100, 255, 100, 200) if self.e_pressed else (100, 255, 100, ALPHA)
        pygame.draw.circle(surface, ecol, self.e_center, SKILL_RADIUS, 3)
        self._draw_text(surface, "E", self.e_center[0], self.e_center[1], 20)

        # ── 暂停/升级 ──
        for rect, txt in ((self.pause_rect, "暂停"), (self.upgrade_rect, "升级")):
            s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            s.fill((150, 150, 150, 150))
            surface.blit(s, rect.topleft)
            self._draw_text(surface, txt, rect.x + rect.w // 2, rect.y + rect.h // 2, 18)

    def _draw_joystick(self, surface, cx, cy, dx, dy, color):
        # 外圈
        s = pygame.Surface((JOYSTICK_RADIUS * 2, JOYSTICK_RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color, ALPHA), (JOYSTICK_RADIUS, JOYSTICK_RADIUS),
                           JOYSTICK_RADIUS, 3)
        surface.blit(s, (cx - JOYSTICK_RADIUS, cy - JOYSTICK_RADIUS))
        # 内圈
        kx = cx + dx * JOYSTICK_RADIUS
        ky = cy + dy * JOYSTICK_RADIUS
        pygame.draw.circle(surface, (*color, 180), (int(kx), int(ky)), KNOB_RADIUS)

    def _draw_text(self, surface, text, x, y, size):
        try:
            font = pygame.font.Font(None, size)
            img = font.render(text, True, (255, 255, 255, 200))
            surface.blit(img, (x - img.get_width() // 2, y - img.get_height() // 2))
        except:
            pass
