# Raízes do Nordeste - Back-End

Projeto desenvolvido para a disciplina de Projeto Multidisciplinar - Trilha Back-End.

O sistema representa o back-end da rede de lanchonetes Raízes do Nordeste. A aplicação foi desenvolvida com foco em usuários, unidades, produtos, estoque, pedidos, pagamentos simulados, fidelidade, promoções e auditoria.

## Repositório

O código-fonte do projeto está disponível em:

https://github.com/YurgenLage/Projeto_Raizes_do_Nordeste

## Requisitos

Para executar o projeto é necessário ter instalado:

- Python 3.13.14
- pip
- SQLite
- Postman, para execução da coleção de testes

As dependências utilizadas pelo projeto estão listadas no arquivo:

`requirements.txt`

## Configuração das variáveis de ambiente

O projeto utiliza uma variável de ambiente para armazenar a chave usada na criação e validação dos tokens JWT.

Na raiz do projeto existe o arquivo:

`.env.example`

Crie um arquivo chamado `.env` também na raiz do projeto e configure a variável:

```env
SECRET_KEY=sua_chave_secreta_aqui
```

O arquivo `.env` é utilizado apenas na máquina local e não deve ser enviado para um repositório público.

## Ambiente virtual

Na pasta raiz do projeto, crie um ambiente virtual com o comando:

```powershell
python -m venv .venv
```

No Windows, ative o ambiente virtual com:

```powershell
.venv\Scripts\activate
```

## Instalação das dependências

Com o ambiente virtual ativo, execute:

```powershell
pip install -r requirements.txt
```

## Banco de dados

O projeto utiliza SQLite como banco de dados.

O arquivo utilizado pela aplicação é:

`raizes.db`

Não foram utilizadas migrations automatizadas.

Também não foi utilizado um seed automatizado. O arquivo `raizes.db` entregue junto ao projeto já contém os dados necessários para os testes.

## Como iniciar a API

Na pasta raiz do projeto, execute:

```powershell
python -m uvicorn codigo.app.main:app --reload
```

Depois de iniciar, a API estará disponível em:

[http://127.0.0.1:8000](http://127.0.0.1:8000)

## Swagger / OpenAPI

A documentação dos endpoints pode ser acessada pelo Swagger no endereço:

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

O Swagger permite visualizar e testar os endpoints implementados na API.

## Usuários utilizados nos testes

### Cliente

Email: `maria@teste.com`  
Senha: `abcdef`  
Perfil: `CLIENTE`

### Administrador

Email: `admin@teste.com`  
Senha: `123456`  
Perfil: `ADMIN`

## Testes

Os testes da API foram realizados utilizando o Postman.

A coleção de testes está salva na pasta:

`testes/`

Arquivo:

`Raízes do Nordeste - Testes.postman_collection.json`

A coleção está organizada nas pastas:

- Auth
- Pedidos
- Pagamento
- Estoque
- Produtos
- Fidelidade
- Auditoria

## Como executar os testes

1. Inicie a API.
2. Abra o Postman.
3. Importe a coleção de testes disponível na pasta `testes`.
4. Execute o teste `T01 - Login válido da Maria`.
5. Copie o `access_token` retornado.
6. Utilize esse token como Bearer Token nas requisições que exigem autenticação de cliente.
7. Para os testes que precisam de permissão administrativa, execute `Login Admin`.
8. Copie o token retornado pelo login do administrador e utilize nas requisições administrativas.
9. Execute os testes na ordem sugerida abaixo.

Os tokens JWT possuem validade de 30 minutos. Caso um token expire, basta realizar o login novamente.

## Ordem sugerida dos testes

- T01 - Login válido da Maria
- T02 - Criar pedido válido
- T03 - Pagamento aprovado
- T04A - Criar pedido para recusa
- T04 - Pagamento recusado
- T04B - Conferir estoque após recusa
- T05 - Cardápio por unidade
- T06 - Consultar pontos de fidelidade
- T07 - Acesso sem token
- T08 - Cliente sem permissão para listar usuários
- T09 - Canal de pedido inválido
- Login Admin
- T10 - Transição de status inválida
- T11 - Campo obrigatório ausente
- T12 - Produto inexistente
- T13 - Estoque insuficiente
- T14 - Auditoria de ação sensível
- T15 - Tipo/formato inválido

## Dados utilizados nos testes

Os principais dados utilizados durante os testes são:

- Usuário cliente: id 2
- Usuário administrador: id 3
- Unidade: id 1
- Produto: id 1

Alguns testes criam novos pedidos. Por esse motivo, o número do pedido pode mudar conforme os testes forem sendo executados.

## Funcionalidades principais

- Cadastro e autenticação de usuários
- Autenticação com JWT
- Controle de acesso por perfil
- Cadastro e consulta de unidades
- Cadastro e consulta de produtos
- Cardápio por unidade
- Controle de estoque
- Criação de pedidos
- Registro do canal de origem do pedido
- Consulta e filtro de pedidos
- Atualização do status dos pedidos
- Pagamento simulado
- Pagamento aprovado e recusado
- Devolução de estoque em pagamento recusado
- Programa de fidelidade
- Promoções
- Auditoria de ações importantes
- Tratamento padronizado de erros

## Observações

A aplicação foi desenvolvida para execução local.

A documentação principal dos endpoints está disponível pelo Swagger.

Os testes incluem cenários positivos e negativos, como autenticação válida, falta de autenticação, falta de permissão, criação de pedido, pagamento aprovado e recusado, produto inexistente, estoque insuficiente, canal inválido e validação de campos obrigatórios.
