import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

import serial
import math
import csv

# ==========================
# CONFIG
# ==========================

PORTA = "COM4"
BAUD = 115200

ALPHA_ACCEL = 0.90
COMPLEMENTARY = 0.98

GYRO_DEADBAND = 0.5

# ==========================
# SERIAL
# ==========================

arduino = serial.Serial(PORTA, BAUD)

# ==========================
# CSV
# ==========================

csv_file = open("dados.csv", "w", newline="")

csv_writer = csv.writer(csv_file)

csv_writer.writerow([
    "tempo_ms",
    "ax",
    "ay",
    "az",
    "gx",
    "gy",
    "gz",
    "pitch",
    "roll",
    "yaw",
    "magnitude"
])

# ==========================
# CALIBRAÇÃO
# ==========================

print("Mantenha o sensor parado...")
print("Calibrando giroscópio...")

gx_offset = 0
gy_offset = 0
gz_offset = 0

samples = 300

for i in range(samples):

    linha = arduino.readline().decode().strip()

    try:
        valores = linha.split(',')

        if len(valores) != 7:
            continue

        ax, ay, az, gx, gy, gz, tempo = map(float, valores)

        gx_offset += gx
        gy_offset += gy
        gz_offset += gz

    except:
        pass

gx_offset /= samples
gy_offset /= samples
gz_offset /= samples

print("Calibração concluída.")
print("Offsets:")
print(gx_offset, gy_offset, gz_offset)

# ==========================
# CUBO
# ==========================

vertices = (
    (1, -1, -1),
    (1,  1, -1),
    (-1, 1, -1),
    (-1,-1, -1),
    (1, -1,  1),
    (1,  1,  1),
    (-1,-1,  1),
    (-1, 1,  1)
)

faces = (
    (0,1,2,3),
    (3,2,7,6),
    (6,7,5,4),
    (4,5,1,0),
    (1,5,7,2),
    (4,0,3,6)
)

cores = (
    (1,0,0),
    (0,1,0),
    (0,0,1),
    (1,1,0),
    (1,0,1),
    (0,1,1)
)

def desenhar_cubo():

    glBegin(GL_QUADS)

    for i, face in enumerate(faces):

        glColor3fv(cores[i])

        for vertex in face:
            glVertex3fv(vertices[vertex])

    glEnd()

# ==========================
# OPENGL
# ==========================

pygame.init()

display = (1000, 700)

pygame.display.set_mode(
    display,
    DOUBLEBUF | OPENGL
)

gluPerspective(
    45,
    display[0] / display[1],
    0.1,
    50.0
)

glEnable(GL_DEPTH_TEST)

glTranslatef(0, 0, -8)

# ==========================
# FILTROS
# ==========================

ax_f = 0
ay_f = 0
az_f = 1

pitch = 0
roll = 0
yaw = 0

tempo_anterior = None

# ==========================
# LOOP
# ==========================

while True:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    try:

        linha = arduino.readline().decode().strip()

        valores = linha.split(',')

        if len(valores) != 7:
            continue

        ax, ay, az, gx, gy, gz, tempo_ms = map(float, valores)

        # ------------------
        # dt real
        # ------------------

        if tempo_anterior is None:

            tempo_anterior = tempo_ms
            continue

        dt = (tempo_ms - tempo_anterior) / 1000.0
        tempo_anterior = tempo_ms

        if dt <= 0:
            continue

        # ------------------
        # Remove offsets
        # ------------------

        gx -= gx_offset
        gy -= gy_offset
        gz -= gz_offset

        # ------------------
        # Deadband
        # ------------------

        if abs(gx) < GYRO_DEADBAND:
            gx = 0

        if abs(gy) < GYRO_DEADBAND:
            gy = 0

        if abs(gz) < GYRO_DEADBAND:
            gz = 0

        # ------------------
        # Low-pass
        # ------------------

        ax_f = ALPHA_ACCEL * ax_f + (1 - ALPHA_ACCEL) * ax
        ay_f = ALPHA_ACCEL * ay_f + (1 - ALPHA_ACCEL) * ay
        az_f = ALPHA_ACCEL * az_f + (1 - ALPHA_ACCEL) * az

        # ------------------
        # Ângulos acelerômetro
        # ------------------

        pitch_acc = math.degrees(
            math.atan2(
                ay_f,
                math.sqrt(ax_f*ax_f + az_f*az_f)
            )
        )

        roll_acc = math.degrees(
            math.atan2(
                -ax_f,
                az_f
            )
        )

        # ------------------
        # Integra giroscópio
        # ------------------

        pitch_gyro = pitch + gx * dt
        roll_gyro = roll + gy * dt

        # ------------------
        # Filtro complementar
        # ------------------

        pitch = (
            COMPLEMENTARY * pitch_gyro +
            (1 - COMPLEMENTARY) * pitch_acc
        )

        roll = (
            COMPLEMENTARY * roll_gyro +
            (1 - COMPLEMENTARY) * roll_acc
        )

        # ------------------
        # Yaw suavizado
        # ------------------

        yaw += gz * dt * 0.5
        
        magnitude = math.sqrt(
            ax * ax +
            ay * ay	+
            az * az
            )
        
        csv_writer.writerow([
            tempo_ms,
            ax,
            ay,
            az,
            gx,
            gy,
            gz,
            pitch,
            roll,
            yaw,
            magnitude])
        csv_file.flush()
            
        
        

    except:
        pass

    # ======================
    # RENDER
    # ======================

    glClear(
        GL_COLOR_BUFFER_BIT |
        GL_DEPTH_BUFFER_BIT
    )

    glPushMatrix()

    glRotatef(pitch, 1, 0, 0)
    glRotatef(yaw,   0, 1, 0)
    glRotatef(roll,  0, 0, 1)

    desenhar_cubo()

    glPopMatrix()

    pygame.display.flip()

    pygame.time.wait(5)