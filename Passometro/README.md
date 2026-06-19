# Marine IMU

Sistema de monitoramento de orientação para embarcações utilizando MPU6050 e ESP32.

## Objetivo

Este projeto foi desenvolvido para medir e registrar a orientação de uma embarcação em tempo real através de uma IMU MPU6050.

O sistema realiza a leitura do acelerômetro e giroscópio, armazena os dados em um cartão SD e permite sua análise posterior através de ferramentas de visualização e replay.

Os principais objetivos são:

- Medição de Roll (inclinação lateral)
- Medição de Pitch (inclinação longitudinal)
- Estimativa de Yaw
- Monitoramento de trim da embarcação
- Estudos de estabilidade
- Registro de movimento durante navegação
- Desenvolvimento de instrumentação náutica de baixo custo

---

## Hardware

### Componentes

- ESP32
- MPU6050 (GY-521)
- Módulo MicroSD
- Cartão MicroSD
- Computador para análise dos dados

### Ligações

#### MPU6050

| MPU6050 | ESP32 |
|----------|----------|
| VCC | 3.3V |
| GND | GND |
| SDA | GPIO 21 |
| SCL | GPIO 22 |

#### Módulo SD

| SD | ESP32 |
|----------|----------|
| VCC | 3.3V |
| GND | GND |
| CS | GPIO 5 |
| MOSI | GPIO 23 |
| MISO | GPIO 19 |
| SCK | GPIO 18 |

---

## Firmware

O firmware é responsável por:

- Configurar o MPU6050
- Ler acelerômetro e giroscópio
- Converter os dados para unidades físicas
- Registrar os dados em cartão SD
- Transmitir os dados via Serial para depuração

Formato registrado:

```text
ax,ay,az,gx,gy,gz,tempo_ms
```

Exemplo:

```text
0.0123,-0.0314,0.9981,0.1526,-0.2147,0.0814,12345
```

Taxa de aquisição:

```text
100 Hz (1 amostra a cada 10 ms)
```

---

## Visualizador

O software de visualização recebe os dados e calcula a orientação da embarcação.

Funcionalidades atuais:

- Visualização 3D em OpenGL
- Cálculo de Pitch
- Cálculo de Roll
- Estimativa de Yaw
- Filtro complementar
- Registro de dados para análise

Tecnologias utilizadas:

- Python
- PyGame
- PyOpenGL
- PySerial

---

## Estrutura do Projeto

```text
marine-imu/
│
├── firmware/
│   └── esp32_mpu6050_sd.ino
│
├── visualizer/
│   └── Visualizador.py
│
├── data/
│   └── dados.csv
│
├── docs/
│
└── README.md
```

---

## Estado Atual

- [x] Comunicação MPU6050
- [x] Leitura de acelerômetro
- [x] Leitura de giroscópio
- [x] Comunicação Serial
- [x] Registro em cartão SD
- [x] Timestamp por amostra
- [x] Visualização 3D
- [x] Filtro complementar
- [x] Calibração de offset do giroscópio
- [x] Exportação CSV

### Em desenvolvimento

- [ ] Replay de navegação
- [ ] Timeline temporal
- [ ] Detecção automática de eventos
- [ ] Estatísticas de estabilidade
- [ ] Filtro Mahony
- [ ] Filtro Madgwick
- [ ] Interface gráfica avançada

---

## Aplicações

- Monitor de trim
- Estudos de estabilidade
- Registro de movimento da embarcação
- Instrumentação náutica experimental
- Pesquisa em sensores inerciais
- Caixa-preta simplificada para embarcações

---

## Roadmap

### Replay de Navegação

Planeja-se implementar um sistema capaz de:

- Ler arquivos CSV gravados pelo ESP32
- Reproduzir a navegação em tempo real
- Exibir uma timeline interativa
- Detectar eventos relevantes
- Gerar estatísticas automáticas

---

## Licença

Projeto desenvolvido para fins educacionais, pesquisa e experimentação.

---

## Autor

Desenvolvido por Eduardo Muniz como parte de estudos em sistemas embarcados, sensores inerciais e instrumentação náutica.
