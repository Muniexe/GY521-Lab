import pandas as pd
import matplotlib.pyplot as plt

dados = pd.read_csv("dados.csv")

plt.figure(figsize=(12,5))

plt.plot(dados["magnitude"])

plt.title("Magnitude da aceleração")
plt.xlabel("Amostra")
plt.ylabel("Magnitude")

plt.grid(True)

plt.show()