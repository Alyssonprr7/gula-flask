"""Os 4 models do contrato (seção 3 do plano).

Nomes de classes, campos, relacionamentos e métodos fazem parte do contrato do
grupo. Não mude sem avisar o grupo.
"""
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login_manager

# Valores aceitos, para os forms usarem nos SelectField e validações.
DIFFICULTIES = ["fácil", "média", "difícil"]
CATEGORY_SLUGS = ["salgados", "doces", "bar"]


class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(256), nullable=False)
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.now)

    receitas = db.relationship("Receita", back_populates="autor", lazy="select")
    comentarios = db.relationship("Comentario", back_populates="autor", lazy="select")

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def checa_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self):
        return f"<Usuario {self.id} {self.email}>"


class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False, index=True)

    receitas = db.relationship("Receita", back_populates="categoria", lazy="select")

    def __repr__(self):
        return f"<Categoria {self.slug}>"


class Receita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    ingredientes = db.Column(db.Text, nullable=False)       # um por linha
    modo_preparo = db.Column(db.Text, nullable=False)
    tempo_min = db.Column(db.Integer, nullable=False)
    dificuldade = db.Column(db.String(10), nullable=False)  # um dos DIFFICULTIES
    imagem = db.Column(db.String(255))                      # caminho relativo a static/
    tags = db.Column(db.String(255), default="")            # separadas por vírgula
    categoria_id = db.Column(db.Integer, db.ForeignKey("categoria.id"), nullable=False)
    autor_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.now)

    autor = db.relationship("Usuario", back_populates="receitas")
    categoria = db.relationship("Categoria", back_populates="receitas")
    comentarios = db.relationship(
        "Comentario",
        back_populates="receita",
        cascade="all, delete-orphan",  # excluir a receita exclui os comentários
        order_by="Comentario.criado_em.desc()",
    )

    def __repr__(self):
        return f"<Receita {self.id} {self.titulo!r}>"


class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    nota = db.Column(db.Integer, nullable=False)  # 1 a 5
    receita_id = db.Column(db.Integer, db.ForeignKey("receita.id"), nullable=False)
    autor_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.now)

    receita = db.relationship("Receita", back_populates="comentarios")
    autor = db.relationship("Usuario", back_populates="comentarios")

    __table_args__ = (db.CheckConstraint("nota BETWEEN 1 AND 5", name="ck_rating_range"),)

    def __repr__(self):
        return f"<Comentario {self.id} nota={self.nota}>"


@login_manager.user_loader
def load_user(user_id):
    # Fica aqui (e não em auth/) porque o base.html usa current_user desde o
    # primeiro dia. A P2 não precisa escrever outro.
    return db.session.get(Usuario, int(user_id))
