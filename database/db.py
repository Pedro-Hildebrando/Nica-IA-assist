# -*- coding: utf-8 -*-
import os
import mysql.connector
from dotenv import load_dotenv

# Carrega as configurações do arquivo .env
load_dotenv()

def get_db_connection():
    """Cria a conexão com o banco de dados utilizando o .env"""
    try:
        conexao = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        return conexao
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
        return None