import streamlit as st
import msal
import requests
from azure.core.credentials import AccessToken, TokenCredential
from langchain_community.agent_toolkits import PowerBIToolkit, create_pbi_agent
from langchain_community.utilities.powerbi import PowerBIDataset
from langchain_cohere import ChatCohere

# Credenciais do Aplicativo Azure AD
CLIENT_ID = '96070a8e-7f25-4e2a-b1a3-3d491245b8e4'
CLIENT_SECRET = '.o-8Q~OQjF2txHjVU.w36xVEepF8WVQ5Up-IQc5.'
AUTHORITY = 'https://login.microsoftonline.com/common'
SCOPE = ["https://analysis.windows.net/powerbi/api/.default"]
REDIRECT_URI = 'http://localhost:8501'  


class MyTokenCredential(TokenCredential):
    def __init__(self, access_token):
        self._access_token = access_token

    def get_token(self, *scopes, **kwargs):
        return AccessToken(self._access_token, 0)


@st.cache_resource
def initialize_agent(access_token):
    
    credential = MyTokenCredential(access_token)
    
    
    cohere_api_key = 'HcOn9LIjD4MztBiwoKXGdz0Ci2JeqwOd1VhRohAJ'  
    fast_llm = ChatCohere(
        model_name="command-light",
        temperature=0.3,
        verbose=True,
        cohere_api_key=cohere_api_key,
        max_tokens=1000
    )

    smart_llm = ChatCohere(
        model_name="command-light",
        verbose=True,
        cohere_api_key=cohere_api_key,
        temperature=0,
        max_tokens=100,
    )

    
    PowerBIDataset.update_forward_refs(TokenCredential=TokenCredential)

    
    few_shots = """
    Question: Quantas vezes o bairro Cajuru aparece na base de dados?
    DAX:
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
    
    -----------
    Question: Quantos anos a pessoa mais velha tem?
    DAX:
    EVALUATE
    ADDCOLUMNS(
        FILTER(
            'public covid19',
            'public covid19'[IDADE (anos)] = MAXX('public covid19', 'public covid19'[IDADE (anos)])
        ),
        "Idade Mais Velha", 'public covid19'[IDADE (anos)]
    )

-----------
    Question: Qual é o bairro com mais casos confirmados?
    DAX:
    EVALUATE
    TOPN(
        1,
        SUMMARIZE(
            FILTER(
                'public covid19',
                'public covid19'[CLASSIFICAÇÃO FINAL] = "CONFIRMADO"
            ),
            'public covid19'[BAIRRO],
            "Total Casos", COUNTROWS('public covid19')
        ),
        [Total Casos],
        DESC
    )

-----------
    Question: Total de obitos?
    DAX:
    EVALUATE
    ROW(
        "Total de Óbitos",
        COUNTROWS(
            FILTER(
                'public covid19',
                NOT(ISBLANK('public covid19'[DATA ÓBITO]))
            )
        )
    )
    """

    
    toolkit = PowerBIToolkit(
        powerbi=PowerBIDataset(
            dataset_id='3298ff60-f72f-48de-81fb-f5bf3a4c2bcf',
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
        max_iterations=3,
    )

    return agent_executor


def main():
    st.title("Chatbot Power BI")

    if 'access_token' not in st.session_state:
        authenticate_user()
    else:
        chatbot_interface()

def authenticate_user():
    
    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET,
    )

    
    query_params = st.experimental_get_query_params()

    if 'code' not in query_params:
        
        auth_url = app.get_authorization_request_url(
            scopes=SCOPE,
            redirect_uri=REDIRECT_URI,
        )
        st.write(f"Por favor, [faça login aqui]({auth_url}) para continuar.")
    else:
        
        code = query_params['code'][0]
        result = app.acquire_token_by_authorization_code(
            code,
            scopes=SCOPE,
            redirect_uri=REDIRECT_URI,
        )
        if "access_token" in result:
            st.session_state['access_token'] = result['access_token']
            st.write("Autenticação bem-sucedida!")
            st.experimental_rerun()  
        else:
            st.error("Erro ao adquirir o token: {}".format(result.get('error_description')))

def chatbot_interface():
    st.write("Você está autenticado. Faça suas perguntas abaixo.")

    
    access_token = st.session_state['access_token']
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    workspace_id = 'f2b8d789-ed55-4a47-a19c-d2ac79dea041'  
    dataset_id = '3298ff60-f72f-48de-81fb-f5bf3a4c2bcf'    
    datasets_url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}"
    dataset_response = requests.get(datasets_url, headers=headers)

    if dataset_response.status_code == 200:
        st.success("Conectado ao dataset do Power BI com sucesso.")
    else:
        st.error("Falha ao conectar ao dataset do Power BI.")
        st.stop()

    
    agent_executor = initialize_agent(access_token)

    
    question = st.text_input("Digite sua pergunta:")
    if st.button("Enviar") and question:
        with st.spinner("Processando..."):
            result = agent_executor.run(question)
        st.write("Resposta:", result)

if __name__ == "__main__":
    main()
