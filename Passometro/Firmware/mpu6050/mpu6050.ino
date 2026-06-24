/**
 * ============================================================
 *  Serial BMS — ESP32 DevKit V1 + USBConverter + BMS
 *  Baud Rate: ??? 
 * ============================================================
 *  PINAGEM:
 *    RX   → GPIO 16
 *    TX → GPIO 17
 * ============================================================
 */

#define RX2_PIN       16    // GPIO_16
#define TX2_PIN       17    // GPIO_17
                            // obs: Lembrar que a conexão é TX_conv -> RX_esp | RX_conv -> TX_esp
#define BMS_BAUD_RATE 250000  // Necessário testar 9600, 19200, 38400, 57600, 115200 (Apenas trocar o valor no define BMS_BAUD_RATE)
                            // Não sabemos qual o baud rate da serial do BMS
#define MSG_MAX_LEN   512   // Caso apareça "[WARN] Buffer overflow", aumentar para 1024 ou para o necessário

String  buffer        = "";
uint32_t frameCount   = 0;

void setup() {
  Serial.begin(115200);
  Serial2.begin(BMS_BAUD_RATE, SERIAL_8N1, RX2_PIN, TX2_PIN);
}

void loop() {
  while (Serial2.available() > 0) {
    char c = (char)Serial2.read();

    if (c == '\n') {
      buffer.trim();

      if (buffer.length() > 0) {
        frameCount++;
        Serial.print("┌─ Mensagem #");
        Serial.print(frameCount);
        Serial.print("  |  raw: ");
        Serial.println(buffer);
        Serial.println("│");

        parsearCSV(buffer);

        Serial.println("└────────────────────────────────────────────\n");
        buffer = "";
      }

    } else {
      if (buffer.length() < MSG_MAX_LEN) {
        buffer += c;
      } else {
        Serial.println("[WARN] Buffer overflow — linha descartada.");
        buffer = "";
      }
    }
  }
}

void parsearCSV(String linha) {
  uint8_t  indiceCampo = 0;
  String   campo       = "";

  linha += ",";

  for (uint16_t i = 0; i < linha.length(); i++) {
    char c = linha.charAt(i);

    if (c == ',') {
      campo.trim();

      Serial.print("│  [");
      // Padding do índice para alinhar a saída
      if (indiceCampo < 10) Serial.print("0");
      Serial.print(indiceCampo);
      Serial.print("]  valor: \"");
      Serial.print(campo);
      Serial.print("\"");

      // Preenche espaços para alinhar a coluna de tipo
      int padding = 20 - campo.length();
      for (int p = 0; p < padding; p++) Serial.print(" ");

      Serial.print("  tipo: ");
      Serial.println(inferirTipo(campo));

      indiceCampo++;
      campo = "";
    } else {
      campo += c;
    }
  }

  Serial.print("│\n│  Total de campos: ");
  Serial.println(indiceCampo);
}

String inferirTipo(String valor) {
  if (valor.length() == 0) return "VAZIO";

  bool temDígito  = false;
  bool temPonto   = false;
  bool temLetra   = false;
  bool temMinus   = false;

  for (uint8_t i = 0; i < valor.length(); i++) {
    char c = valor.charAt(i);
    if (isDigit(c))               temDígito = true;
    else if (c == '.')            temPonto  = true;
    else if (c == '-' && i == 0)  temMinus  = true;
    else if (isAlpha(c))          temLetra  = true;
  }

  if (temLetra  && !temDígito)           return "STRING";
  if (temLetra  &&  temDígito)           return "ALFANUM";
  if (temDígito && !temPonto)            return "INT    ";
  if (temDígito &&  temPonto)            return "FLOAT  ";

  return "DESCONHECIDO";
}