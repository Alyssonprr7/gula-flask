# Gula em Flask

Revista digital de receitas do Trabalho 1 (capa, salgados, doces e bar), transformada em
uma aplicação Web dinâmica com **Flask**, **Jinja2**, **Flask-SQLAlchemy**, **Flask-WTF**,
**Flask-Login** e **python-dotenv**, contando com persistência em banco de dados, cadastro
de usuários, publicação de receitas, avaliações com comentários e registro de logs para debug.

## Sumário

1. [Preâmbulo](#preâmbulo)
2. [Como rodar localmente](#como-rodar-localmente)
3. [Organização dos arquivos](#organização-dos-arquivos)
4. [Guia do usuário](#guia-do-usuário)
5. [Testes automatizados](#testes-automatizados)
6. [Para quem desenvolve](#para-quem-desenvolve)

## Preâmbulo

- **Grupo:** Gula *(ajustar nome do grupo, se necessário)*
- **Aplicação:** Revista digital de receitas **Gula** (evolução dinâmica do site estático do Trabalho 1).
- **Requisitos atendidos:** mais de 5 rotas dinâmicas (11 rotas distribuídas em 4 blueprints), 4 models SQLAlchemy (`Usuario`, `Categoria`, `Receita`, `Comentario`), formulários com validação e proteção CSRF via Flask-WTF e log rotativo com nível configurável (`DEBUG`/`INFO`) em `logs/gula.log`.

### Integrantes e divisão de tarefas

| Parte | Responsável | Branch | Responsabilidades |
|---|---|---|---|
| **P1 · Fundação e deploy** | Alysson Rocha | `main` | Fábrica do app (`create_app`), configuração via `.env`, models SQLAlchemy, CSRF, Flask-Login, logging rotativo (`logs/gula.log`), páginas de erro (403, 404, 500), template `base.html`, estilos base e deploy no PythonAnywhere. |
| **P2 · Autenticação e perfil** | *(a preencher)* | `feat/auth` | Cadastro de usuários, login, logout e página de perfil com formulários Flask-WTF e controle de sessão. |
| **P3 · Catálogo, busca e seed** | Felipe G. Mello | `feat/catalogo` | Capa editorial (`/`), páginas de categoria (`/categoria/<slug>`), pesquisa por título e filtros por tag no servidor, script de carga inicial (`seed.py`) e testes do catálogo. |
| **P4 · Criar, editar e excluir receitas** | *(a preencher)* | `feat/receitas` | Formulário de criação e edição de receitas (`ReceitaForm`), upload de fotos em `app/static/uploads/` e exclusão com verificação de autoria. |
| **P5 · Página da receita, comentários e README** | Arthur Alexandrino | `feat/comentarios` | Página completa da receita (`/receitas/<id>`), formulário de comentários com avaliação de 1 a 5 estrelas (`ComentarioForm`), média de notas, exclusão de comentários com verificação de autoria (`/comentarios/<id>/excluir`), testes unitários e documentação no `README.md`. |

## Como rodar localmente

Requisitos: Python 3.10 ou mais novo. No Ubuntu/Debian, o `venv` precisa do pacote
`python3-venv` (ex.: `sudo apt install python3-venv`).

```bash
# 1. clonar e entrar na pasta
git clone <url-do-repositorio> gula-flask
cd gula-flask

# 2. criar e ativar o ambiente virtual
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. instalar as dependências
pip install -r requirements.txt

# 4. criar o .env a partir do exemplo e trocar a SECRET_KEY
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"   # cole o resultado em SECRET_KEY

# 5. criar o banco, carregar as receitas iniciais e rodar
flask init-db
python seed.py
flask run
```

O site abre em <http://127.0.0.1:5000>.

### Comandos úteis

| Comando | O que faz |
|---|---|
| `flask run` | Sobe o servidor de desenvolvimento (recarrega ao salvar). |
| `flask init-db` | Cria as tabelas do banco (`instance/gula.db`). |
| `flask init-db --drop` | Apaga todas as tabelas e cria de novo (**perde os dados**). |
| `python seed.py` | Cadastra as categorias e as receitas do Trabalho 1; pode ser repetido sem duplicar dados. |
| `python -m unittest discover -s tests` | Executa a suíte de testes automatizados. |

### Variáveis do `.env`

| Variável | Para que serve |
|---|---|
| `SECRET_KEY` | Assina a sessão de login e o token CSRF dos formulários. |
| `DATABASE_URL` | Endereço do banco. `sqlite:///gula.db` fica em `instance/gula.db`. |
| `UPLOAD_FOLDER` | Pasta das fotos enviadas pelos usuários. |
| `APP_ENV` | `development` (log em `DEBUG`) ou `production` (log em `INFO`). |
| `FLASK_DEBUG` | `1` liga o modo debug do Flask (apenas na máquina local). |

## Organização dos arquivos

A aplicação segue o padrão *Application Factory* (`create_app`) com divisão modular em
**Blueprints** por domínio funcional:

```text
gula-flask/
├── app/
│   ├── __init__.py                  # Fábrica create_app: SQLAlchemy, CSRF, LoginManager, logging, blueprints, erros e comando init-db (P1)
│   ├── models.py                    # Models SQLAlchemy: Usuario, Categoria, Receita e Comentario + user_loader (P1)
│   ├── auth/                        # Blueprint "auth": cadastro, login, logout e perfil (P2)
│   │   ├── __init__.py
│   │   ├── forms.py                 # Formulários de autenticação
│   │   └── routes.py                # /cadastro, /login, /logout, /perfil
│   ├── main/                        # Blueprint "main": capa editorial e catálogo por categoria (P3)
│   │   ├── __init__.py
│   │   └── routes.py                # / e /categoria/<slug> (busca ?q= e filtro ?tag=)
│   ├── receitas/                    # Blueprint "receitas": criação, edição e exclusão de receitas (P4)
│   │   ├── __init__.py
│   │   ├── forms.py                 # ReceitaForm (campos da receita e upload de foto)
│   │   └── routes.py                # /receitas/nova, /receitas/<id>/editar, /receitas/<id>/excluir
│   ├── comentarios/                 # Blueprint "comentarios": página da receita e comentários (P5)
│   │   ├── __init__.py
│   │   ├── forms.py                 # ComentarioForm (nota 1 a 5 e texto validado)
│   │   └── routes.py                # /receitas/<id> (GET/POST) e /comentarios/<id>/excluir (POST)
│   ├── templates/
│   │   ├── base.html                # Layout base: barra superior, navbar, mensagens flash e rodapé (P1)
│   │   ├── 403.html                 # Página de erro 403 (acesso negado) (P1)
│   │   ├── 404.html                 # Página de erro 404 (página não encontrada) (P1)
│   │   ├── 500.html                 # Página de erro 500 (erro interno) (P1)
│   │   ├── under_construction.html  # Página provisória usada durante o desenvolvimento das rotas (P1)
│   │   ├── auth/                    # Templates de cadastro, login e perfil (P2)
│   │   ├── main/                    # Templates da capa e das categorias (P3)
│   │   │   ├── index.html           # Capa editorial com prato em destaque e receitas recentes
│   │   │   ├── categoria.html       # Listagem por categoria com barra de busca e chips de filtro
│   │   │   └── _card_receita.html   # Partial reutilizável do cartão de receita
│   │   ├── receitas/                # Templates do formulário de receitas (P4)
│   │   └── comentarios/             # Templates da página da receita e comentários (P5)
│   │       └── detalhe.html         # Página completa da receita, ingredientes, preparo e seção de comentários
│   └── static/
│       ├── css/
│       │   ├── base.css             # Estilos base do Trabalho 1 (paleta, tipografia, navbar, cards e rodapé)
│       │   ├── style.css            # Estilos editoriais da capa do Trabalho 1
│       │   └── app.css              # Estilos da versão Flask (menu da conta, flash, página da receita e comentários)
│       ├── img/                     # Favicon, selos da UFF/IC e fotos das receitas iniciais (img/recipes/)
│       ├── js/                      # Scripts estáticos das páginas
│       └── uploads/                 # Fotos enviadas pelos usuários (ignoradas pelo Git, mantém apenas .gitkeep)
├── tests/
│   ├── test_catalogo.py             # Testes automatizados do catálogo, busca, filtros e seed (P3)
│   └── test_comentarios.py          # Testes da página da receita, comentários, permissões e CSRF (P5)
├── config.py                        # Classe Config: carrega variáveis do .env via python-dotenv (P1)
├── run.py                           # Ponto de entrada para `flask run` e WSGI do PythonAnywhere (P1)
├── seed.py                          # Popula o banco com categorias e as 21 receitas do Trabalho 1 (P3)
├── requirements.txt                 # Dependências Python fixadas com versão
├── .env.example                     # Modelo das variáveis de ambiente (o .env real não vai para o Git)
├── .flaskenv                        # Aponta FLASK_APP=run.py para a CLI do Flask
├── instance/gula.db                 # Banco SQLite gerado pelo `flask init-db` (fora do Git)
└── logs/gula.log                    # Arquivo de log rotativo gerado automaticamente (fora do Git)
```

### Detalhamento dos módulos

- **Fundação e banco de dados (`app/__init__.py`, `app/models.py`, `config.py`, `run.py`):**
  Define a fábrica `create_app`, inicializa `SQLAlchemy`, `CSRFProtect` e `LoginManager`,
  configura o log rotativo em `logs/gula.log` (até 1 MB por arquivo, 5 backups, nível `DEBUG`
  em desenvolvimento e `INFO` em produção) e registra os handlers de erro `403`, `404` e `500`.
  O banco possui 4 models relacionados:
  - `Usuario`: conta autenticável com senha em hash (`set_senha` / `checa_senha`), autor de receitas e comentários.
  - `Categoria`: seções fixas da revista (`salgados`, `doces`, `bar`).
  - `Receita`: título, descrição, ingredientes (um por linha), modo de preparo, tempo em minutos, dificuldade (`fácil`, `média`, `difícil`), imagem, tags separadas por vírgula, categoria e autor. Ao excluir uma receita, seus comentários são removidos em cascata.
  - `Comentario`: texto, nota inteira de `1` a `5` (validada no formulário e por `CheckConstraint` no banco), data de criação, receita e autor.

- **Autenticação e perfil (`app/auth/`):**
  Gerencia o ciclo de sessão dos usuários com Flask-Login nas rotas `/cadastro`, `/login`, `/logout` e `/perfil`.

- **Catálogo, busca e seed (`app/main/`, `seed.py`):**
  Expõe a capa (`/`) — destacando o prato de capa e as 3 receitas mais recentes — e as
  páginas de seção (`/categoria/<slug>`). Nas páginas de categoria, `?q=` pesquisa no título
  (ignorando acentos e maiúsculas/minúsculas) e `?tag=` filtra por tags inteiras ou pelo
  atalho `quick` (preparo até 30 minutos). O script `seed.py` cria as 3 categorias, o usuário
  editorial (`redacao@gula.local`) e as 21 receitas originais do Trabalho 1 de forma idempotente.

- **Gestão de receitas (`app/receitas/`):**
  Responsável pelas rotas `/receitas/nova`, `/receitas/<id>/editar` e `/receitas/<id>/excluir`,
  permitindo que usuários autenticados publiquem receitas com foto e gerenciem apenas as receitas
  de sua própria autoria.

- **Página da receita e comentários (`app/comentarios/`):**
  - `GET /receitas/<id>`: exibe a página completa da receita com foto, metadados (tempo,
    dificuldade, autor, data e média das avaliações), tags clicáveis para filtrar a categoria,
    lista formatada de ingredientes, modo de preparo numerado passo a passo e os comentários
    ordenados do mais recente ao mais antigo. Quando o usuário autenticado é o autor da receita,
    exibe os botões de edição e exclusão.
  - `POST /receitas/<id>`: recebe o `ComentarioForm` (nota de 1 a 5 estrelas e texto entre 3
    e 1000 caracteres com proteção CSRF). Apenas usuários autenticados podem publicar; visitantes
    anônimos são redirecionados para o login. Após salvar, aplica o padrão Post/Redirect/Get
    voltando para `#comentarios` com mensagem flash e registro em log.
  - `POST /comentarios/<id>/excluir`: protegido por `@login_required` e CSRF; verifica se o
    usuário autenticado é o autor do comentário (retornando `403` caso contrário), remove o
    registro do banco, registra o evento no log e redireciona de volta para a receita.

### Mapa de rotas da aplicação

| Método | Rota | Endpoint | Descrição |
|---|---|---|---|
| `GET` | `/` | `main.index` | Capa editorial da revista (destaque e receitas recentes). |
| `GET` | `/categoria/<slug>` | `main.categoria` | Listagem de receitas da categoria com busca (`?q=`) e filtro (`?tag=`). |
| `GET`, `POST` | `/receitas/<id>` | `comentarios.detalhe` | Página completa da receita e envio de novos comentários/avaliações. |
| `POST` | `/comentarios/<id>/excluir` | `comentarios.excluir` | Exclusão de um comentário pelo próprio autor. |
| `GET`, `POST` | `/receitas/nova` | `receitas.nova` | Publicação de uma nova receita (requer login). |
| `GET`, `POST` | `/receitas/<id>/editar` | `receitas.editar` | Edição de uma receita pelo próprio autor. |
| `POST` | `/receitas/<id>/excluir` | `receitas.excluir` | Exclusão de uma receita pelo próprio autor. |
| `GET`, `POST` | `/cadastro` | `auth.cadastro` | Cadastro de nova conta de usuário. |
| `GET`, `POST` | `/login` | `auth.login` | Autenticação de usuário existente. |
| `GET` | `/logout` | `auth.logout` | Encerramento da sessão autenticada. |
| `GET` | `/perfil` | `auth.perfil` | Perfil do usuário autenticado. |

## Guia do usuário

### 1. Navegar pela capa e pelas seções
- Ao abrir a página inicial (**Gula**), você encontra o **Prato de capa** em destaque e a seção **Nesta edição** com as receitas mais recentes.
- Para explorar por categoria, clique em **Receitas** na barra superior e escolha entre **Salgadas**, **Doces** ou **Drinks** (Bar).

### 2. Buscar e filtrar receitas
- Dentro de qualquer categoria (`/categoria/salgados`, `/categoria/doces` ou `/categoria/bar`), use a caixa **Buscar receita...** para pesquisar pelo título (a busca ignora acentos e letras maiúsculas/minúsculas).
- Clique nos filtros rápidos ao lado da busca (como *Rápida*, *Forno*, *Vegano*, *Gelados*, *Cítricos*, *Clássicos* ou *Sem álcool*) para refinar os resultados. Busca e filtro podem ser combinados; clique em **Tudo** para limpar o filtro de tag.

### 3. Ler uma receita completa
- Clique em **Ver a receita completa** (na capa) ou em qualquer cartão do catálogo para abrir a página da receita (`/receitas/<id>`).
- Nela você visualiza a foto do prato, o tempo de preparo, o nível de dificuldade, a nota média das avaliações, o autor, a data de publicação, a lista de **Ingredientes** e o **Modo de preparo** passo a passo.
- Clicar em qualquer tag da receita leva diretamente à categoria já filtrada por aquela tag.

### 4. Criar conta e fazer login
- Visitantes sem login podem navegar por todo o catálogo e ler todas as receitas e comentários.
- Para publicar receitas ou avaliar/comentar, clique em **Cadastrar** no menu superior para criar uma conta com nome, e-mail e senha, ou em **Entrar** caso já possua cadastro.
- Enquanto estiver conectado, o menu superior exibe **Nova receita**, seu primeiro nome (acesso ao **Perfil**) e **Sair**.

### 5. Publicar, editar e excluir receitas
- Com a conta autenticada, acesse **Nova receita** no menu superior para cadastrar uma nova receita informando título, descrição, categoria, tempo de preparo, dificuldade, ingredientes (um por linha), modo de preparo, tags e imagem.
- Ao abrir uma receita criada por você, os botões **Editar receita** e **Excluir receita** ficam disponíveis logo abaixo das informações do prato. Usuários que não são autores da receita não têm permissão para alterá-la ou excluí-la.

### 6. Avaliar e comentar receitas
- Role até a seção **Comentários e avaliações** na página da receita.
- Se estiver conectado, escolha uma nota de **1 a 5 estrelas**, escreva seu comentário (mínimo de 3 caracteres) e clique em **Publicar comentário**.
- O comentário aparece imediatamente no topo da lista e a média de avaliação da receita é atualizada automaticamente.
- Caso queira remover um comentário que você publicou, clique em **Excluir** no canto superior direito do seu próprio comentário e confirme a ação.

## Testes automatizados

Os testes usam banco SQLite temporário isolado e validam rotas, buscas, seed, persistência,
regras de permissão e proteção CSRF:

```bash
python -m unittest discover -s tests -v
```

## Para quem desenvolve

**Contrato.** Models, nomes de endpoints e blocos do `base.html` fazem parte do contrato
do grupo e não devem mudar sem aviso prévio. Sempre use `url_for('blueprint.endpoint', ...)`,
nunca caminhos escritos à mão.

**Templates.** Todo template começa com `{% extends "base.html" %}` e usa os blocos
`title`, `content` e `scripts`. O bloco opcional `section` (ou a variável `section`
passada no `render_template`) define o texto da seção que aparece na navbar.

**Mensagens flash.** Use as categorias do Bootstrap: `flash("...", "success")`,
`"info"`, `"warning"` ou `"danger"`.

**Log.** Cada parte registra os próprios eventos em `logs/gula.log`:

```python
from flask import current_app
current_app.logger.info("Receita %s criada pelo usuário %s", receita.id, current_user.id)
current_app.logger.warning("Usuário %s tentou editar a receita %s sem permissão", current_user.id, id)
current_app.logger.exception("Erro ao salvar o upload")   # dentro do except
```

Nunca registre senhas nos logs.

**Constantes prontas** em `app/models.py`: `DIFFICULTIES` (`fácil`, `média`, `difícil`) e
`CATEGORY_SLUGS` (`salgados`, `doces`, `bar`).

**Git.** Uma branch por pessoa, com Pull Request para a `main`. Antes de abrir o PR,
rode `git pull origin main` e confira se o app ainda sobe. Nunca commite `.env`,
`instance/`, `logs/`, `venv/` nem fotos de `static/uploads/` (o `.gitignore` já cuida disso).
