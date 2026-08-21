"""Script opcional para inserir dados de exemplo no banco.

Uso: python seed.py
"""

from app import app
from services import chamado_service, usuario_service
from services.exceptions import RegraDeNegocioError

USUARIOS = [
    {"nome": "Ana Souza", "email": "ana.souza@empresa.com", "setor": "TI"},
    {"nome": "Bruno Lima", "email": "bruno.lima@empresa.com", "setor": "Financeiro"},
    {"nome": "Carla Dias", "email": "carla.dias@empresa.com", "setor": "RH"},
]

CHAMADOS = [
    {
        "titulo": "Impressora do setor não imprime",
        "descricao": "A impressora do 2o andar exibe erro de comunicação ao enviar documentos.",
        "prioridade": "Alta",
        "tecnico": "Marcos",
        "usuario_indice": 0,
    },
    {
        "titulo": "Sistema de folha fora do ar",
        "descricao": "O sistema de folha de pagamento não carrega a tela de login desde ontem.",
        "prioridade": "Alta",
        "tecnico": "Juliana",
        "usuario_indice": 1,
    },
    {
        "titulo": "Solicitação de novo monitor",
        "descricao": "Necessário um monitor adicional para trabalho com planilhas extensas.",
        "prioridade": "Baixa",
        "tecnico": None,
        "usuario_indice": 2,
    },
    {
        "titulo": "Lentidão no acesso à rede",
        "descricao": "A conexão de rede do setor está muito lenta durante o período da tarde.",
        "prioridade": "Média",
        "tecnico": "Marcos",
        "usuario_indice": 0,
    },
]


def executar():
    with app.app_context():
        usuarios_existentes = usuario_service.listar_usuarios()

        if usuarios_existentes:
            print("Banco já possui dados. Nada foi inserido.")
            return

        usuarios = []
        for dados_usuario in USUARIOS:
            usuarios.append(usuario_service.criar_usuario(dados_usuario))

        for chamado in CHAMADOS:
            dados_chamado = {
                chave: valor
                for chave, valor in chamado.items()
                if chave != "usuario_indice"
            }

            indice_usuario = chamado["usuario_indice"]
            dados_chamado["usuario_id"] = usuarios[indice_usuario].id

            chamado_service.criar_chamado(dados_chamado)

        # Demonstra o fluxo de status: Aberto -> Em atendimento -> Encerrado
        try:
            chamado_service.iniciar_atendimento(1)
            chamado_service.iniciar_atendimento(2)
            chamado_service.encerrar_chamado(2)
        except RegraDeNegocioError as erro:
            print("Aviso:", erro.mensagem)

        print("Dados de exemplo inseridos com sucesso.")
        print("Estatísticas:", chamado_service.obter_estatisticas())


if __name__ == "__main__":
    executar()
