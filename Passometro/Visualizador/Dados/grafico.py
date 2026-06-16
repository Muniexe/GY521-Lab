import pandas as pd
import matplotlib.pyplot as plt

dados = pd.read_csv("160626.csv")

plt.figure(figsize=(12,5))

plt.plot(dados["pitch"])

plt.title("Pitch ao longo do tempo")
plt.xlabel("Amostra (ms)")
plt.ylabel("Pitch")

plt.grid(True)

plt.show()