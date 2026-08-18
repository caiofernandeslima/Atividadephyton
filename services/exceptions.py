"""Exceções de negócio compartilhadas pelos services.

Cada exceção carrega o código HTTP que o controller deve devolver,
mantendo os services livres de dependências do Flask.
"""


class RegraDeNegocioError(Exception):
    status_code = 400

    def __init__(self, mensagem):
        super().__init__(mensagem)
        self.mensagem = mensagem


class ValidacaoError(RegraDeNegocioError):
    """Dados inválidos enviados pelo cliente."""

    status_code = 400


class NaoEncontradoError(RegraDeNegocioError):
    """Recurso inexistente."""

    status_code = 404


class ConflitoError(RegraDeNegocioError):
    """Operação conflita com o estado atual dos dados (ex.: e-mail duplicado)."""

    status_code = 409
