# Passômetro / Visualizador MPU-6050

Objetivo

Este projeto utiliza o sensor GY-521 (MPU-6050) para:

Coletar dados de aceleração e velocidade angular.
Visualizar a orientação do sensor em tempo real através de um cubo 3D.
Servir como base para o desenvolvimento de um p
assômetro.
Servir como etapa de pesquisa para aplicações futuras em cálculo de trim de embarcações.

Hardware Utilizado
| Componente        | Função                       |
| ----------------- | ---------------------------- |
| Arduino Uno       | Aquisição dos dados          |
| GY-521 (MPU-6050) | Sensor inercial              |
| Cabo USB          | Comunicação serial           |
| Computador        | Processamento e visualização |

Ligações
GY-521      Arduino Uno

VCC   ----> 5V
GND   ----> GND
SDA   ----> A4
SCL   ----> A5

Técnicas Utilizadas
Filtro Digital do MPU-6050

Foi configurado o DLPF interno do sensor para reduzir ruído de alta frequência.

Calibração do Giroscópio

Ao iniciar o programa:

Mantenha o sensor parado...

são coletadas 300 amostras para cálculo dos offsets.

Filtro Passa-Baixa

Aplicado aos dados do acelerômetro para reduzir jitte
Filtro Complementar

Combina:

estabilidade de longo prazo do acelerômetro;
resposta rápida do giroscópio.

A equação utilizada é:

θ=0.98(θ+ωΔt)+0.02θ
acc

Como Executar
1. Instalar Python

Versão recomendada:

Python 3.12

2. Instalar Dependências
`py -3.12 -m pip install pygame`
`py -3.12 -m pip install pyserial`
`py -3.12 -m pip install PyOpenGL`
`py -3.12 -m pip install PyOpenGL_accelerate`

3. Enviar Firmware

Abra:

firmware/mpu6050.ino

e envie para o Arduino Uno.

4. Configurar Porta Serial

No arquivo:

visualizador/cubo.py

alterar:

PORTA = "COM3"

para a porta correspondente ao Arduino.

5. Executar

`py -3.12 cubo.py`

Procedimento de Teste

Teste 1 – Sensor Parado

Posicionar o sensor sobre uma superfície plana.

Resultado esperado:

Cubo estável.
Pequena oscilação residual.
Sem rotações espontâneas significativas.

Teste 2 – Inclinação

Inclinar lentamente:

Frente e trás.
Esquerda e direita.

Resultado esperado:

Cubo acompanha os movimentos.

Teste 3 – Rotação

Rotacionar o sensor em torno do eixo vertical.

Resultado esperado:

Cubo acompanha a rotação.
Pode ocorrer drift gradual devido à ausência de magnetômetro.
