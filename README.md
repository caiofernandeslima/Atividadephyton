# API HelpDesk

API REST para registro de chamados de suporte, desenvolvida em **Python + Flask + SQLAlchemy (SQLite)**
seguindo o padrão de **arquitetura em camadas**.

---

## Arquitetura

```
helpdesk/
├── controllers/                  # Recebem requisições e devolvem respostas HTTP
│   ├── usuario_controller.py
│   └── chamado_controller.py
│
├── services/                     # Regras de negócio e validações
│   ├── usuario_service.py
│   ├── chamado_service.py
│   └── exceptions.py             # Exceções de negócio com o código HTTP correspondente
│
├── repositories/                 # Consultas com SQLAlchemy (sem regra de negócio)
│   ├── usuario_repository.py
│   └── chamado_repository.py
│
├── models/                       # Entidades do banco de dados
│   ├── usuario.py
│   └── chamado.py
│
├── database.py                   # Configuração do SQLAlchemy e criação das tabelas
├── app.py                        # Ponto de entrada / registro dos blueprints
├── seed.py                       # Script opcional com dados de exemplo
├── requirements.txt
├── helpdesk.db                   # Banco SQLite gerado pela aplicação
└── README.md
```

### Responsabilidade de cada camada

| Camada | Responsabilidade |
|---|---|
| **Controller** | Recebe a requisição, valida o formato básico do corpo, chama o service e devolve o JSON com o status HTTP. |
| **Service** | Concentra todas as regras de negócio, validações e a coordenação dos repositórios. |
| **Repository** | Executa apenas as consultas e persistência com SQLAlchemy. |
| **Model** | Define somente as entidades e o relacionamento entre elas. |

O fluxo é sempre `Controller → Service → Repository → Model`. Os controllers nunca acessam
os repositórios diretamente, e os repositórios não conhecem regras de negócio.

---

## Como executar

### 1. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 2. Executar a aplicação

```bash
python app.py
```

A API ficará disponível em `http://127.0.0.1:5000`.
O arquivo `helpdesk.db` é criado automaticamente pela aplicação na primeira execução.

### 3. (Opcional) Popular o banco com dados de exemplo

```bash
python seed.py
```

---

## Entidades

### Usuário
| Campo | Tipo | Observação |
|---|---|---|
| id | inteiro | chave primária |
| nome | texto | obrigatório |
| email | texto | obrigatório e único |
| setor | texto | opcional |

### Chamado
| Campo | Tipo | Observação |
|---|---|---|
| id | inteiro | chave primária |
| titulo | texto | obrigatório, mínimo de 5 caracteres |
| descricao | texto | obrigatório, mínimo de 10 caracteres |
| prioridade | texto | `Baixa`, `Média` ou `Alta` |
| status | texto | `Aberto`, `Em atendimento` ou `Encerrado` |
| tecnico | texto | opcional |
| data_abertura | data/hora | preenchido automaticamente |
| usuario_id | inteiro | chave estrangeira, obrigatória |

**Relacionamento:** um usuário possui vários chamados; cada chamado pertence a um único usuário.

---

## Regras de negócio implementadas

### Usuários
- Nome é obrigatório.
- E-mail é obrigatório.
- Não é permitido cadastrar dois usuários com o mesmo e-mail.
- Não é permitido excluir um usuário que possua chamados cadastrados.

### Chamados
- Título obrigatório e com no mínimo 5 caracteres.
- Descrição com no mínimo 10 caracteres.
- O chamado deve estar vinculado a um usuário existente.
- Prioridade limitada a `Baixa`, `Média` ou `Alta`.
- O status inicial é sempre `Aberto` (não pode ser definido pelo cliente na criação).
- Um usuário não pode possuir mais de **5 chamados de prioridade Alta ainda não encerrados**.

### Transições de status

```
Aberto  →  Em atendimento  →  Encerrado
```

| Transição | Permitida |
|---|---|
| Aberto → Em atendimento | Sim |
| Em atendimento → Encerrado | Sim |
| Aberto → Encerrado | Não |
| Encerrado → Aberto | Não |
| Encerrado → Em atendimento | Não |

As mesmas regras valem tanto para os endpoints `PATCH` quanto para uma alteração de `status` via `PUT`.

---

## Endpoints

### Usuários
| Método | Rota | Descrição | Status de sucesso |
|---|---|---|---|
| GET | `/usuarios` | Lista todos os usuários | 200 |
| GET | `/usuarios/<id>` | Busca um usuário | 200 |
| POST | `/usuarios` | Cadastra um usuário | 201 |
| PUT | `/usuarios/<id>` | Atualiza um usuário | 200 |
| DELETE | `/usuarios/<id>` | Remove um usuário | 204 |
| GET | `/usuarios/<id>/chamados` | Lista os chamados do usuário | 200 |

### Chamados
| Método | Rota | Descrição | Status de sucesso |
|---|---|---|---|
| GET | `/chamados` | Lista todos os chamados | 200 |
| GET | `/chamados/<id>` | Busca um chamado | 200 |
| POST | `/chamados` | Cadastra um chamado | 201 |
| PUT | `/chamados/<id>` | Atualiza um chamado | 200 |
| DELETE | `/chamados/<id>` | Remove um chamado | 204 |
| PATCH | `/chamados/<id>/iniciar` | Altera o status para `Em atendimento` | 200 |
| PATCH | `/chamados/<id>/encerrar` | Altera o status para `Encerrado` | 200 |
| GET | `/chamados/abertos` | Lista apenas os chamados abertos | 200 |
| GET | `/chamados/prioridade/alta` | Lista os chamados de prioridade alta | 200 |

### Estatísticas
| Método | Rota | Descrição |
|---|---|---|
| GET | `/estatisticas` | Retorna os totais do sistema |

```json
{
  "usuarios": 15,
  "chamados": 48,
  "abertos": 10,
  "em_atendimento": 8,
  "encerrados": 30
}
```

---

## Códigos HTTP utilizados

| Código | Situação |
|---|---|
| 200 | Consulta ou atualização realizada com sucesso |
| 201 | Recurso criado |
| 204 | Recurso removido (sem conteúdo no corpo) |
| 400 | Dados inválidos (campo obrigatório ausente, tamanho mínimo, prioridade inválida, JSON malformado) |
| 404 | Recurso não encontrado |
| 409 | Conflito com o estado atual (e-mail duplicado, exclusão de usuário com chamados, transição de status inválida, limite de chamados Alta) |
| 500 | Erro interno |

Em caso de erro, a resposta segue o formato:

```json
{ "erro": "Mensagem explicando o problema." }
```

---

## Exemplos de requisição

### Cadastrar usuário
```bash
curl -X POST http://127.0.0.1:5000/usuarios -H "Content-Type: application/json" -d "{\"nome\":\"Ana Souza\",\"email\":\"ana@empresa.com\",\"setor\":\"TI\"}"
```

### Cadastrar chamado
```bash
curl -X POST http://127.0.0.1:5000/chamados -H "Content-Type: application/json" -d "{\"titulo\":\"Impressora com defeito\",\"descricao\":\"A impressora do setor nao esta imprimindo\",\"prioridade\":\"Alta\",\"usuario_id\":1}"
```

### Iniciar atendimento
```bash
curl -X PATCH http://127.0.0.1:5000/chamados/1/iniciar
```

### Encerrar chamado
```bash
curl -X PATCH http://127.0.0.1:5000/chamados/1/encerrar
```

### Consultar estatísticas
```bash
curl http://127.0.0.1:5000/estatisticas
```
