# Sistema de Gerenciamento da Expotec/SPP 2024

## Integração com o SUAP

- Acesse: https://suap.ifrn.edu.br/admin/api/aplicacaooauth2/ (precisa estar logado)
- Clique em "Adicionar Aplicação OAUTH2" e insira os seguintes dados:
    - Name (o nome que aparecerá para o usuário na hora do login)
    - Authorization grant type: Authorization code
    - Redirect URIs: http://127.0.0.1:8000/accounts/suap/login/callback/ e http://localhost:8000/accounts/suap/login/callback/ (coloca em linhas diferentes)
    - Client type: Confidential
    - O resto deixa o padrão
- Anote o *Client id* e o *Client secret* que serão gerados, o *Client secret* não poderá mais ser visualizado.

## Setup do projeto

Para executar o projeto primeiro copie `.env.exemplo` para `.env` fazendo as alterações necessárias.

Crie e ative o venv:
```
python -m venv venv
.\venv\Scrips\activate
```

Instale as dependências com:
```sh
pip install -r requirements.txt
```

Crie o BD/faça as migrações:
```sh
python manage.py migrate
```

Carregue o DUMP da base
```sh
python manage.py loaddata config/fixtures/initial.json
```

Para atualizar o DUMP da base
```sh
python -Xutf8 manage.py dumpdata auth.group usuarios eventos atividades documentos enderecos portal  --natural-primary --natural-foreign --output=config/fixtures/initial.json
```


## Fluxo de desenvolvimento
1. Inicie com o clone do repositório
2. Se o repositório já existir no seu computador, faça um `git pull` para atualizar o repositório local com as alterações do Github. Resolva os conflitos, se houver.
3. Faça suas alterações e faça commits sempre que alguma funcionalidade, correção de erro ou refatoração de código for realizada. Só adicione os arquivos que tem relação com o propósito inicial do commit, mantendo as mensagens curtas e claras sobre o que foi feito.
4. Após os commits realizados localmente, sincronize o projeto com `git pull` e na sequência o `git push` para enviar para o Github.
5. Sempre que for trabalhar no projeto, inicie pelo passo 2.

Nunca deixe seu repositório "sujo" com alterações que não foram commitadas.

O fluxo final do projeto será o do Github [link](https://docs.github.com/pt/get-started/using-github/github-flow)

## Estilo
Sigam o [PEP8](https://peps.python.org/pep-0008/) e o [Coding Sytle Guide](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/) do Django.

### Resumo:
- Nomes de classes e modelos devem usar PascalCase
- Nomes de modelos devem ser no singular
- Nomes de métodos e funções devem ser minúsculos e usar `_` como separador (*snake_case*). Ex.: `pagina_inicial`
- Evite espaços vazios (mais de um Enter, mais de um espaço, etc), exceto entre funções e classes, onde são utilizados 2 linhas de espaçamento.
- A indentação do Python é com 4 espaços e do HTML/CSS/JS é com 2 espaços.
- Remova includes e imports desnecessários.

## Dependências
Sempre que algum novo pacote for instalado (`pip install pacote`) atualize o `requirements.txt` com:

```
pip freeze > requirements.txt
```

Faça o commit da alteração informando o pacote que foi adicionado.
