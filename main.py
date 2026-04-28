import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import urllib.parse

# Configuração do Banco de Dados
conn = sqlite3.connect('clientes_iptv.db', check_same_thread=False)
c = conn.cursor()

def create_table():
    c.execute('''CREATE TABLE IF NOT EXISTS clientes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  nome TEXT, telefone TEXT, usuario TEXT, senha TEXT, vencimento DATE)''')
    conn.commit()

create_table()

st.title("📺 IPTV Manager Pro")

menu = ["Cadastrar Cliente", "Lista & Cobrança"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Cadastrar Cliente":
    st.subheader("📝 Novo Cadastro")
    with st.form("cadastro_form"):
        nome = st.text_input("Nome do Cliente")
        telefone = st.text_input("WhatsApp (Ex: 5511999999999)", help="Coloque o código do país + DDD + Número")
        user = st.text_input("Usuário IPTV")
        senha = st.text_input("Senha IPTV")
        vencimento = st.date_input("Data de Vencimento")
        submit = st.form_submit_button("Salvar Cliente")
        
        if submit:
            c.execute("INSERT INTO clientes (nome, telefone, usuario, senha, vencimento) VALUES (?,?,?,?,?)", 
                      (nome, telefone, user, senha, vencimento))
            conn.commit()
            st.success(f"Cliente {nome} cadastrado!")

elif choice == "Lista & Cobrança":
    st.subheader("📅 Gestão e Alertas")
    
    df = pd.read_sql_query("SELECT * FROM clientes", conn)
    if not df.empty:
        df['vencimento'] = pd.to_datetime(df['vencimento']).dt.date
        hoje = datetime.now().date()
        alvo = hoje + timedelta(days=2)

        for index, row in df.iterrows():
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.write(f"**{row['nome']}**")
                st.caption(f"Vence em: {row['vencimento']}")
            
            with col2:
                # Lógica de Alerta
                if row['vencimento'] == alvo:
                    st.warning("⚠️ Vence em 2 dias!")
                elif row['vencimento'] < hoje:
                    st.error("🚨 Vencido!")

            with col3:
                # Criar link do WhatsApp
                msg = f"Olá {row['nome']}, seu plano de IPTV vence dia {row['vencimento'].strftime('%d/%m')}. Deseja realizar a renovação?"
                msg_encoded = urllib.parse.quote(msg)
                link_wa = f"https://wa.me/{row['telefone']}?text={msg_encoded}"
                
                st.link_button("Cobrar", link_wa)
            st.divider()
    else:
        st.info("Nenhum cliente cadastrado.")
