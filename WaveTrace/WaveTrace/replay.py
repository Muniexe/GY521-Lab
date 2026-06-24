import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import threading
import time

from cube import desenhar_cubo

# ==========================
# Configuração da janela 3D
# ==========================

DISPLAY = (1000, 700)
FOV     = 45
Z_NEAR  = 0.1
Z_FAR   = 50.0
Z_CAM   = -6.0


def _configurar_opengl():
    """Configura perspectiva e estado inicial do OpenGL."""

    # Matriz de projeção (câmera / perspectiva)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOV, DISPLAY[0] / DISPLAY[1], Z_NEAR, Z_FAR)

    # Volta para a matriz de modelo/visão
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1.0)   # fundo cinza escuro


def _loop_replay(df):
    """Loop principal do pygame/OpenGL (roda em thread separada)."""

    pygame.init()
    pygame.display.set_caption("WaveTrace – Replay 3D")
    pygame.display.set_mode(DISPLAY, DOUBLEBUF | OPENGL)

    _configurar_opengl()

    clock = pygame.time.Clock()

    for i in range(len(df)):

        # Verifica se o usuário fechou a janela
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        pitch = df.iloc[i]["pitch"]
        roll  = df.iloc[i]["roll"]
        yaw   = df.iloc[i]["yaw"]

        # Limpa buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Reposiciona a câmera a cada frame
        glLoadIdentity()
        glTranslatef(0.0, 0.0, Z_CAM)

        # Aplica a orientação do sensor
        glRotatef(pitch, 1, 0, 0)
        glRotatef(yaw,   0, 1, 0)
        glRotatef(roll,  0, 0, 1)

        desenhar_cubo()

        pygame.display.flip()

        # Respeita o tempo real entre amostras
        if i > 0:
            dt_ms = df.iloc[i]["tempo_ms"] - df.iloc[i - 1]["tempo_ms"]
            dt_s  = max(1, dt_ms) / 1000.0
            time.sleep(dt_s)
        else:
            clock.tick(60)

    pygame.quit()


def iniciar_replay(df):
    """
    Inicia o replay 3D em uma thread separada para não travar o tkinter.
    Retorna imediatamente; a janela pygame roda de forma independente.
    """
    if df is None:
        return

    t = threading.Thread(target=_loop_replay, args=(df,), daemon=True)
    t.start()
