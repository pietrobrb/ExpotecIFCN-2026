# Sistema de Gerenciamento da Expotec 2026

Projeto Django para gerenciamento da Expotec do IFRN Currais Novos.

## Configuração no Windows

Tenha Python 3.14 e Git instalados. Abra o PowerShell na pasta do projeto.

Copie o arquivo de exemplo e configure o `.env` para desenvolvimento local. Mantenha `DEBUG=True` para usar o SQLite:

```powershell
Copy-Item .env.exemplo .env
```

Crie o ambiente virtual e instale as dependências:

```powershell
py -3.14 -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

Não é necessário ativar o ambiente virtual. Os comandos abaixo usam o Python dele diretamente.

Prepare o banco de dados:

```powershell
.\venv\Scripts\python.exe manage.py migrate
```

Para carregar os dados iniciais disponíveis no projeto:

```powershell
.\venv\Scripts\python.exe manage.py loaddata config/fixtures/initial.json
```

Verifique a configuração e inicie o servidor:

```powershell
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py runserver
```

Acesse `http://127.0.0.1:8000/portal/`.

O `.env`, o banco local `db.sqlite3` e o ambiente `venv` não são enviados ao GitHub. Cada pessoa que clonar o projeto precisa preparar seu ambiente.

## Integração com o SUAP

Acesse [a página de aplicações OAuth2 do SUAP](https://suap.ifrn.edu.br/admin/api/aplicacaooauth2/) com uma conta autorizada. Clique em **Adicionar Aplicação OAUTH2** e informe:

- **Name:** nome que aparecerá para o usuário na hora do login.
- **Authorization grant type:** `Authorization code`.
- **Redirect URIs:** coloque cada endereço em uma linha:
  - `http://127.0.0.1:8000/accounts/suap/login/callback/`
  - `http://localhost:8000/accounts/suap/login/callback/`
- **Client type:** `Confidential`.

Anote o Client ID e o Client Secret gerados e coloque-os no seu `.env`, nas variáveis `SUAP_CLIENT_ID` e `SUAP_CLIENT_SECRET`. Não envie essas credenciais ao GitHub.

## Atualizar os dados iniciais

Quando for necessário atualizar o arquivo de dados iniciais do projeto:

```powershell
.\venv\Scripts\python.exe -X utf8 manage.py dumpdata auth.group usuarios eventos atividades documentos enderecos portal --natural-primary --natural-foreign --output=config/fixtures/initial.json
```

Confira as alterações nesse arquivo antes de incluí-lo em um commit.

## Fluxo de desenvolvimento

1. Clone o repositório e configure o ambiente seguindo as instruções acima.
2. Antes de começar um novo trabalho, use `git pull` para receber as alterações da equipe.
3. Faça e teste suas alterações. Confira os arquivos modificados com `git status`.
4. Adicione apenas os arquivos relacionados à alteração e crie um commit com uma mensagem clara.
5. Use `git push` para enviar o commit ao GitHub.

Consulte também o [GitHub Flow](https://docs.github.com/pt/get-started/using-github/github-flow).

## Estilo

Siga o [PEP 8](https://peps.python.org/pep-0008/) e o [guia de estilo do Django](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/).

- Use `PascalCase` para nomes de classes e modelos.
- Use nomes de modelos no singular.
- Use `snake_case` para métodos e funções. Exemplo: `pagina_inicial`.
- Evite espaços e linhas vazias desnecessários.
- Use 4 espaços para indentar Python e 2 espaços para HTML, CSS e JavaScript.
- Remova imports e includes desnecessários.

## Dependências

Ao instalar um pacote necessário ao projeto, adicione-o ao `requirements.txt`, teste a instalação e inclua essa alteração no commit. Não substitua automaticamente o arquivo inteiro usando `pip freeze`, pois ele também pode listar pacotes sem relação com o projeto.
