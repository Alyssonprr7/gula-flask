import os
import tempfile
import unittest
from pathlib import Path

from app import create_app, db
from app.models import Categoria, Comentario, Receita, Usuario
from config import Config


class ComentariosTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        database_path = Path(self.temp_dir.name, "test.db").as_posix()

        class TestConfig(Config):
            TESTING = True
            SECRET_KEY = "test-key"
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{database_path}"
            LOG_DIR = os.path.join(self.temp_dir.name, "logs")
            UPLOAD_FOLDER = os.path.join(self.temp_dir.name, "uploads")
            WTF_CSRF_ENABLED = False

        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            categoria = Categoria(nome="Salgadas", slug="salgados")
            autor = Usuario(nome="Ana Cozinheira", email="ana@example.com")
            autor.set_senha("senha-ana")
            leitor = Usuario(nome="Bruno Leitor", email="bruno@example.com")
            leitor.set_senha("senha-bruno")
            db.session.add_all([categoria, autor, leitor])
            db.session.flush()

            receita = Receita(
                titulo="Moqueca de banana-da-terra",
                descricao="Dendê, leite de coco e banana madura na panela de barro.",
                ingredientes="4 bananas-da-terra maduras\n200 ml de leite de coco",
                modo_preparo="1. Doure as bananas.\n2. Cozinhe com leite de coco.",
                tempo_min=50,
                dificuldade="média",
                imagem="img/recipes/moqueca-banana.jpg",
                tags="stove,vegan",
                categoria=categoria,
                autor=autor,
            )
            db.session.add(receita)
            db.session.commit()

            self.autor_id = autor.id
            self.leitor_id = leitor.id
            self.receita_id = receita.id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.engine.dispose()
        for handler in self.app.logger.handlers:
            handler.close()
        self.app.logger.handlers.clear()
        self.temp_dir.cleanup()

    def _login_as(self, user_id):
        with self.client.session_transaction() as sess:
            sess["_user_id"] = str(user_id)
            sess["_fresh"] = True

    def test_detalhe_renders_recipe_details_and_empty_comments(self):
        response = self.client.get(f"/receitas/{self.receita_id}")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Moqueca de banana-da-terra", response.data)
        self.assertIn(b"4 bananas-da-terra maduras", response.data)
        self.assertIn(b"Doure as bananas.", response.data)
        self.assertNotIn(b"1. Doure as bananas.", response.data)
        self.assertIn(b"Ana Cozinheira", response.data)
        self.assertIn(b"Vegano", response.data)
        self.assertIn(b"Quer avaliar esta receita?", response.data)
        self.assertIn(b"Ainda n\xc3\xa3o h\xc3\xa1 coment\xc3\xa1rios nesta receita.", response.data)

    def test_detalhe_unknown_recipe_returns_404(self):
        response = self.client.get("/receitas/99999")
        self.assertEqual(response.status_code, 404)

    def test_post_comment_requires_login(self):
        response = self.client.post(
            f"/receitas/{self.receita_id}",
            data={"nota": "5", "texto": "Ficou excelente!"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])
        with self.app.app_context():
            self.assertEqual(Comentario.query.count(), 0)

    def test_authenticated_user_can_create_comment_and_update_average_rating(self):
        self._login_as(self.leitor_id)
        first = self.client.post(
            f"/receitas/{self.receita_id}",
            data={"nota": "5", "texto": "Ficou deliciosa, fiz com coentro fresco!"},
        )
        self.assertEqual(first.status_code, 302)
        self.assertTrue(first.headers["Location"].endswith(f"/receitas/{self.receita_id}#comentarios"))

        self._login_as(self.autor_id)
        second = self.client.post(
            f"/receitas/{self.receita_id}",
            data={"nota": "3", "texto": "Dica: use banana bem madura."},
        )
        self.assertEqual(second.status_code, 302)

        page = self.client.get(f"/receitas/{self.receita_id}")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"Ficou deliciosa, fiz com coentro fresco!", page.data)
        self.assertIn(b"Dica: use banana bem madura.", page.data)
        self.assertIn(b"Bruno Leitor", page.data)
        self.assertIn(b"4.0", page.data)
        self.assertIn(b"2 avalia\xc3\xa7\xc3\xb5es", page.data)

        with self.app.app_context():
            self.assertEqual(Comentario.query.count(), 2)

    def test_invalid_comment_is_rejected(self):
        self._login_as(self.leitor_id)

        empty_text = self.client.post(
            f"/receitas/{self.receita_id}",
            data={"nota": "4", "texto": "   "},
        )
        short_text = self.client.post(
            f"/receitas/{self.receita_id}",
            data={"nota": "4", "texto": "ok"},
        )
        bad_rating = self.client.post(
            f"/receitas/{self.receita_id}",
            data={"nota": "6", "texto": "Texto válido para testar nota inválida."},
        )

        self.assertEqual(empty_text.status_code, 200)
        self.assertIn(b"Escreva seu coment\xc3\xa1rio antes de publicar.", empty_text.data)
        self.assertEqual(short_text.status_code, 200)
        self.assertIn(b"entre 3 e 1000 caracteres", short_text.data)
        self.assertEqual(bad_rating.status_code, 200)

        with self.app.app_context():
            self.assertEqual(Comentario.query.count(), 0)

    def test_delete_comment_authorization_and_success(self):
        with self.app.app_context():
            comentario = Comentario(
                texto="Muito boa!",
                nota=5,
                receita_id=self.receita_id,
                autor_id=self.leitor_id,
            )
            db.session.add(comentario)
            db.session.commit()
            comentario_id = comentario.id

        # Anônimo -> redireciona para login
        anon_resp = self.client.post(f"/comentarios/{comentario_id}/excluir")
        self.assertEqual(anon_resp.status_code, 302)
        self.assertIn("/login", anon_resp.headers["Location"])

        # Outro usuário (mesmo sendo autor da receita) -> 403
        self._login_as(self.autor_id)
        forbidden_resp = self.client.post(f"/comentarios/{comentario_id}/excluir")
        self.assertEqual(forbidden_resp.status_code, 403)
        with self.app.app_context():
            self.assertIsNotNone(db.session.get(Comentario, comentario_id))

        # Autor do comentário -> exclui e redireciona
        self._login_as(self.leitor_id)
        delete_resp = self.client.post(f"/comentarios/{comentario_id}/excluir")
        self.assertEqual(delete_resp.status_code, 302)
        self.assertTrue(
            delete_resp.headers["Location"].endswith(f"/receitas/{self.receita_id}#comentarios")
        )
        with self.app.app_context():
            self.assertIsNone(db.session.get(Comentario, comentario_id))

        # Comentário inexistente -> 404
        missing_resp = self.client.post("/comentarios/99999/excluir")
        self.assertEqual(missing_resp.status_code, 404)

    def test_recipe_author_sees_edit_and_delete_controls(self):
        self._login_as(self.leitor_id)
        reader_page = self.client.get(f"/receitas/{self.receita_id}")
        self.assertNotIn(b"Editar receita", reader_page.data)
        self.assertNotIn(b"Excluir receita", reader_page.data)

        self._login_as(self.autor_id)
        author_page = self.client.get(f"/receitas/{self.receita_id}")
        self.assertIn(b"Editar receita", author_page.data)
        self.assertIn(b"Excluir receita", author_page.data)


class ComentariosCsrfTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        database_path = Path(self.temp_dir.name, "csrf.db").as_posix()

        class CsrfConfig(Config):
            TESTING = True
            SECRET_KEY = "csrf-secret"
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{database_path}"
            LOG_DIR = os.path.join(self.temp_dir.name, "logs_csrf")
            UPLOAD_FOLDER = os.path.join(self.temp_dir.name, "uploads_csrf")
            WTF_CSRF_ENABLED = True

        self.app = create_app(CsrfConfig)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            cat = Categoria(nome="Doces", slug="doces")
            user = Usuario(nome="Carla", email="carla@example.com")
            user.set_senha("123456")
            db.session.add_all([cat, user])
            db.session.flush()
            rec = Receita(
                titulo="Brigadeiro",
                descricao="Clássico.",
                ingredientes="Leite condensado",
                modo_preparo="Misture tudo.",
                tempo_min=20,
                dificuldade="fácil",
                categoria=cat,
                autor=user,
            )
            db.session.add(rec)
            db.session.commit()
            self.rec_id = rec.id
            self.user_id = user.id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.engine.dispose()
        for handler in self.app.logger.handlers:
            handler.close()
        self.app.logger.handlers.clear()
        self.temp_dir.cleanup()

    def test_csrf_protection_enforced_when_enabled(self):
        with self.client.session_transaction() as sess:
            sess["_user_id"] = str(self.user_id)
            sess["_fresh"] = True

        page = self.client.get(f"/receitas/{self.rec_id}")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b'name="csrf_token"', page.data)

        missing_token = self.client.post(
            f"/receitas/{self.rec_id}",
            data={"nota": "5", "texto": "Sem token CSRF"},
        )
        self.assertEqual(missing_token.status_code, 400)


if __name__ == "__main__":
    unittest.main()
