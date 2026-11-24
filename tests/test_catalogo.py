import os
import tempfile
import unittest
from pathlib import Path

from app import create_app, db
from app.models import Categoria, Receita, Usuario
from config import Config
from seed import seed_database


class CatalogoTest(unittest.TestCase):
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
            categories = {
                slug: Categoria(nome=name, slug=slug)
                for slug, name in [
                    ("salgados", "Salgadas"),
                    ("doces", "Doces"),
                    ("bar", "Bar"),
                ]
            }
            author = Usuario(nome="Leitor", email="leitor@example.com")
            author.set_senha("senha-teste")
            db.session.add_all([*categories.values(), author])
            db.session.flush()
            db.session.add_all(
                [
                    Receita(
                        titulo="Moqueca de banana-da-terra",
                        descricao="Dendê e leite de coco.",
                        ingredientes="Banana",
                        modo_preparo="Cozinhe.",
                        tempo_min=50,
                        dificuldade="média",
                        imagem="img/recipes/moqueca-banana.jpg",
                        tags="stove,vegan",
                        categoria=categories["salgados"],
                        autor=author,
                    ),
                    Receita(
                        titulo="Farofa de limão",
                        descricao="Farofa cítrica.",
                        ingredientes="Farinha",
                        modo_preparo="Toste.",
                        tempo_min=20,
                        dificuldade="fácil",
                        tags="vegan",
                        categoria=categories["salgados"],
                        autor=author,
                    ),
                    Receita(
                        titulo="Salada vegan-friendly",
                        descricao="Salada fresca.",
                        ingredientes="Folhas",
                        modo_preparo="Misture.",
                        tempo_min=10,
                        dificuldade="fácil",
                        tags="vegan-friendly",
                        categoria=categories["salgados"],
                        autor=author,
                    ),
                ]
            )
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.engine.dispose()
        for handler in self.app.logger.handlers:
            handler.close()
        self.app.logger.handlers.clear()
        self.temp_dir.cleanup()

    def test_home_and_category_render_database_recipes(self):
        home = self.client.get("/")
        category = self.client.get("/categoria/salgados")

        self.assertEqual(home.status_code, 200)
        self.assertIn(b"Moqueca de banana-da-terra", home.data)
        self.assertIn(b"Prato de capa", home.data)
        self.assertEqual(category.status_code, 200)
        self.assertIn(b"Salada vegan-friendly", category.data)
        self.assertIn(b'href="/receitas/', category.data)

    def test_search_ignores_accents_and_tag_filter_matches_whole_tags(self):
        response = self.client.get("/categoria/salgados?q=limao&tag=vegan")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Farofa de lim\xc3\xa3o", response.data)
        self.assertNotIn(b"Salada vegan-friendly", response.data)

    def test_empty_results_and_unknown_category(self):
        no_results = self.client.get("/categoria/doces?q=nao-existe")
        unknown = self.client.get("/categoria/inexistente")

        self.assertEqual(no_results.status_code, 200)
        self.assertIn(b"Nenhuma receita encontrada.", no_results.data)
        self.assertEqual(unknown.status_code, 404)

    def test_seed_can_be_repeated_without_duplicating_recipes(self):
        with self.app.app_context():
            first_added = seed_database()
            second_added = seed_database()
            recipe_count = Receita.query.count()
            category_count = Categoria.query.count()
            editorial_count = Usuario.query.filter_by(email="redacao@gula.local").count()

        self.assertEqual(first_added, 20)
        self.assertEqual(second_added, 0)
        self.assertEqual(recipe_count, 23)
        self.assertEqual(category_count, 3)
        self.assertEqual(editorial_count, 1)


if __name__ == "__main__":
    unittest.main()
