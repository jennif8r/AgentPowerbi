from azure.identity import InteractiveBrowserCredential
from azure.core.credentials import TokenCredential  
from langchain_community.agent_toolkits import PowerBIToolkit, create_pbi_agent
from langchain_community.utilities.powerbi import PowerBIDataset
from langchain_cohere import ChatCohere
import requests

few_shots = """
1- ###Question:## Quantas vezes o bairro Cajuru aparece na base de dados?
###Resposta:### a query DAX que responde essa pergunta 
'

EVALUATE
ROW(
    "Total Cajuru", 
    COUNTROWS(
        FILTER(
            'public covid19',
            'public covid19'[bairro] = "CAJURU"
        )
    )
)'.


2- ###Question:## Quantas vezes o centro aparece na base de dados?
###Resposta:### a query DAX que responde essa pergunta:
'

EVALUATE
ROW(
    "Total Centro", 
    COUNTROWS(
        FILTER(
            'public covid19',
            'public covid19'[bairro] = "CENTRO"
        )
    )
)'.

"""
# Definir IDs do workspace e dataset do Power BI
workspace_id = 'f2b8d789-ed55-4a47-a19c-d2ac79dea041'
dataset_id = '3298ff60-f72f-48de-81fb-f5bf3a4c2bcf'

# Inicialização dos modelos LLM com chaves da OpenAI
fast_llm = ChatCohere( 
    model_name="command-r-plus", 
    verbose=True, 
    cohere_api_key='HcOn9LIjD4MztBiwoKXGdz0Ci2JeqwOd1VhRohAJ'
)

smart_llm = ChatCohere(
    model_name="command-r-plus", 
    verbose=True,
    cohere_api_key='HcOn9LIjD4MztBiwoKXGdz0Ci2JeqwOd1VhRohAJ'
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

    # Resolver a referência do campo `credential` no PowerBIDataset
    PowerBIDataset.update_forward_refs(TokenCredential=TokenCredential)
    
    toolkit = PowerBIToolkit(
            powerbi=PowerBIDataset(
                dataset_id=dataset_id,
                table_names=["public covid19"],  
                credential=credential
            ),
            llm=smart_llm,
            examples=few_shots,
            output_token_limit=1000,
        )
    
    agent_executor = create_pbi_agent(
            llm=fast_llm,
            toolkit=toolkit,
            verbose=True,
            max_itarations=5,
       )
    # Exemplos de consultas que o agente pode executar
    result = agent_executor.run("Quantas vezes o cajuru aparece na base de dados")
    print("Resposta:", result)

    
else:
    print(f"Falha na autenticação: {dataset_response.status_code}")
    print("Detalhes da resposta:", dataset_response.text)
