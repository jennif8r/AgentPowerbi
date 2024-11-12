from azure.identity import InteractiveBrowserCredential
from azure.core.credentials import TokenCredential
from langchain_community.utilities.powerbi import PowerBIDataset
from langchain_community.agent_toolkits import PowerBIToolkit
from langchain_community.vectorstores import FAISS
from langchain_cohere import CohereEmbeddings, ChatCohere
import requests

# Dicionário de perguntas predefinidas e suas consultas DAX correspondentes
predefined_queries = {
    "Quantas vezes o bairro 'Cajuru' aparece na base de dados na coluna 'bairro'?": """
EVALUATE
ROW(
    "Total Cajuru", 
    COUNTROWS(
        FILTER(
            'public covid19',
            'public covid19'[bairro] = "CAJURU"
        )
    )
)
"""
}

# Definir IDs do workspace e dataset do Power BI
workspace_id = 'f2b8d789-ed55-4a47-a19c-d2ac79dea041'
dataset_id = '3298ff60-f72f-48de-81fb-f5bf3a4c2bcf'

cohere_api_key = 'key'
# Inicialização do modelo LLM com chave da Cohere
fast_llm = ChatCohere(
    model_name="command-r-plus",
    verbose=True,
    cohere_api_key=cohere_api_key
)

# Autenticação interativa via navegador
credential = InteractiveBrowserCredential()

# Definir o escopo da API do Power BI
POWERBI_SCOPE = ["https://analysis.windows.net/powerbi/api/.default"]

# Obter o token de acesso para o Power BI
token = credential.get_token(*POWERBI_SCOPE).token

# Cabeçalho de autorização com o token de acesso
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Verificar se a autenticação foi bem-sucedida ao consultar um dataset
datasets_url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}"
dataset_response = requests.get(datasets_url, headers=headers)

if dataset_response.status_code == 200:
    print("Autenticação bem-sucedida. Continuando com a execução...")

    # Inicializar o PowerBIDataset
    powerbi_dataset = PowerBIDataset(
        dataset_id=dataset_id,
        table_names=["public covid19"],
        credential=credential
    )

  # Inicializar o toolkit
    toolkit = PowerBIToolkit(
        powerbi=powerbi_dataset,
        llm=fast_llm
    )

# Obter a ferramenta 'query_dax' do toolkit
    tools = toolkit.get_tools()
    query_dax_tool = None
    for tool in tools:
        if tool.name == 'query_dax':
            query_dax_tool = tool
            break

    if query_dax_tool is None:
        print("Erro: A ferramenta 'query_dax' não foi encontrada no toolkit.")
        exit()
        
    # Criar embeddings das perguntas predefinidas
    embeddings = CohereEmbeddings(
    model="embed-multilingual-v3.0",
    cohere_api_key=cohere_api_key
    )

    predefined_questions = list(predefined_queries.keys())
    vectorstore = FAISS.from_texts(predefined_questions, embeddings)

    def get_matching_query(question, vectorstore, predefined_queries):
        similar_docs = vectorstore.similarity_search(question, k=1)
        if similar_docs:
            matched_question = similar_docs[0].page_content
            dax_query = predefined_queries[matched_question]
            return dax_query
        return None

    # Exemplo de pergunta do usuário
    user_question = "Quantas vezes o bairro 'Cajuru' aparece na base de dados na coluna 'bairro'?"

    # Obter a consulta DAX correspondente
    dax_query = get_matching_query(user_question, vectorstore, predefined_queries)

    if dax_query:
        # Executar a consulta DAX usando o PowerBIDataset
        result = query_dax_tool.run(dax_query)
        print("Resposta:", result)
    else:
        print("A informação solicitada não existe.")

else:
    print(f"Falha na autenticação: {dataset_response.status_code}")
    print("Detalhes da resposta:", dataset_response.text)
