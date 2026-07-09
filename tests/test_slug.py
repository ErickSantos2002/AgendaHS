import re
from app.slug import gerar_slug


def test_slug_formato_e_tamanho():
    s = gerar_slug()
    assert len(s) == 8
    assert re.fullmatch(r"[A-Za-z0-9_-]+", s)


def test_slugs_diferentes():
    assert gerar_slug() != gerar_slug()
