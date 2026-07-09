import secrets
import string

_ALFABETO = string.ascii_letters + string.digits + "-_"


def gerar_slug(n=8):
    return "".join(secrets.choice(_ALFABETO) for _ in range(n))
