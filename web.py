import sqlite3
import pandas as pd

# 1️⃣ Lê o arquivo CSV (coloque o caminho correto)
df = pd.read_csv("C:/Users/winic/OneDrive/Área de Trabalho/filmes.csv")

# 2️⃣ Cria (ou abre) o banco de dados SQLite local
conn = sqlite3.connect("filmes.db")

# 3️⃣ Salva o DataFrame como tabela chamada 'filmes'
df.to_sql("filmes", conn, if_exists="replace", index=False)

# 4️⃣ Fecha a conexão
conn.close()

print("✅ Banco de dados 'filmes.db' criado com sucesso!")


