from OpenGL.GL import *

# ==========================
# Geometria do cubo
# ==========================

VERTICES = (
    ( 1, -1, -1),
    ( 1,  1, -1),
    (-1,  1, -1),
    (-1, -1, -1),
    ( 1, -1,  1),
    ( 1,  1,  1),
    (-1, -1,  1),
    (-1,  1,  1),
)

FACES = (
    (0, 1, 2, 3),
    (3, 2, 7, 6),
    (6, 7, 5, 4),
    (4, 5, 1, 0),
    (1, 5, 7, 2),
    (4, 0, 3, 6),
)

# Uma cor diferente para cada face (R, G, B)
CORES = (
    (1.0, 0.2, 0.2),   # vermelho
    (0.2, 1.0, 0.2),   # verde
    (0.2, 0.2, 1.0),   # azul
    (1.0, 1.0, 0.2),   # amarelo
    (1.0, 0.5, 0.0),   # laranja
    (0.8, 0.2, 1.0),   # roxo
)

# Arestas para o wireframe
ARESTAS = (
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 7), (7, 6), (6, 4),
    (0, 4), (1, 5), (2, 7), (3, 6),
)


def desenhar_cubo():
    """Desenha o cubo com faces coloridas e arestas pretas."""

    # Faces coloridas
    glBegin(GL_QUADS)
    for i, face in enumerate(FACES):
        glColor3fv(CORES[i])
        for vertex in face:
            glVertex3fv(VERTICES[vertex])
    glEnd()

    # Arestas em branco para dar contorno
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_LINES)
    for aresta in ARESTAS:
        for vertex in aresta:
            glVertex3fv(VERTICES[vertex])
    glEnd()
