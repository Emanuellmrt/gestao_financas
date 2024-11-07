import streamlit as st
import pandas as pd
import plotly.express as px
import datetime


# Função para carregar dados (substituir por conexão com banco de dados, se preferir)
@st.cache_data
def load_data():
    try:
        data = pd.read_csv("transacoes.csv")
        # Garantir que a coluna 'Data' seja interpretada como datas
        data["Data"] = pd.to_datetime(data["Data"], errors="coerce").dt.date
    except FileNotFoundError:
        # Inicializar com um DataFrame vazio, caso o arquivo não exista
        data = pd.DataFrame(columns=["Data", "Descrição", "Categoria", "Valor", "Tipo"])
        data.to_csv("transacoes.csv", index=False)  # Salva o arquivo para futura utilização
    return data

# Função para salvar dados
def save_data(data):
    data.to_csv("transacoes.csv", index=False)

# Função para adicionar transação
def add_transaction(data, date, description, category, amount, type):
    new_row = pd.DataFrame({
        "Data": [date],
        "Descrição": [description],
        "Categoria": [category],
        "Valor": [amount],
        "Tipo": [type]
    })
    data = pd.concat([data, new_row], ignore_index=True)
    save_data(data)
    return data

# Função para editar uma transação
def edit_transaction(data, index, date, description, category, amount, type):
    data.loc[index] = [date, description, category, amount, type]
    save_data(data)
    return data

# Função para excluir uma transação
def delete_transaction(data, index):
    data = data.drop(index).reset_index(drop=True)
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

# Filtrando dados pelo período selecionado
filtered_data = data[(pd.to_datetime(data["Data"]) >= pd.to_datetime(start_date)) & (pd.to_datetime(data["Data"]) <= pd.to_datetime(end_date))]

# Exibindo métricas de saldo, receitas e despesas, verificando se há dados
if not filtered_data.empty:
    total_income = filtered_data[filtered_data["Tipo"] == "Receita"]["Valor"].sum()
    total_expense = filtered_data[filtered_data["Tipo"] == "Despesa"]["Valor"].sum()
    balance = total_income - total_expense

    # Exibir Resumo
    st.metric("Saldo Atual", f"R${balance:,.2f}")
    st.metric("Receitas", f"R${total_income:,.2f}")
    st.metric("Despesas", f"R${total_expense:,.2f}")

    # Gráfico de Despesas por Categoria
    despesas_data = filtered_data[filtered_data["Tipo"] == "Despesa"]
    if not despesas_data.empty:
        fig = px.pie(despesas_data, names="Categoria", values="Valor", title="Distribuição de Despesas por Categoria")
        st.plotly_chart(fig)
    else:
        st.write("Nenhuma despesa encontrada para o período selecionado.")

    # Gráfico de Barras de Receitas vs Despesas por Mês
    # Agrupar por mês e ano, somando as receitas e despesas
    filtered_data['Ano-Mês'] = filtered_data['Data'].apply(lambda x: x.replace(day=1))  # Adicionar Ano-Mês
    grouped_data = filtered_data.groupby(['Ano-Mês', 'Tipo'])['Valor'].sum().reset_index()

    # Criar gráfico de barras
    if not grouped_data.empty:
        fig = px.bar(grouped_data, x='Ano-Mês', y='Valor', color='Tipo', barmode='group', 
                     title="Comparação de Receitas e Despesas ao Longo dos Meses")
        st.plotly_chart(fig)
    else:
        st.write("Nenhum dado disponível para comparar receitas e despesas.")
else:
    st.write("Nenhuma transação disponível para o período selecionado.")

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

# Exibir transações
st.header("Transações")
if not filtered_data.empty:
    st.dataframe(filtered_data)

    # Editar ou excluir transações
    st.subheader("Editar ou Excluir Transação")
    transaction_index = st.selectbox("Escolha a transação para editar ou excluir", filtered_data.index, format_func=lambda x: f"{filtered_data.loc[x, 'Descrição']} - {filtered_data.loc[x, 'Data']}")
    
    selected_transaction = filtered_data.loc[transaction_index]

    # Exibir detalhes da transação selecionada
    st.write(f"Data: {selected_transaction['Data']}")
    st.write(f"Descrição: {selected_transaction['Descrição']}")
    st.write(f"Categoria: {selected_transaction['Categoria']}")
    st.write(f"Valor: R${selected_transaction['Valor']:,.2f}")
    st.write(f"Tipo: {selected_transaction['Tipo']}")

    # Formulário de edição
    st.header("Editar Transação")
    new_date = st.date_input("Nova Data", selected_transaction['Data'])
    new_description = st.text_input("Nova Descrição", selected_transaction['Descrição'])
    new_category = st.selectbox("Nova Categoria", ["Alimentação", "Moradia", "Lazer", "Transporte", "Outros"], index=["Alimentação", "Moradia", "Lazer", "Transporte", "Outros"].index(selected_transaction['Categoria']))
    new_amount = st.number_input("Novo Valor", min_value=0.01, value=selected_transaction['Valor'], step=0.01, format="%.2f")
    new_type = st.selectbox("Novo Tipo", ["Receita", "Despesa"], index=["Receita", "Despesa"].index(selected_transaction['Tipo']))

    # Botão para salvar a edição
    if st.button("Salvar Edição"):
        data = edit_transaction(data, transaction_index, new_date, new_description, new_category, new_amount, new_type)
        st.success("Transação editada com sucesso!")

    # Botão para excluir a transação
    if st.button("Excluir Transação"):
        data = delete_transaction(data, transaction_index)
        st.success("Transação excluída com sucesso!")

else:
    st.write("Nenhuma transação disponível para exibir.")

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
