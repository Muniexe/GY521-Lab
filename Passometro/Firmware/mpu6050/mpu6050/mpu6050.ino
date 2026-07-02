#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <math.h>

LiquidCrystal_I2C lcd(0x27, 24, 2);   // Se não funcionar, troque para 0x27

const int MPU = 0x68;

// ---------------- Escalas do MPU6050 ----------------
// Acelerômetro em ±2g  -> divisor 16384.0 (LSB/g)
// Giroscópio em ±250°/s -> divisor 131.0 (LSB/(°/s))
const float ACCEL_SCALE = 16384.0;
const float GYRO_SCALE  = 131.0;

// ---------------- Filtro complementar ----------------
// Alpha alto = confia mais no giroscópio (resposta rápida, mas deriva);
// Alpha baixo = confia mais no acelerômetro (estável, mas sensível a vibração).
const float ALPHA = 0.96;

float pitch = 0, roll = 0, yaw = 0;
float gyroBiasX = 0, gyroBiasY = 0, gyroBiasZ = 0;

unsigned long tempoAnterior = 0;

// ---------------- Contador de passos ----------------
int passos = 0;
bool acimaLimiar = false;
unsigned long ultimoPasso = 0;

const float LIMIAR_SUBIDA  = 1.15;   // cruza pra cima -> candidato a passo
const float LIMIAR_DESCIDA = 1.05;   // precisa cruzar pra baixo antes de contar outro
const unsigned long INTERVALO_MIN_PASSO = 300; // ms, evita contar passos "fantasma"

// Filtro passa-baixa (média móvel exponencial) pra suavizar ruído da magnitude
const float ALPHA_MAG = 0.3;
float magnitudeFiltrada = 1.0;

// ---------------- Timing do loop (60 FPS) ----------------
const unsigned long INTERVALO_LOOP_US = 16667UL; // 1000000/60 ~= 16667 us
unsigned long tempoLoopAnterior = 0;

// ---------------- Throttle do LCD ----------------
// Escrever no LCD todo loop é lento (I2C) e derruba o FPS do envio serial.
// Atualiza o display só a cada N loops (~10 Hz é mais que suficiente pra leitura humana).
const int LCD_A_CADA_N_LOOPS = 6;
int contadorLoopsLCD = 0;

void calibrarGiroscopio() {
  lcd.setCursor(0,0);
  lcd.print("Calibrando giro ");
  lcd.setCursor(0,1);
  lcd.print("Fique parado... ");

  const int N = 200;
  long somaX = 0, somaY = 0, somaZ = 0;

  for (int i = 0; i < N; i++) {
    Wire.beginTransmission(MPU);
    Wire.write(0x43); // registrador inicial do giroscópio
    Wire.endTransmission(false);
    Wire.requestFrom(MPU, 6, true);

    if (Wire.available() == 6) {
      int16_t gx = Wire.read() << 8 | Wire.read();
      int16_t gy = Wire.read() << 8 | Wire.read();
      int16_t gz = Wire.read() << 8 | Wire.read();
      somaX += gx;
      somaY += gy;
      somaZ += gz;
    }
    delay(5);
  }

  gyroBiasX = (somaX / (float)N) / GYRO_SCALE;
  gyroBiasY = (somaY / (float)N) / GYRO_SCALE;
  gyroBiasZ = (somaZ / (float)N) / GYRO_SCALE;
}

void setup() {

  Serial.begin(115200);

  Wire.begin();

  lcd.init();
  lcd.backlight();

  lcd.setCursor(0,0);
  lcd.print("Inicializando...");
  lcd.setCursor(0,1);
  lcd.print("MPU6050");

  // Liga o MPU6050
  Wire.beginTransmission(MPU);
  Wire.write(0x6B);
  Wire.write(0);
  Wire.endTransmission(true);

  delay(100);

  lcd.clear();
  calibrarGiroscopio();
  lcd.clear();

  tempoAnterior = millis();
  tempoLoopAnterior = micros();

  // Cabeçalho do CSV - exatamente as colunas usadas pelo programa de gráficos
  Serial.println("tempo_ms,ax,ay,az,gx,gy,gz,pitch,roll,yaw,magnitude");
}

void loop() {

  int16_t AcX, AcY, AcZ, GyX, GyY, GyZ;

  // ---- Leitura do acelerômetro (0x3B a 0x40) ----
  Wire.beginTransmission(MPU);
  Wire.write(0x3B);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU, 6, true);

  if (Wire.available() < 6) return;

  AcX = Wire.read() << 8 | Wire.read();
  AcY = Wire.read() << 8 | Wire.read();
  AcZ = Wire.read() << 8 | Wire.read();

  // ---- Leitura do giroscópio (0x43 a 0x48) ----
  Wire.beginTransmission(MPU);
  Wire.write(0x43);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU, 6, true);

  if (Wire.available() < 6) return;

  GyX = Wire.read() << 8 | Wire.read();
  GyY = Wire.read() << 8 | Wire.read();
  GyZ = Wire.read() << 8 | Wire.read();

  float ax = AcX / ACCEL_SCALE;
  float ay = AcY / ACCEL_SCALE;
  float az = AcZ / ACCEL_SCALE;

  float gx = (GyX / GYRO_SCALE) - gyroBiasX;
  float gy = (GyY / GYRO_SCALE) - gyroBiasY;
  float gz = (GyZ / GYRO_SCALE) - gyroBiasZ;

  float magnitude = sqrt(ax * ax + ay * ay + az * az);

  // ---- dt real entre leituras ----
  unsigned long agora = millis();
  float dt = (agora - tempoAnterior) / 1000.0;
  tempoAnterior = agora;

  // ---- Ângulos a partir do acelerômetro (só funciona bem em repouso/baixa vibração) ----
  float pitchAcc = atan2(-ax, sqrt(ay * ay + az * az)) * 180.0 / PI;
  float rollAcc  = atan2(ay, az) * 180.0 / PI;

  // ---- Filtro complementar: combina giroscópio (rápido) com acelerômetro (estável) ----
  pitch = ALPHA * (pitch + gx * dt) + (1 - ALPHA) * pitchAcc;
  roll  = ALPHA * (roll  + gy * dt) + (1 - ALPHA) * rollAcc;

  // Yaw não tem referência absoluta sem magnetômetro: é só a integração do giro
  // (vai "derivar" com o tempo, é uma limitação física do MPU6050, não do código)
  yaw += gz * dt;

  // ---- Filtro passa-baixa na magnitude, pra detecção de passos mais estável ----
  magnitudeFiltrada = ALPHA_MAG * magnitude + (1 - ALPHA_MAG) * magnitudeFiltrada;

  // ---- Detecção de passos com histerese ----
  if (magnitudeFiltrada > LIMIAR_SUBIDA && !acimaLimiar) {
    if (agora - ultimoPasso > INTERVALO_MIN_PASSO) {
      passos++;
      ultimoPasso = agora;
    }
    acimaLimiar = true;
  }

  if (magnitudeFiltrada < LIMIAR_DESCIDA) {
    acimaLimiar = false;
  }

  // ---- LCD (atualizado só a cada N loops pra não roubar tempo do loop de 60 FPS) ----
  contadorLoopsLCD++;
  if (contadorLoopsLCD >= LCD_A_CADA_N_LOOPS) {
    contadorLoopsLCD = 0;

    lcd.setCursor(0,0);
    lcd.print("Passos:");
    lcd.print(passos);
    lcd.print("      ");

    lcd.setCursor(0,1);
    lcd.print("Acc:");
    lcd.print(magnitude,2);
    lcd.print("g     ");
  }

  // ---- Envia CSV para o computador ----
  Serial.print(agora);         Serial.print(",");
  Serial.print(ax,4);          Serial.print(",");
  Serial.print(ay,4);          Serial.print(",");
  Serial.print(az,4);          Serial.print(",");
  Serial.print(gx,4);          Serial.print(",");
  Serial.print(gy,4);          Serial.print(",");
  Serial.print(gz,4);          Serial.print(",");
  Serial.print(pitch,4);       Serial.print(",");
  Serial.print(roll,4);        Serial.print(",");
  Serial.print(yaw,4);         Serial.print(",");
  Serial.println(magnitude,4);

  // ---- Trava o loop em 60 FPS (~16.667 ms), compensando o tempo já gasto acima ----
  unsigned long tempoGastoUs = micros() - tempoLoopAnterior;
  if (tempoGastoUs < INTERVALO_LOOP_US) {
    delayMicroseconds(INTERVALO_LOOP_US - tempoGastoUs);
  }
  tempoLoopAnterior = micros();
}

