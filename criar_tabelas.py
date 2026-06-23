from database.db import conectar

conexao = conectar()
cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS pacientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(20),
    telefone VARCHAR(20),
    nascimento DATE,
    observacoes TEXT
)
""")

conexao.commit()

print("✅ Tabela pacientes criada com sucesso!")

cursor.close()
conexao.close()