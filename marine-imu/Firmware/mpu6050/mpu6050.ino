#include <Wire.h>
#include <SPI.h>
#include <SD.h>

const int MPU = 0x68;
const int SD_CS = 5;   // Pino CS do módulo SD

File arquivo;

void setup() {

  Serial.begin(115200);

  // I2C do ESP32
  Wire.begin(21, 22);
  Wire.setClock(400000);

  // Inicializa MPU6050
  Wire.beginTransmission(MPU);
  Wire.write(0x6B);
  Wire.write(0x00);
  Wire.endTransmission(true);

  // DLPF = 42 Hz
  Wire.beginTransmission(MPU);
  Wire.write(0x1A);
  Wire.write(0x03);
  Wire.endTransmission(true);

  // Giroscópio ±250 °/s
  Wire.beginTransmission(MPU);
  Wire.write(0x1B);
  Wire.write(0x00);
  Wire.endTransmission(true);

  // Acelerômetro ±2g
  Wire.beginTransmission(MPU);
  Wire.write(0x1C);
  Wire.write(0x00);
  Wire.endTransmission(true);

  delay(1000);

  // Inicializa SD
  if (!SD.begin(SD_CS)) {
    Serial.println("Falha ao inicializar SD!");
    while (1);
  }

  Serial.println("SD inicializado!");

  // Cria arquivo e cabeçalho
  if (!SD.exists("/dados.csv")) {

    File cabecalho = SD.open("/dados.csv", FILE_WRITE);

    if (cabecalho) {
      cabecalho.println("ax,ay,az,gx,gy,gz,tempo_ms");
      cabecalho.close();
      Serial.println("Arquivo criado.");
    }
  }

  // Abre arquivo para gravação contínua
  arquivo = SD.open("/dados.csv", FILE_APPEND);

  if (!arquivo) {
    Serial.println("Erro ao abrir arquivo!");
    while (1);
  }
}

void loop() {

  int16_t AcX, AcY, AcZ;
  int16_t GyX, GyY, GyZ;

  Wire.beginTransmission(MPU);
  Wire.write(0x3B);
  Wire.endTransmission(false);

  Wire.requestFrom(MPU, 14, true);

  if (Wire.available() < 14) {
    return;
  }

  AcX = Wire.read() << 8 | Wire.read();
  AcY = Wire.read() << 8 | Wire.read();
  AcZ = Wire.read() << 8 | Wire.read();

  // Ignora temperatura
  Wire.read();
  Wire.read();

  GyX = Wire.read() << 8 | Wire.read();
  GyY = Wire.read() << 8 | Wire.read();
  GyZ = Wire.read() << 8 | Wire.read();

  float ax = AcX / 16384.0;
  float ay = AcY / 16384.0;
  float az = AcZ / 16384.0;

  float gx = GyX / 131.0;
  float gy = GyY / 131.0;
  float gz = GyZ / 131.0;

  unsigned long tempo = millis();

  String linha =
      String(ax, 4) + "," +
      String(ay, 4) + "," +
      String(az, 4) + "," +
      String(gx, 4) + "," +
      String(gy, 4) + "," +
      String(gz, 4) + "," +
      String(tempo);

  // Salva no SD
  arquivo.println(linha);

  // Mostra na Serial
  Serial.println(linha);

  // Garante que os dados sejam gravados no cartão
  static int contador = 0;
  contador++;

  if (contador >= 100) {
    arquivo.flush();
    contador = 0;
  }

  delay(10);
}