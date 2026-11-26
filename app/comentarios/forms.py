"""ComentarioForm. Dono: P5."""
from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange

RATING_CHOICES = [
    (5, "5 estrelas — Excelente"),
    (4, "4 estrelas — Muito boa"),
    (3, "3 estrelas — Boa"),
    (2, "2 estrelas — Regular"),
    (1, "1 estrela — Ruim"),
]


def _strip_text(value):
    return value.strip() if isinstance(value, str) else value


class ComentarioForm(FlaskForm):
    nota = RadioField(
        "Sua avaliação",
        choices=RATING_CHOICES,
        coerce=int,
        default=5,
        validators=[
            InputRequired(message="Escolha uma nota de 1 a 5."),
            NumberRange(min=1, max=5, message="A nota deve ser entre 1 e 5."),
        ],
    )
    texto = TextAreaField(
        "Seu comentário",
        filters=[_strip_text],
        validators=[
            DataRequired(message="Escreva seu comentário antes de publicar."),
            Length(
                min=3,
                max=1000,
                message="O comentário deve ter entre 3 e 1000 caracteres.",
            ),
        ],
    )
    submit = SubmitField("Publicar comentário")
