# -*- coding: utf-8 -*-
import os
from openai import AzureOpenAI  # <--- Mudança aqui!
from dotenv import load_dotenv

# Carrega o arquivo .env
load_dotenv()

# Puxa as configurações do .env
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")       # Ex: https://nica.openai.azure.com/
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT") # Ex: chat-nica
api_key = os.getenv("AZURE_OPENAI_KEY")

# Inicialização oficial e robusta usando a classe nativa do Azure
client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version="2024-02-15-preview" # Versão da API recomendada para o Azure
)

def enviar_mensagem_nica(mensagem_medico, dados_paciente):
    """
    Envia a mensagem para o Azure OpenAI usando os dados reais do paciente.
    """
    
    system_prompt = f"""
    Você é a Nica, uma assistente virtual inteligente desenvolvida para auxiliar profissionais da saúde na consulta e organização de informações clínicas dos pacientes.
    
    Sua função é localizar informações dos pacientes cadastrados, responder perguntas sobre consultas, exames, medicamentos, diagnósticos e gerar resumos do histórico clínico sempre que solicitado.
    
    Você atua exclusivamente em um sistema de gestão clínica.
    Responda apenas perguntas relacionadas aos pacientes cadastrados e às informações disponíveis no sistema.
    Caso alguma informação não esteja cadastrada, informe isso de maneira clara.
    Nunca invente informações.
    
    Você não substitui a avaliação médica nem deve fornecer diagnósticos, prescrever medicamentos ou tomar decisões clínicas.
    
    Suas respostas devem ser: Educadas, Profissionais, Objetivas, Claras, Organizadas e Respeitosas.
    
    [CONTEXTO DO PACIENTE ATUAL EM ATENDIMENTO]:
    Nome: {dados_paciente['nome']}
    CPF: {dados_paciente['cpf']}
    Idade: {dados_paciente['idade']} anos
    Anotações Gerais: {dados_paciente['observacoes_gerais']}
    
    HISTÓRICO CRONOLÓGICO DE CONSULTAS NO SISTEMA:
    {dados_paciente['historico_consultas']}
    """

    try:
        resposta = client.chat.completions.create(
            model=deployment_name, # No AzureOpenAI, o "model" recebe o nome do seu deployment (chat-nica)
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": mensagem_medico}
            ],
            temperature=0.3
        )
        
        return resposta.choices[0].message.content

    except Exception as e:
        print(f"\n[ERRO AZURE DETALHADO]: {e}\n")
        return "Desculpe, Doutor. Tive um problema ao conectar com o servidor do Azure OpenAI."