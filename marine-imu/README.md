# Marine IMU

Sistema de monitoramento de orientação para embarcações utilizando MPU6050 e Arduino.

## Objetivo

Este projeto foi desenvolvido para medir a orientação de uma embarcação em tempo real através de uma IMU MPU6050.

O sistema realiza a leitura do acelerômetro e giroscópio, aplica algoritmos de fusão sensorial e disponibiliza os dados para visualização em um computador.

Os principais objetivos são:

- Medição de Roll (inclinação lateral)
- Medição de Pitch (inclinação longitudinal)
- Monitoramento de trim da embarcação
- Estudos de estabilidade
- Desenvolvimento de instrumentação náutica de baixo custo

---

## Hardware

### Componentes

- Arduino Uno
- MPU6050 (GY-521)
- Cabo USB
- Computador para visualização dos dados

### Ligações

| MPU6050 | Arduino Uno |
|----------|----------|
| VCC | 5V |
| GND | GND |
| SDA | A4 |
| SCL | A5 |

---

## Software

### Firmware

O firmware é responsável por:

- Configurar o MPU6050
- Ler acelerômetro e giroscópio
- Converter os dados para unidades físicas
- Transmitir os dados via Serial

Formato enviado:

```text
ax,ay,az,gx,gy,gz,timestamp
```

Exemplo:

```text
0.012,-0.031,0.998,0.15,-0.21,0.08,12345
```

---

## Visualizador

O software de visualização recebe os dados da porta serial e calcula a orientação da embarcação.

Atualmente são avaliados:

- Filtro Complementar
- Filtro Mahony
- Filtro Madgwick

Critérios de comparação:

- Estabilidade
- Drift
- Consumo computacional
- Facilidade de implementação

---

## Estrutura do Projeto

```text
marine-imu/
│
├── firmware/
│   └── mpu6050.ino
│
├── visualizer/
│   └── Visualizador.py
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
- [x] Comunicação serial
- [x] Visualização 3D
- [x] Filtro Complementar
- [ ] Filtro Mahony
- [ ] Filtro Madgwick
- [ ] Calibração automática
- [ ] Interface gráfica avançada

---

## Aplicações Futuras

- Monitor de trim em embarcações
- Registro de movimento
- Sistema de estabilização
- Instrumentação náutica
- Estudos de comportamento em navegação

---

## Licença

Projeto desenvolvido para fins educacionais, pesquisa e experimentação.