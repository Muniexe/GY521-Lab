#include <Wire.h>

const int MPU = 0x68;

void setup() {

  Wire.begin();
  Serial.begin(115200);

  // Desperta o MPU6050
  Wire.beginTransmission(MPU);
  Wire.write(0x6B);
  Wire.write(0x00);
  Wire.endTransmission(true);

  // Configura DLPF (42 Hz)
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
}

void loop() {

  int16_t AcX, AcY, AcZ;
  int16_t GyX, GyY, GyZ;

  Wire.beginTransmission(MPU);
  Wire.write(0x3B);
  Wire.endTransmission(false);

  Wire.requestFrom(MPU, 14, true);

  AcX = Wire.read() << 8 | Wire.read();
  AcY = Wire.read() << 8 | Wire.read();
  AcZ = Wire.read() << 8 | Wire.read();

  // Ignora temperatura
  Wire.read();
  Wire.read();

  GyX = Wire.read() << 8 | Wire.read();
  GyY = Wire.read() << 8 | Wire.read();
  GyZ = Wire.read() << 8 | Wire.read();

  // Converte para unidades físicas

  float ax = AcX / 16384.0;
  float ay = AcY / 16384.0;
  float az = AcZ / 16384.0;

  float gx = GyX / 131.0;
  float gy = GyY / 131.0;
  float gz = GyZ / 131.0;

  unsigned long tempo = millis();

  Serial.print(ax, 4);
  Serial.print(",");

  Serial.print(ay, 4);
  Serial.print(",");

  Serial.print(az, 4);
  Serial.print(",");

  Serial.print(gx, 4);
  Serial.print(",");

  Serial.print(gy, 4);
  Serial.print(",");

  Serial.print(gz, 4);
  Serial.print(",");

  Serial.println(tempo);

  delay(10); // ~100 Hz
}