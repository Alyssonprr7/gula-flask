"""Carrega as categorias e as receitas originais do Trabalho 1 no banco."""
import secrets

from app import create_app, db
from app.models import Categoria, Receita, Usuario

CATEGORIES = [
    {"nome": "Salgadas", "slug": "salgados"},
    {"nome": "Doces", "slug": "doces"},
    {"nome": "Bar", "slug": "bar"},
]

EDITORIAL_EMAIL = "redacao@gula.local"

RECIPES = [
    {
        "categoria": "salgados",
        "titulo": "Coxinha de frango",
        "descricao": "Massa cremosa recheada com frango desfiado e catupiry.",
        "tempo_min": 40,
        "dificuldade": "média",
        "imagem": "img/recipes/coxinha.jpg",
        "tags": "fried",
        "ingredientes": "2 xícaras de caldo de frango\n2 xícaras de farinha de trigo\n2 colheres de sopa de manteiga\n2 xícaras de frango cozido e desfiado\n4 colheres de sopa de requeijão\nFarinha de rosca e óleo para empanar e fritar",
        "modo_preparo": "1. Ferva o caldo com a manteiga e acrescente a farinha de uma vez, mexendo até formar uma massa que solte da panela.\n2. Espere amornar, abra porções da massa e recheie com frango e requeijão.\n3. Modele as coxinhas, passe em farinha de rosca e frite em óleo quente até dourarem.",
    },
    {
        "categoria": "salgados",
        "titulo": "Pão de queijo mineiro",
        "descricao": "Polvilho azedo, queijo canastra e casquinha que estala ao morder.",
        "tempo_min": 35,
        "dificuldade": "fácil",
        "imagem": "img/recipes/pao-de-queijo.jpg",
        "tags": "oven",
        "ingredientes": "500 g de polvilho azedo\n250 ml de leite\n100 ml de óleo\n2 ovos\n250 g de queijo meia-cura ralado\nSal a gosto",
        "modo_preparo": "1. Aqueça o leite com o óleo e despeje sobre o polvilho, misturando até amornar.\n2. Junte os ovos, o queijo e o sal; amasse até ficar homogêneo.\n3. Faça bolinhas e asse em forno preaquecido a 200 °C por cerca de 25 minutos.",
    },
    {
        "categoria": "salgados",
        "titulo": "Moqueca de banana-da-terra",
        "descricao": "Dendê, leite de coco e banana madura na panela de barro.",
        "tempo_min": 50,
        "dificuldade": "média",
        "imagem": "img/recipes/moqueca-banana.jpg",
        "tags": "stove,vegan",
        "ingredientes": "4 bananas-da-terra maduras\n1 cebola fatiada\n1 pimentão vermelho em tiras\n2 tomates picados\n200 ml de leite de coco\n2 colheres de sopa de azeite de dendê\nCoentro, sal e limão a gosto",
        "modo_preparo": "1. Corte as bananas no comprimento e doure-as dos dois lados em uma panela com um fio de azeite.\n2. Refogue a cebola, o pimentão e os tomates; tempere com sal e limão.\n3. Junte o leite de coco e o dendê, acomode as bananas e cozinhe tampado por 15 minutos. Finalize com coentro.",
    },
    {
        "categoria": "salgados",
        "titulo": "Bolinho de bacalhau da vovó",
        "descricao": "Batata bem seca, bacalhau desfiado e óleo no ponto certo.",
        "tempo_min": 40,
        "dificuldade": "média",
        "imagem": "img/recipes/bolinho-bacalhau.jpg",
        "tags": "fried",
        "ingredientes": "300 g de bacalhau dessalgado e desfiado\n500 g de batata\n1 ovo\n2 colheres de sopa de salsinha picada\nPimenta-do-reino a gosto\nÓleo para fritar",
        "modo_preparo": "1. Cozinhe as batatas, escorra bem e amasse ainda quentes.\n2. Misture a batata com o bacalhau, o ovo, a salsinha e a pimenta até obter uma massa firme.\n3. Modele os bolinhos com duas colheres e frite em óleo quente até ficarem dourados.",
    },
    {
        "categoria": "salgados",
        "titulo": "Escondidinho de carne-seca",
        "descricao": "Purê de mandioca gratinado por cima da carne-seca acebolada.",
        "tempo_min": 60,
        "dificuldade": "média",
        "imagem": "img/recipes/escondidinho.jpg",
        "tags": "oven",
        "ingredientes": "700 g de mandioca descascada\n500 g de carne-seca dessalgada e desfiada\n1 cebola fatiada\n2 colheres de sopa de manteiga\n1/2 xícara de leite\n100 g de queijo coalho ralado",
        "modo_preparo": "1. Cozinhe a mandioca até ficar macia e amasse com a manteiga e o leite.\n2. Refogue a cebola, acrescente a carne-seca e cozinhe por alguns minutos.\n3. Em um refratário, espalhe a carne, cubra com o purê e o queijo. Leve ao forno a 200 °C até gratinar.",
    },
    {
        "categoria": "salgados",
        "titulo": "Salada de grão-de-bico",
        "descricao": "Grão-de-bico, tomate, pepino e hortelã com limão e azeite.",
        "tempo_min": 15,
        "dificuldade": "fácil",
        "imagem": "img/recipes/salada-grao-de-bico.jpg",
        "tags": "raw,vegan",
        "ingredientes": "2 xícaras de grão-de-bico cozido\n1 tomate em cubos\n1 pepino em cubos\n1/4 de cebola roxa fatiada\nSuco de 1 limão\n2 colheres de sopa de azeite\nHortelã, sal e pimenta a gosto",
        "modo_preparo": "1. Coloque o grão-de-bico, o tomate, o pepino e a cebola em uma tigela.\n2. Tempere com o suco de limão, azeite, sal e pimenta.\n3. Misture a hortelã e sirva fria.",
    },
    {
        "categoria": "salgados",
        "titulo": "Legumes assados com ervas",
        "descricao": "Abóbora, cenoura e cebola roxa assadas com alecrim e tomilho.",
        "tempo_min": 30,
        "dificuldade": "fácil",
        "imagem": "img/recipes/legumes-assados.jpg",
        "tags": "oven,vegan",
        "ingredientes": "2 cenouras em pedaços\n300 g de abóbora em cubos\n1 cebola roxa em pétalas\n2 colheres de sopa de azeite\nAlecrim e tomilho a gosto\nSal e pimenta a gosto",
        "modo_preparo": "1. Aqueça o forno a 220 °C e distribua os legumes em uma assadeira.\n2. Regue com azeite, tempere com sal, pimenta, alecrim e tomilho.\n3. Asse por cerca de 30 minutos, virando os legumes na metade do tempo.",
    },
    {
        "categoria": "salgados",
        "titulo": "Empadão de palmito",
        "descricao": "Massa podre amanteigada e recheio cremoso de palmito com azeitona.",
        "tempo_min": 70,
        "dificuldade": "média",
        "imagem": "img/recipes/empadao-palmito.jpg",
        "tags": "oven",
        "ingredientes": "3 xícaras de farinha de trigo\n200 g de manteiga gelada\n1 ovo\n1 vidro de palmito picado\n1/2 cebola picada\n1/2 xícara de azeitonas\n1/2 xícara de leite\n1 gema para pincelar",
        "modo_preparo": "1. Misture a farinha com a manteiga e o ovo até formar uma massa; reserve na geladeira.\n2. Refogue a cebola, junte o palmito, as azeitonas e o leite; cozinhe até o recheio engrossar e deixe esfriar.\n3. Forre uma forma com parte da massa, coloque o recheio, cubra com o restante e pincele a gema. Asse a 180 °C até dourar.",
    },
    {
        "categoria": "salgados",
        "titulo": "Tapioca de queijo coalho",
        "descricao": "Goma hidratada na frigideira quente, queijo coalho e orégano.",
        "tempo_min": 10,
        "dificuldade": "fácil",
        "imagem": "img/recipes/tapioca.jpg",
        "tags": "stove",
        "ingredientes": "4 colheres de sopa de goma de tapioca\n80 g de queijo coalho ralado\nOrégano a gosto",
        "modo_preparo": "1. Espalhe a goma em uma frigideira antiaderente aquecida, formando um disco.\n2. Quando a tapioca firmar, distribua o queijo e o orégano sobre metade do disco.\n3. Dobre ao meio e aqueça até o queijo começar a derreter.",
    },
    {
        "categoria": "salgados",
        "titulo": "Feijoada vegana",
        "descricao": "Feijão preto, cogumelos defumados e linguiça de soja no caldo grosso.",
        "tempo_min": 90,
        "dificuldade": "média",
        "imagem": "img/recipes/feijoada-vegana.jpg",
        "tags": "stove,vegan",
        "ingredientes": "500 g de feijão-preto\n1 cebola picada\n2 dentes de alho\n200 g de cogumelos\n200 g de linguiça vegetal em rodelas\n2 folhas de louro\nAzeite, sal e cheiro-verde a gosto",
        "modo_preparo": "1. Deixe o feijão de molho, escorra e cozinhe com as folhas de louro até ficar macio.\n2. Refogue a cebola e o alho no azeite; doure os cogumelos e a linguiça vegetal.\n3. Junte o refogado ao feijão e cozinhe até o caldo encorpar. Acerte o sal e finalize com cheiro-verde.",
    },
    {
        "categoria": "salgados",
        "titulo": "Farofa de banana",
        "descricao": "Farinha de mandioca torrada no azeite com banana e cebola dourada.",
        "tempo_min": 20,
        "dificuldade": "fácil",
        "imagem": "img/recipes/farofa-banana.jpg",
        "tags": "stove,vegan",
        "ingredientes": "2 bananas maduras em rodelas\n1 cebola picada\n2 colheres de sopa de azeite\n2 xícaras de farinha de mandioca\nSal e salsinha a gosto",
        "modo_preparo": "1. Aqueça o azeite e doure a cebola.\n2. Acrescente as bananas e cozinhe até dourarem levemente.\n3. Junte a farinha aos poucos, mexendo até ficar crocante. Tempere com sal e salsinha.",
    },
    {
        "categoria": "salgados",
        "titulo": "Quiche de alho-poró",
        "descricao": "Creme de ovos e queijo gruyère sobre alho-poró refogado na manteiga.",
        "tempo_min": 55,
        "dificuldade": "média",
        "imagem": "img/recipes/quiche-alho-poro.jpg",
        "tags": "oven",
        "ingredientes": "1 massa para torta salgada\n2 talos de alho-poró fatiados\n1 colher de sopa de manteiga\n3 ovos\n200 ml de creme de leite\n100 g de queijo gruyère ralado\nSal e pimenta a gosto",
        "modo_preparo": "1. Refogue o alho-poró na manteiga até amaciar e espalhe sobre a massa em uma forma.\n2. Bata os ovos com o creme de leite, o queijo, o sal e a pimenta; despeje sobre o alho-poró.\n3. Asse a 180 °C por cerca de 35 minutos, até o recheio firmar e dourar.",
    },
    {
        "categoria": "doces",
        "titulo": "Bolo de fubá cremoso",
        "descricao": "Tudo no liquidificador, queijo ralado na massa e forno médio até a casquinha dourar sem rachar.",
        "tempo_min": 55,
        "dificuldade": "fácil",
        "imagem": "img/recipes/bolo-fuba.jpg",
        "tags": "oven",
        "ingredientes": "3 ovos\n2 xícaras de leite\n2 xícaras de açúcar\n1 xícara de fubá\n3 colheres de sopa de farinha de trigo\n2 colheres de sopa de manteiga\n50 g de queijo ralado\n1 colher de sopa de fermento",
        "modo_preparo": "1. Bata no liquidificador os ovos, o leite, o açúcar, o fubá, a farinha, a manteiga e o queijo.\n2. Misture o fermento delicadamente e despeje em uma forma untada.\n3. Asse em forno preaquecido a 180 °C por cerca de 45 minutos, até dourar.",
    },
    {
        "categoria": "doces",
        "titulo": "Pudim de leite sem furinhos",
        "descricao": "Bater devagar, assar em banho-maria e esperar a geladeira fazer o resto até o dia seguinte.",
        "tempo_min": 90,
        "dificuldade": "média",
        "imagem": "img/recipes/pudim-leite.jpg",
        "tags": "oven,cold",
        "ingredientes": "1 lata de leite condensado\nA mesma medida de leite\n3 ovos\n1 xícara de açúcar para a calda",
        "modo_preparo": "1. Derreta o açúcar em fogo baixo até formar um caramelo e espalhe em uma forma de pudim.\n2. Misture o leite condensado, o leite e os ovos sem incorporar muito ar; passe por uma peneira e despeje na forma.\n3. Asse em banho-maria a 160 °C por cerca de 1 hora e 30 minutos. Deixe esfriar e leve à geladeira antes de desenformar.",
    },
    {
        "categoria": "doces",
        "titulo": "Brigadeiro de colher",
        "descricao": "Ponto mais mole, manteiga no fim e cacau de verdade. Vai direto para a tigelinha.",
        "tempo_min": 20,
        "dificuldade": "fácil",
        "imagem": "img/recipes/brigadeiro.jpg",
        "tags": "stove",
        "ingredientes": "1 lata de leite condensado\n2 colheres de sopa de cacau em pó\n1 colher de sopa de manteiga\nGranulado para servir",
        "modo_preparo": "1. Misture o leite condensado e o cacau em uma panela.\n2. Cozinhe em fogo baixo, mexendo sempre, até engrossar mas continuar cremoso.\n3. Desligue o fogo, misture a manteiga e sirva em tigelinhas com granulado.",
    },
    {
        "categoria": "doces",
        "titulo": "Torta gelada de limão",
        "descricao": "Base de biscoito maisena, creme ácido na medida e raspas da casca por cima antes de servir.",
        "tempo_min": 30,
        "dificuldade": "fácil",
        "imagem": "img/recipes/torta-limao.jpg",
        "tags": "cold",
        "ingredientes": "200 g de biscoito maisena\n100 g de manteiga derretida\n1 lata de leite condensado\n1/2 xícara de suco de limão\n1 caixa de creme de leite\nRaspas de limão para finalizar",
        "modo_preparo": "1. Triture os biscoitos e misture com a manteiga; pressione no fundo de uma forma.\n2. Misture o leite condensado com o suco de limão e o creme de leite até formar um creme.\n3. Espalhe sobre a base, finalize com raspas e leve à geladeira até firmar.",
    },
    {
        "categoria": "bar",
        "titulo": "Caipirinha de tangerina",
        "descricao": "Tangerina macerada na medida, cachaça de alambique e gelo para um brinde perfumado.",
        "tempo_min": 5,
        "dificuldade": "fácil",
        "imagem": "img/recipes/caipirinha-tangerina.jpg",
        "tags": "citrico,classico",
        "ingredientes": "1 tangerina\n50 ml de cachaça\n2 colheres de chá de açúcar\nGelo a gosto",
        "modo_preparo": "1. Corte a tangerina em pedaços e retire as sementes.\n2. Coloque a fruta e o açúcar em um copo e macere suavemente.\n3. Acrescente a cachaça e o gelo, misture e sirva.",
    },
    {
        "categoria": "bar",
        "titulo": "Mojito",
        "descricao": "Rum branco, limão e hortelã fresca num drink leve, aromático e cheio de gelo.",
        "tempo_min": 7,
        "dificuldade": "fácil",
        "imagem": "img/recipes/mojito.jpg",
        "tags": "citrico,classico",
        "ingredientes": "50 ml de rum branco\n1/2 limão em pedaços\n1 colher de sopa de açúcar\n8 folhas de hortelã\nÁgua com gás e gelo a gosto",
        "modo_preparo": "1. Coloque o limão, o açúcar e a hortelã no copo e macere levemente.\n2. Encha o copo com gelo e acrescente o rum.\n3. Complete com água com gás, misture e decore com hortelã.",
    },
    {
        "categoria": "bar",
        "titulo": "Negroni",
        "descricao": "Partes iguais de gin, vermute tinto e bitter italiano, com laranja para perfumar.",
        "tempo_min": 5,
        "dificuldade": "fácil",
        "imagem": "img/recipes/negroni.jpg",
        "tags": "classico",
        "ingredientes": "30 ml de gin\n30 ml de vermute tinto\n30 ml de bitter italiano\nGelo\n1 rodela de laranja",
        "modo_preparo": "1. Coloque o gin, o vermute e o bitter em um copo baixo com gelo.\n2. Mexa até a bebida ficar bem gelada.\n3. Finalize com uma rodela de laranja.",
    },
    {
        "categoria": "bar",
        "titulo": "Clericot de frutas",
        "descricao": "Vinho branco bem gelado, frutas da estação e água com gás para servir à mesa.",
        "tempo_min": 15,
        "dificuldade": "fácil",
        "imagem": "img/recipes/clericot.jpg",
        "tags": "citrico",
        "ingredientes": "1 garrafa de vinho branco gelado\n1 maçã em cubos\n1 laranja em rodelas\n1 xícara de uvas cortadas\nÁgua com gás a gosto\nGelo",
        "modo_preparo": "1. Coloque as frutas em uma jarra e cubra com o vinho branco.\n2. Leve à geladeira por alguns minutos para as frutas aromatizarem a bebida.\n3. Acrescente gelo e água com gás antes de servir.",
    },
    {
        "categoria": "bar",
        "titulo": "Limonada rosa",
        "descricao": "Limão espremido, frutas vermelhas e água com gás: refrescante e sem álcool.",
        "tempo_min": 5,
        "dificuldade": "fácil",
        "imagem": "img/recipes/limonada-rosa.jpg",
        "tags": "citrico,sem-alcool",
        "ingredientes": "Suco de 2 limões\n1/2 xícara de frutas vermelhas\n500 ml de água com gás\nAçúcar ou mel a gosto\nGelo",
        "modo_preparo": "1. Amasse as frutas vermelhas e misture com o suco de limão.\n2. Adoce a gosto e divida em copos com gelo.\n3. Complete com água com gás e sirva imediatamente.",
    },
]


def seed_database():
    categories = {}
    for data in CATEGORIES:
        category = Categoria.query.filter_by(slug=data["slug"]).first()
        if category is None:
            category = Categoria(**data)
            db.session.add(category)
        categories[data["slug"]] = category

    editorial = Usuario.query.filter_by(email=EDITORIAL_EMAIL).first()
    if editorial is None:
        editorial = Usuario(
            nome="Redação Gula",
            email=EDITORIAL_EMAIL,
            senha_hash="",
        )
        editorial.set_senha(secrets.token_urlsafe(32))
        db.session.add(editorial)

    db.session.flush()
    added = 0
    for data in RECIPES:
        category = categories[data["categoria"]]
        exists = Receita.query.filter_by(
            categoria_id=category.id,
            titulo=data["titulo"],
        ).first()
        if exists is not None:
            continue

        recipe_data = {key: value for key, value in data.items() if key != "categoria"}
        db.session.add(
            Receita(
                **recipe_data,
                categoria=category,
                autor=editorial,
            )
        )
        added += 1

    db.session.commit()
    return added


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        count = seed_database()
        print(f"Seed concluído: {count} receita(s) adicionada(s).")
