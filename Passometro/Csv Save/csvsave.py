"""
Lê os dados enviados pelo passometro (Arduino) via serial e salva em CSV
com as colunas: tempo_ms, ax, ay, az, gx, gy, gz, pitch, roll, yaw, magnitude
 
Uso simples (usa a porta e o arquivo definidos abaixo):
    python serial_to_csv.py
 
Uso avançado (sobrescreve os valores padrão):
    python serial_to_csv.py COM3 dados.csv
 
Requisitos:
    pip install pyserial
"""
import sys
import csv
import time
import serial
 
# ---------------- CONFIGURAÇÕES (edite aqui) ----------------
PORTA = "COM3"          # Windows: "COM3", "COM4"...  |  Linux/Mac: "/dev/ttyUSB0", "/dev/cu.usbserial-XXXX"
ARQUIVO_SAIDA = "dados.csv"
BAUD = 115200
# --------------------------------------------------------------
 
COLUNAS = ["tempo_ms", "ax", "ay", "az", "gx", "gy", "gz", "pitch", "roll", "yaw", "magnitude"]
 
 
def main():
    # Se passar argumentos na linha de comando, eles sobrescrevem os valores fixos acima
    porta = sys.argv[1] if len(sys.argv) > 1 else PORTA
    arquivo_saida = sys.argv[2] if len(sys.argv) > 2 else ARQUIVO_SAIDA
    baud = BAUD
 
    print(f"Conectando em {porta} @ {baud} baud...")
    ser = serial.Serial(porta, baud, timeout=2)
    time.sleep(2)  # espera o Arduino resetar após abrir a porta
 
    ser.reset_input_buffer()
 
    with open(arquivo_saida, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(COLUNAS)
        f.flush()
 
        print(f"Gravando em {arquivo_saida}. Pressione Ctrl+C para parar.")
        linhas_gravadas = 0
 
        try:
            while True:
                linha = ser.readline().decode("utf-8", errors="ignore").strip()
 
                if not linha:
                    continue
 
                # Ignora o cabeçalho enviado pelo próprio Arduino
                if linha.lower().startswith("tempo_ms"):
                    continue
 
                valores = linha.split(",")
 
                if len(valores) != len(COLUNAS):
                    # Linha corrompida/incompleta - ignora
                    continue
 
                try:
                    # tempo_ms vem como inteiro (millis()), o resto como float
                    tempo_ms = int(float(valores[0]))
                    resto = [float(v) for v in valores[1:]]
                except ValueError:
                    continue
 
                writer.writerow([tempo_ms] + resto)
                linhas_gravadas += 1
 
                if linhas_gravadas % 50 == 0:
                    f.flush()
                    print(f"{linhas_gravadas} linhas gravadas...", end="\r")
 
        except KeyboardInterrupt:
            print(f"\nFinalizado. {linhas_gravadas} linhas gravadas em {arquivo_saida}.")
        finally:
            ser.close()
 
 
if __name__ == "__main__":
    main()