"""Exceções utilizadas nas regras de negócio da aplicação.

Cada tipo de erro possui um código HTTP correspondente.
"""


class RegraDeNegocioError(Exception):
    status_code = 400

    def __init__(self, mensagem):
        self.mensagem = mensagem
        super().__init__(mensagem)


class ValidacaoError(RegraDeNegocioError):
    """Erro utilizado quando os dados recebidos são inválidos."""

    status_code = 400


class NaoEncontradoError(RegraDeNegocioError):
    """Erro utilizado quando um registro não é encontrado."""

    status_code = 404


class ConflitoError(RegraDeNegocioError):
    """Erro utilizado quando uma operação gera conflito com os dados existentes."""

    status_code = 409
