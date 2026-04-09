# Por que Agno em vez de LangChain / LangGraph

## Comparativo geral

| | Agno | LangChain / LangGraph |
|---|---|---|
| **Foco** | Agentes multi-modal com suporte nativo a MCP | Pipelines e grafos de agentes genéricos |
| **MCP nativo** | Sim — `MCPTools` built-in | Não nativo — requer integração manual |
| **Performance** | Leve, poucas camadas de abstração | Mais pesado, mais indireções |
| **Curva de aprendizado** | Menor | Maior, especialmente LangGraph |
| **Ecossistema** | Menor, mais novo | Muito maior, mais maduro |
| **Observabilidade** | Básica | LangSmith integrado |
| **Grafos de fluxo** | Não tem | LangGraph é especialista nisso |
| **Servidor de agente** | AgentOS incluso (FastAPI + sessões + DB) | Não incluso — montar manualmente |

---

## Por que Agno é a escolha certa para este projeto

### 1. MCP é o núcleo da arquitetura

A LiGiaPro se conecta aos agentes via protocolo MCP. No Agno, isso é suporte de primeira classe:

```python
from agno.tools.mcp import MCPTools

agent = Agent(
    tools=[
        MCPTools(url="http://mcp-job-opening:8001/mcp"),
        MCPTools(url="http://mcp-process-management:8002/mcp"),
    ]
)
```

No LangChain, MCP não é nativo. Seria necessário escrever um wrapper customizado para traduzir o protocolo MCP para o formato de tools do LangChain — código extra que precisa ser mantido e testado.

---

### 2. O padrão Magentic não é um grafo fixo

LangGraph foi projetado para fluxos **determinísticos e pré-definidos**: nó A → nó B → nó C, com condições explícitas entre cada transição. É ideal quando o plano de execução é conhecido antes da chamada.

O padrão Magentic usado pela LiGiaPro é o oposto: o orquestrador **constrói o plano em tempo real**, refinando o registro de tarefas à medida que coleta informações dos agentes. Não há um grafo fixo — o agente decide dinamicamente quais tools chamar e em que ordem.

Usar LangGraph aqui seria modelar um problema aberto como se fosse fechado, adicionando complexidade sem benefício.

---

### 3. AgentOS elimina infraestrutura boilerplate

O Agno entrega junto com o agente:

- Servidor FastAPI com endpoints de chat prontos
- Gerenciamento de sessões e histórico de conversas
- Integração com PostgreSQL para persistência
- Suporte a múltiplos agentes na mesma instância

```python
agent_os = AgentOS(
    agents=[recruitment_agent],
    db=PostgresDb(db_url=settings.database_url),
)
app = agent_os.get_app()
```

Com LangChain, tudo isso seria montado manualmente: servidor, rotas, controle de sessão, persistência. Mais código, mais superfície de bug.

---

### 4. Menos abstração, mais controle

LangChain acumula anos de camadas de compatibilidade. Isso tem custo: debugging mais difícil, comportamentos inesperados em versões, e dependências pesadas.

O Agno tem uma API mais direta. O que o agente faz é legível no código — não está enterrado em chains e runnables.

---

## Quando LangGraph faria sentido

LangGraph seria a escolha certa se o projeto tivesse fluxos **fixos e auditáveis**, por exemplo:

- Pipeline de onboarding com etapas obrigatórias em ordem
- Processo de aprovação com ramificações predefinidas (aprovado → etapa X, reprovado → etapa Y)
- Workflows regulatórios onde cada transição precisa ser rastreável

Para o agente de recrutamento com padrão Magentic — onde o plano é construído dinamicamente a partir da intenção do usuário — Agno com tools MCP é a arquitetura correta.
