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

O `.env`, o banco local `db.sqlite3` e o ambiente `venv` não são enviados ao GitHub. Cada pessoa que clonar o projeto precisa preparar seu próprio ambiente.

## Integração com o SUAP

Acesse [a página de aplicações OAuth2 do SUAP](https://suap.ifrn.edu.br/admin/api/aplicacaooauth2/) com uma conta autorizada. Clique em **Adicionar Aplicação OAUTH2** e informe:

- **Name:** nome que aparecerá para o usuário na hora do login.
- **Authorization grant type:** `Authorization code`.
- **Redirect URIs:** coloque cada endereço em uma linha:
  - `http://127.0.0.1:8000/accounts/suap/login/callback/`
  - `http://localhost:8000/accounts/suap/login/callback/`
- **Client type:** `Confidential`.

Anote o Client ID e o Client Secret gerados e coloque-os no seu `.env`, nas variáveis `SUAP_CLIENT_ID` e `SUAP_CLIENT_SECRET`.

**Nunca envie essas credenciais ao GitHub.**

Para informações adicionais sobre a integração OAuth2 com o SUAP, consulte [`doc/suap_oauth.md`](doc/suap_oauth.md).

## Estrutura do projeto

O projeto é dividido em aplicações Django com responsabilidades específicas:

- `eventos/` — gerenciamento dos eventos e informações das edições.
- `chamadas/` — gerenciamento das chamadas, etapas, critérios e documentos relacionados.
- `submissao/` — gerenciamento da submissão de trabalhos.
- `credenciamento/` — funcionalidades relacionadas ao credenciamento.
- `documentos/` — gerenciamento de documentos.
- `enderecos/` — gerenciamento de endereços.
- `usuarios/` — gerenciamento dos usuários e informações dos participantes.
- `portal/` — páginas públicas do evento.
- `suap_oauth/` — integração de autenticação com o SUAP.
- `config/` — configurações, URLs e arquivos gerais do projeto.

## Atualizar os dados iniciais

Quando for necessário atualizar o arquivo de dados iniciais do projeto:

```powershell
.\venv\Scripts\python.exe -X utf8 manage.py dumpdata auth.group usuarios eventos atividades documentos enderecos portal --natural-primary --natural-foreign --output=config/fixtures/initial.json
```

Confira as alterações nesse arquivo antes de incluí-lo em um commit.

## Testes e verificações

Antes de abrir um Pull Request, verifique a configuração do projeto:

```powershell
.\venv\Scripts\python.exe manage.py check
```

Execute os testes:

```powershell
.\venv\Scripts\python.exe manage.py test
```

Também é recomendado verificar problemas de whitespace no diff:

```powershell
git diff --check
```

Os testes relevantes devem passar antes da abertura do Pull Request.

## Fluxo de desenvolvimento

1. Clone o repositório e configure o ambiente seguindo as instruções acima.

2. Antes de começar um novo trabalho, atualize a `main`:

   ```powershell
   git checkout main
   git pull origin main
   ```

3. Crie uma branch específica para a tarefa:

   ```powershell
   git checkout -b feature/nome-da-funcionalidade
   ```

4. Faça e teste suas alterações.

5. Confira os arquivos modificados:

   ```powershell
   git status
   ```

6. Adicione apenas os arquivos relacionados à alteração:

   ```powershell
   git add caminho/do/arquivo
   ```

7. Crie um commit com uma mensagem clara:

   ```powershell
   git commit -m "Descrição da alteração"
   ```

8. Envie a branch para o GitHub:

   ```powershell
   git push -u origin feature/nome-da-funcionalidade
   ```

9. Abra um Pull Request da sua branch para `main`.

10. Aguarde a revisão e a execução dos testes do Pull Request.

11. Após o merge, atualize novamente sua `main`:

   ```powershell
   git checkout main
   git pull origin main
   ```

Não faça alterações diretamente na `main`.

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

Ao instalar um pacote necessário ao projeto, adicione-o ao `requirements.txt`, teste a instalação e inclua essa alteração no commit.

[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue)](https://www.python.org/)
[![Django 5.0+](https://img.shields.io/badge/django-5.0+-green)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests Passing](https://github.com/pietrobrb/ExpotecIFCN-2026/actions/workflows/tests.yml/badge.svg)](https://github.com/pietrobrb/ExpotecIFCN-2026/actions)

Não substitua automaticamente o arquivo inteiro usando `pip freeze`, pois ele também pode listar pacotes sem relação com o projeto.
