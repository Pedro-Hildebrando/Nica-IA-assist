from flask import Blueprint, render_template, request
from database.db import conectar

pacientes_bp = Blueprint("pacientes", __name__)

# Cadastro de pacientes
@pacientes_bp.route("/pacientes", methods=["GET", "POST"])
def pacientes():

    if request.method == "POST":

        nome = request.form["nome"]
        cpf = request.form["cpf"]
        telefone = request.form["telefone"]
        nascimento = request.form["nascimento"]
        observacoes = request.form["observacoes"]

        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        INSERT INTO pacientes
        (nome, cpf, telefone, nascimento, observacoes)
        VALUES (%s, %s, %s, %s, %s)
        """

        valores = (
            nome,
            cpf,
            telefone,
            nascimento,
            observacoes
        )

        cursor.execute(sql, valores)

        conexao.commit()

        cursor.close()
        conexao.close()

        return "✅ Paciente cadastrado com sucesso!"

    return render_template("pacientes/cadastro.html")


# Lista de pacientes
@pacientes_bp.route("/lista-pacientes")
def lista_pacientes():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("SELECT * FROM pacientes")

    pacientes = cursor.fetchall()

    cursor.close()
    conexao.close()

    return render_template(
        "pacientes/lista.html",
        pacientes=pacientes
    )