# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
from database.db import get_db_connection
from datetime import date

# IMPORTANTE: Aqui estamos trazendo a função da IA
from services.openai_service import enviar_mensagem_nica

app = Flask(__name__)

def calcular_idade(data_nascimento):
    """Calcula a idade baseada na data de nascimento vinda do MySQL"""
    if not data_nascimento:
        return 0
    hoje = date.today()
    idade = hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))
    return idade if idade >= 0 else 0

def buscar_paciente_do_banco(paciente_id):
    """Busca as informações do paciente e todo o seu histórico de consultas"""
    conexao = get_db_connection()
    if not conexao:
        return None

    cursor = conexao.cursor(dictionary=True)
    try:
        # 1. Busca dados básicos do paciente
        query_paciente = "SELECT id, nome, cpf, nascimento, observacoes FROM pacientes WHERE id = %s"
        cursor.execute(query_paciente, (paciente_id,))
        paciente = cursor.fetchone()

        if not paciente:
            return None

        # 2. Busca todas as consultas desse paciente ordenadas pela mais recente
        query_consultas = "SELECT data_consulta, relato_medico FROM consultas WHERE paciente_id = %s ORDER BY data_consulta DESC"
        cursor.execute(query_consultas, (paciente_id,))
        historico_consultas = cursor.fetchall()

        # 3. Formata as consultas em texto para a IA entender
        texto_consultas = ""
        for c in historico_consultas:
            data_formatada = c['data_consulta'].strftime('%d/%m/%Y')
            texto_consultas += f"\n* DATA: {data_formatada} - EVOLUÇÃO: {c['relato_medico']}\n"

        if not texto_consultas:
            texto_consultas = "Nenhuma consulta anterior registrada no sistema."

        return {
            "id": paciente["id"],
            "nome": paciente["nome"],
            "cpf": paciente["cpf"] or "Não informado",
            "idade": calcular_idade(paciente["nascimento"]),
            "observacoes_gerais": paciente["observacoes"] or "Nenhuma observação geral.",
            "historico_consultas": texto_consultas  # <--- Aqui está o segredo!
        }
    except Exception as e:
        print(f"Erro na consulta SQL detalhada: {e}")
        return None
    finally:
        cursor.close()
        conexao.close()

def listar_todos_pacientes():
    """Busca a lista de todos os pacientes cadastrados para montar o menu"""
    conexao = get_db_connection()
    if not conexao:
        return []
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, nome FROM pacientes ORDER BY nome")
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao listar pacientes: {e}")
        return []
    finally:
        cursor.close()
        conexao.close()


@app.route('/')
def index():
    lista_pacientes = listar_todos_pacientes()
    
    id_padrao = lista_pacientes[0]['id'] if lista_pacientes else 1
    paciente_id = request.args.get('id', default=id_padrao, type=int)
    
    paciente_real = buscar_paciente_do_banco(paciente_id)
    
    if not paciente_real:
        paciente_real = {
            "id": 0,
            "nome": "Selecione um Paciente",
            "idade": 0,
            "cpf": "000.000.000-00",
            "historico": "Nenhum prontuário carregado no momento. Cadastre pacientes no MySQL."
        }
        
    return render_template('index.html', paciente=paciente_real, lista_pacientes=lista_pacientes)



#ROTA DO CHAT CONECTADA À OPENAI

@app.route('/chat', methods=['POST'])
def chat():
    dados_requisicao = request.json
    user_message = dados_requisicao.get('message', '')
    
    # Descobre qual paciente está aberto na tela olhando o link do navegador
    referer = request.referrer or ""
    paciente_id = 1
    if "id=" in referer:
        try:
            paciente_id = int(referer.split("id=")[1].split("&")[0])
        except:
            paciente_id = 1

    # Busca os dados desse paciente específico no MySQL para passar como contexto para a IA
    dados_paciente = buscar_paciente_do_banco(paciente_id)
    
    if not dados_paciente:
        return jsonify({"response": "Erro: Nenhum paciente selecionado para o chat."})

    # Envia a mensagem do médico + os dados do banco para a OpenAI decidir a resposta da Nica
    bot_response = enviar_mensagem_nica(user_message, dados_paciente)
    
    return jsonify({"response": bot_response})


if __name__ == '__main__':
    app.run(debug=True)