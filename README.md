# AgentPowerbi
Agent de powerbi que está com few-shot para responder questions sobre o dataset


#Descrição
Estou utilizando o Agent do LangChain, um framework que permite integrações específicas, como com o Power BI e DAX. (Link do framework: https://python.langchain.com/docs/integrations/tools/powerbi/). Esse Agent foi desenvolvido em inglês e tem um contexto focado em Power BI e DAX, permitindo realizar consultas usando DAX para buscar informações relevantes.

Configuração do Ambiente
Para habilitar o uso desse Agent, precisei configurar um usuário no Entra ID (antigo Azure Active Directory) e conceder as permissões necessárias para que ele possa acessar e consultar dados do Power BI via API REST. Esse usuário tem acesso ao Power BI Premium e ao workspace que criei, onde está configurado um dataset com conexão DirectQuery.

Estabeleci a conexão entre o Python e o Power BI incluindo o ID do dataset e o nome da tabela onde o Agent realizará consultas DAX para responder às perguntas dos usuários. Utilizei dados públicos sobre a Covid-19, disponibilizados pelo site da prefeitura de Curitiba (link: https://www.curitiba.pr.gov.br/dadosabertos/busca/?grupo=16), que foram armazenados em um banco de dados PostgreSQL em um servidor próprio.

Testes Iniciais com o LangChain e OpenAI
Após configurar o banco de dados, o Power BI e o Entra ID, testei o Agent do LangChain com os modelos de linguagem da OpenAI (GPT-3.5 Turbo e GPT-4.0). Consegui realizar algumas consultas DAX e obter respostas para perguntas, mas, devido ao crédito limitado, não consegui realizar muitos testes para aprimoramento.

Alternativa com a API do Cohere (https://cohere.com/)
Para continuar os testes, optei por usar a API do Cohere, que oferece um modelo open-source. No entanto, encontrei uma limitação: o modelo permite apenas 10 requisições por minuto, o que é insuficiente, pois meu sistema realiza diversas requisições numa cadeia de pensamento entre dois Agents. Para contornar essa limitação, implementei as seguintes melhorias:

- Técnica de Few-Shot Prompt: Em vez de utilizar a técnica zero-shot (onde não são fornecidos exemplos), adotei a técnica de few-shot, fornecendo exemplos de perguntas e respostas DAX no prompt para direcionar o modelo a um desempenho mais preciso.

- Limite de Requisições por Agent: Configurei o código para limitar cada Agent a cinco requisições, evitando exceder o limite imposto pela API do Cohere.

Atualmente, estou na fase de tentativa e erro, ajustando o código para garantir que o modelo traga resultados satisfatórios em português, pois, até agora, ele responde em inglês.


#Ambiente Controlado e Dados Públicos:#
Estou utilizando meu notebook pessoal para esse projeto, e todos os dados são públicos, obtidos através do site da prefeitura de Curitiba.

#Acesso Temporário com Conta premium da azure por 30 dias:#
Com a conta, consegui um acesso de 30 dias para testar as ferramentas da Microsoft, que oferecem R$ 1.080,00 em créditos para uso nesse período. Com esses créditos:

- Ativei o Power BI Premium por 30 dias.
- Configurei um servidor para hospedar um banco de dados PostgreSQL.
- Ativei o Microsoft Entra ID (antigo Active Directory) para gerenciar permissões e acessos.

#Uso de LLM Open Source (Cohere) para Testes:#
Estou utilizando a API de um modelo de LLM open source da Cohere. Como essa ferramenta é para testes, aceitei o contrato que permite o uso dos dados para o treinamento do modelo, já que não há informações sensíveis envolvidas.

#Planos para Ambiente Empresarial Seguro:#
Para o ambiente da empresa, o modelo deverá ser ajustado:

- Será necessária uma API da Google, openAi ou outra a escolha acredito que google pois ate onde tenho conhecimento é o que já está sendo utilizada na empresa, configurada com uma conta empresarial.
- O contrato da API deverá garantir que os dados não serão utilizados para treinamento, o que é um requisito essencial para manter a segurança e a privacidade.
- Em um ambiente empresarial, não utilizaremos o modelo open source da Cohere, e sim uma LLM com contrato que assegure que os dados fornecidos não serão usados para treinamento.
