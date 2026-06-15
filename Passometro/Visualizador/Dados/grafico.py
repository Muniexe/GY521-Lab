import pandas as pd
import matplotlib.pyplot as plt

dados = pd.read_csv("15062026.csv")

plt.figure(figsize=(12,5))

plt.plot(dados["roll"])

plt.title("Roll ao longo do tempo")
plt.xlabel("Amostra (ms)")
plt.ylabel("Roll")

plt.grid(True)

plt.show()