import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import threading
import time

from cube import desenhar_cubo

# ==========================
# Configuração
# ==========================

DISPLAY      = (1000, 780)
FOV          = 45
Z_NEAR       = 0.1
Z_FAR        = 50.0
Z_CAM        = -6.0

# Timeline
TL_X         = 40
TL_Y         = 720
TL_W         = 920
TL_H         = 16
TL_RADIUS    = 8

# Cores (R, G, B)
COR_BG_UI    = (20,  20,  30)
COR_TL_TRACK = (60,  60,  80)
COR_TL_FILL  = (80, 140, 255)
COR_TL_THUMB = (255, 255, 255)
COR_TEXT     = (220, 220, 220)
COR_BTN      = (50,  50,  70)
COR_BTN_HOV  = (80,  80, 110)
COR_BTN_ACT  = (80, 140, 255)
COR_STOP     = (200,  60,  60)
COR_STOP_HOV = (240,  80,  80)

SPEEDS       = [0.25, 0.5, 1.0, 2.0, 4.0]
SPEED_LABELS = ["0.25x", "0.5x", "1x", "2x", "4x"]

# ==========================
# Helpers de desenho 2D
# ==========================

def _rect(surf, cor, x, y, w, h, radius=6):
    pygame.draw.rect(surf, cor, (x, y, w, h), border_radius=radius)

def _circle(surf, cor, cx, cy, r):
    pygame.draw.circle(surf, cor, (cx, cy), r)

def _text(surf, font, msg, cor, cx, cy):
    s = font.render(msg, True, cor)
    r = s.get_rect(center=(cx, cy))
    surf.blit(s, r)

def _fmt_time(ms):
    s   = int(ms / 1000)
    dec = int((ms % 1000) / 100)
    m   = s // 60
    s   = s % 60
    return f"{m:02d}:{s:02d}.{dec}"

# ==========================
# Configurar OpenGL
# ==========================

def _configurar_opengl():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOV, DISPLAY[0] / DISPLAY[1], Z_NEAR, Z_FAR)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.08, 0.08, 0.12, 1.0)

# ==========================
# Renderizar frame 3D
# ==========================

def _render_frame(pitch, roll, yaw):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, Z_CAM)
    glRotatef(pitch, 1, 0, 0)
    glRotatef(yaw,   0, 1, 0)
    glRotatef(roll,  0, 0, 1)
    desenhar_cubo()

# ==========================
# Desenhar UI (2D overlay)
# ==========================

def _draw_ui(surf, font_sm, font_md, font_lg,
             idx, total, tempo_ms, tempo_total_ms,
             playing, speed_idx, btn_rects, dragging):

    # Fundo da faixa de controles
    ui_rect = pygame.Rect(0, DISPLAY[1] - 140, DISPLAY[0], 140)
    pygame.draw.rect(surf, COR_BG_UI, ui_rect)

    # ── Timeline track ──
    progress = idx / max(total - 1, 1)
    fill_w   = int(TL_W * progress)
    thumb_x  = TL_X + fill_w

    _rect(surf, COR_TL_TRACK, TL_X, TL_Y, TL_W, TL_H, 8)
    if fill_w > 0:
        _rect(surf, COR_TL_FILL, TL_X, TL_Y, fill_w, TL_H, 8)
    _circle(surf, COR_TL_THUMB, thumb_x, TL_Y + TL_H // 2, TL_RADIUS)

    # ── Tempo ──
    t_cur   = _fmt_time(tempo_ms)
    t_total = _fmt_time(tempo_total_ms)
    _text(surf, font_sm, f"{t_cur}  /  {t_total}", COR_TEXT,
          DISPLAY[0] // 2, TL_Y - 16)

    # ── Botões ──
    mx, my = pygame.mouse.get_pos()

    for key, rect in btn_rects.items():
        hov = rect.collidepoint(mx, my)

        if key == "stop":
            cor = COR_STOP_HOV if hov else COR_STOP
            _rect(surf, cor, rect.x, rect.y, rect.w, rect.h)
            _text(surf, font_md, "■", COR_TEXT, rect.centerx, rect.centery)

        elif key == "playpause":
            cor = COR_BTN_HOV if hov else COR_BTN
            _rect(surf, cor, rect.x, rect.y, rect.w, rect.h)
            label = "▐▐" if playing else "▶"
            _text(surf, font_lg, label, COR_TEXT, rect.centerx, rect.centery)

        elif key.startswith("spd_"):
            si     = int(key.split("_")[1])
            active = (si == speed_idx)
            cor    = COR_BTN_ACT if active else (COR_BTN_HOV if hov else COR_BTN)
            _rect(surf, cor, rect.x, rect.y, rect.w, rect.h)
            _text(surf, font_sm, SPEED_LABELS[si], COR_TEXT,
                  rect.centerx, rect.centery)

    # Label velocidade
    _text(surf, font_sm, "Velocidade:", COR_TEXT, 530, 758)

# ==========================
# Loop principal
# ==========================

def _loop_replay(df):
    pygame.init()
    pygame.display.set_caption("WaveTrace - Replay 3D")
    screen = pygame.display.set_mode(DISPLAY, DOUBLEBUF | OPENGL)
    _configurar_opengl()

    ui_surf = pygame.Surface(DISPLAY, pygame.SRCALPHA)

    font_sm = pygame.font.SysFont("segoeui", 15)
    font_md = pygame.font.SysFont("segoeui", 20, bold=True)
    font_lg = pygame.font.SysFont("segoeui", 26, bold=True)

    total          = len(df)
    tempo_total_ms = df.iloc[-1]["tempo_ms"] - df.iloc[0]["tempo_ms"]
    tempo_base_ms  = df.iloc[0]["tempo_ms"]

    idx       = 0
    playing   = True
    speed_idx = 2       # 1x por padrao
    dragging  = False
    acc_ms    = 0.0
    last_tick = time.perf_counter()

    btn_rects = {
        "stop":      pygame.Rect(360, 743, 54, 34),
        "playpause": pygame.Rect(430, 738, 64, 42),
        "spd_0":     pygame.Rect(610, 745, 54, 28),
        "spd_1":     pygame.Rect(672, 745, 54, 28),
        "spd_2":     pygame.Rect(734, 745, 54, 28),
        "spd_3":     pygame.Rect(796, 745, 54, 28),
        "spd_4":     pygame.Rect(858, 745, 54, 28),
    }

    clock = pygame.time.Clock()

    while True:
        dt_real   = time.perf_counter() - last_tick
        last_tick = time.perf_counter()

        # ── Eventos ──
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return

            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                tl_rect = pygame.Rect(TL_X - TL_RADIUS, TL_Y - TL_RADIUS,
                                      TL_W + TL_RADIUS * 2, TL_H + TL_RADIUS * 2)

                if tl_rect.collidepoint(mx, my):
                    dragging = True
                    frac = max(0.0, min(1.0, (mx - TL_X) / TL_W))
                    idx  = int(frac * (total - 1))
                    acc_ms = 0.0

                elif btn_rects["playpause"].collidepoint(mx, my):
                    playing = not playing
                    acc_ms  = 0.0

                elif btn_rects["stop"].collidepoint(mx, my):
                    idx     = 0
                    playing = False
                    acc_ms  = 0.0

                else:
                    for si in range(len(SPEEDS)):
                        if btn_rects[f"spd_{si}"].collidepoint(mx, my):
                            speed_idx = si

            elif event.type == MOUSEBUTTONUP and event.button == 1:
                dragging = False

            elif event.type == MOUSEMOTION and dragging:
                mx   = event.pos[0]
                frac = max(0.0, min(1.0, (mx - TL_X) / TL_W))
                idx  = int(frac * (total - 1))
                acc_ms = 0.0

            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    playing = not playing
                elif event.key == K_LEFT:
                    idx    = max(0, idx - 10)
                    acc_ms = 0.0
                elif event.key == K_RIGHT:
                    idx    = min(total - 1, idx + 10)
                    acc_ms = 0.0

        # ── Avança índice ──
        if playing and not dragging and idx < total - 1:
            acc_ms += dt_real * 1000.0 * SPEEDS[speed_idx]

            while acc_ms > 0 and idx < total - 1:
                dt_sample = (df.iloc[idx + 1]["tempo_ms"] -
                             df.iloc[idx]["tempo_ms"])
                if acc_ms >= dt_sample:
                    acc_ms -= dt_sample
                    idx += 1
                else:
                    break

            if idx >= total - 1:
                playing = False

        # ── Render 3D ──
        pitch = df.iloc[idx]["pitch"]
        roll  = df.iloc[idx]["roll"]
        yaw   = df.iloc[idx]["yaw"]
        _render_frame(pitch, roll, yaw)

        # ── Overlay 2D ──
        ui_surf.fill((0, 0, 0, 0))
        tempo_ms_atual = df.iloc[idx]["tempo_ms"] - tempo_base_ms
        _draw_ui(ui_surf, font_sm, font_md, font_lg,
                 idx, total, tempo_ms_atual, tempo_total_ms,
                 playing, speed_idx, btn_rects, dragging)

        raw = pygame.image.tostring(ui_surf, "RGBA", True)
        glWindowPos2d(0, 0)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDrawPixels(DISPLAY[0], DISPLAY[1], GL_RGBA, GL_UNSIGNED_BYTE, raw)
        glDisable(GL_BLEND)

        pygame.display.flip()
        clock.tick(60)

# ==========================
# API pública
# ==========================

def iniciar_replay(df):
    """Abre a janela de replay 3D em thread separada."""
    if df is None:
        return
    t = threading.Thread(target=_loop_replay, args=(df,), daemon=True)
    t.start()
