# Gula em Flask

Revista digital de receitas do Trabalho 1 (capa, salgados, doces e bar), agora como
aplicação Flask com banco de dados, cadastro de usuários, receitas e comentários.

> **P5:** este README é o ponto de partida. As seções marcadas com *(a completar)*
> são preenchidas com o texto de cada parte, conforme o plano do trabalho.

## Sumário

1. [Preâmbulo](#preâmbulo)
2. [Como rodar localmente](#como-rodar-localmente)
3. [Organização dos arquivos](#organização-dos-arquivos)
4. [Guia do usuário](#guia-do-usuário)
5. [Para quem desenvolve](#para-quem-desenvolve)

## Preâmbulo

*(a completar: nome do grupo, integrantes e divisão de tarefas)*

| Parte | Responsável | Branch |
|---|---|---|
| P1 · Fundação e deploy | | `main` |
| P2 · Autenticação e perfil | | `feat/auth` |
| P3 · Catálogo, busca e seed | | `feat/catalogo` |
| P4 · Criar, editar e excluir receitas | | `feat/receitas` |
| P5 · Página da receita, comentários e README | | `feat/comentarios` |

## Como rodar localmente

Requisitos: Python 3.10 ou mais novo. No Ubuntu/Debian, o venv precisa do pacote
`python3-venv` (`sudo apt install python3.10-venv`).

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

# 5. criar o banco e rodar
flask init-db
flask run
```

O site abre em <http://127.0.0.1:5000>.

### Comandos úteis

| Comando | O que faz |
|---|---|
| `flask run` | Sobe o servidor de desenvolvimento (recarrega ao salvar). |
| `flask init-db` | Cria as tabelas do banco (`instance/gula.db`). |
| `flask init-db --drop` | Apaga todas as tabelas e cria de novo (**perde os dados**). |
| `python seed.py` | Cadastra as receitas do Trabalho 1 *(P3, a completar)*. |

### Variáveis do `.env`

| Variável | Para que serve |
|---|---|
| `SECRET_KEY` | Assina a sessão de login e o token CSRF dos formulários. |
| `DATABASE_URL` | Endereço do banco. `sqlite:///gula.db` fica em `instance/gula.db`. |
| `UPLOAD_FOLDER` | Pasta das fotos enviadas pelos usuários. |
| `APP_ENV` | `development` (log em DEBUG) ou `production` (log em INFO). |
| `FLASK_DEBUG` | `1` liga o modo debug do Flask (só na máquina local). |

## Organização dos arquivos

```
app/
  __init__.py        create_app: banco, CSRF, login, logging, blueprints, erros, init-db   P1
  models.py          Usuario, Categoria, Receita, Comentario                               P1
  auth/              cadastro, login, logout e perfil (routes.py, forms.py)                P2
  main/              capa e páginas de categoria (routes.py)                               P3
  receitas/          criar, editar e excluir receitas (routes.py, forms.py)                P4
  comentarios/       página da receita e comentários (routes.py, forms.py)                 P5
  templates/
    base.html        header, menu, mensagens flash e footer de todas as páginas            P1
    403.html 404.html 500.html   páginas de erro                                           P1
    under_construction.html      página provisória das rotas ainda não feitas              P1
    auth/ main/ receitas/ comentarios/   templates de cada parte
  static/
    css/base.css     estilos comuns do Trabalho 1 (paleta, menu, cards, rodapé)
    css/style.css    estilos da capa do Trabalho 1
    css/app.css      estilos novos da versão Flask (menu da conta, mensagens flash)        P1
    img/             favicon, selos da UFF e fotos das receitas (img/recipes/)
    js/              scripts das páginas                                                   P3
    uploads/         fotos enviadas pelos usuários (fora do git)                           P4
config.py            configurações lidas do .env                                           P1
run.py               ponto de entrada (flask run / WSGI do PythonAnywhere)                 P1
requirements.txt     dependências
.env.example         modelo do .env (o .env real não vai para o git)
seed.py              receitas do Trabalho 1 para o banco                                   P3
logs/gula.log        log da aplicação, gerado automaticamente (fora do git)
instance/gula.db     banco SQLite, gerado pelo init-db (fora do git)
```

*(a completar: descrição de cada parte, com o texto enviado por cada pessoa)*

## Guia do usuário

*(a completar: como navegar, buscar, criar conta, publicar, editar, comentar, com prints)*

## Para quem desenvolve

**Contrato.** Models, nomes de endpoints e blocos do `base.html` estão na seção 3 do plano
e não mudam sem avisar o grupo. Sempre use `url_for('blueprint.endpoint', ...)`, nunca o
caminho escrito à mão.

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

Nunca registre senhas.

**Constantes prontas** em `app/models.py`: `DIFFICULTIES` (`fácil`, `média`, `difícil`) e
`CATEGORY_SLUGS` (`salgados`, `doces`, `bar`).

**Git.** Uma branch por pessoa, com Pull Request para a `main`. Antes de abrir o PR,
rode `git pull origin main` e confira se o app ainda sobe. Nunca commite `.env`,
`instance/`, `logs/`, `venv/` nem fotos de `static/uploads/` (o `.gitignore` já cuida disso).
