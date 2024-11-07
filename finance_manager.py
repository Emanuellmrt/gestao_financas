import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# Função para carregar dados (substituir por conexão com banco de dados, se preferir)
@st.cache_data
def load_data():
    try:
        return pd.read_csv("transacoes.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["Data", "Descrição", "Categoria", "Valor", "Tipo"])

# Função para salvar dados
def save_data(data):
    data.to_csv("transacoes.csv", index=False)

# Função para adicionar transação
def add_transaction(data, date, description, category, amount, type):
    new_row = pd.DataFrame({"Data": [date], "Descrição": [description], "Categoria": [category], "Valor": [amount], "Tipo": [type]})
    data = pd.concat([data, new_row], ignore_index=True)
    save_data(data)
    return data

# Carregar dados
data = load_data()

# Dashboard
st.title("Sistema de Gestão Financeira")
st.header("Dashboard de Resumo Financeiro")

# Filtro por período
today = datetime.date.today()
start_date = st.sidebar.date_input("Data inicial", today.replace(day=1))
end_date = st.sidebar.date_input("Data final", today)

filtered_data = data[(pd.to_datetime(data["Data"]) >= pd.to_datetime(start_date)) & (pd.to_datetime(data["Data"]) <= pd.to_datetime(end_date))]

# Cálculo do saldo
total_income = filtered_data[filtered_data["Tipo"] == "Receita"]["Valor"].sum()
total_expense = filtered_data[filtered_data["Tipo"] == "Despesa"]["Valor"].sum()
balance = total_income - total_expense

# Exibir Resumo
st.metric("Saldo Atual", f"R${balance:,.2f}")
st.metric("Receitas", f"R${total_income:,.2f}")
st.metric("Despesas", f"R${total_expense:,.2f}")

# Gráfico de Despesas por Categoria
if not filtered_data.empty:
    fig, ax = plt.subplots()
    filtered_data[filtered_data["Tipo"] == "Despesa"].groupby("Categoria")["Valor"].sum().plot(kind="pie", autopct='%1.1f%%', ax=ax)
    ax.set_ylabel("")
    st.pyplot(fig)

# Cadastro de Transação
st.header("Cadastro de Transação")
with st.form(key="add_transaction_form"):
    date = st.date_input("Data", today)
    description = st.text_input("Descrição")
    category = st.selectbox("Categoria", ["Alimentação", "Moradia", "Lazer", "Transporte", "Outros"])
    amount = st.number_input("Valor", min_value=0.01, step=0.01, format="%.2f")
    type = st.selectbox("Tipo", ["Receita", "Despesa"])
    submitted = st.form_submit_button("Adicionar Transação")

    if submitted:
        data = add_transaction(data, date, description, category, amount, type)
        st.success("Transação adicionada com sucesso!")

# Visualização de Transações
st.header("Transações")
st.dataframe(filtered_data)

# Exportar dados
st.download_button("Exportar Dados em CSV", data.to_csv(index=False), "transacoes_exportadas.csv")

# Importar dados
st.header("Importar Dados")
uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv")
if uploaded_file:
    new_data = pd.read_csv(uploaded_file)
    data = pd.concat([data, new_data], ignore_index=True)
    save_data(data)
    st.success("Dados importados com sucesso!")
