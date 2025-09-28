# Como Testar MCP Server com Streaming

## 1. Configurar Ambiente

Crie um arquivo `.env` com configurações mínimas:

```env
# Configurações do Banco
DB__HOST=localhost
DB__PORT=5432
DB__DATABASE=test_db
DB__USER=test_user
DB__PASSWORD=test_password
DB__SCHEMA_NAME=test_schema

# Chave da Anthropic (necessária para chat)
ANTHROPIC_API_KEY=seu_api_key_aqui
```

## 2. Rodar o MCP Server

O servidor funciona no mesmo modo stdio, mas agora com capacidades de streaming:

```bash
# Opção 1: Diretamente
python mcp_server.py

# Opção 2: Com UV
uv run python mcp_server.py

# Opção 3: Via Makefile
make mcp
```

## 3. Testar com MCP Inspector

### Iniciar o Inspector:
```bash
# Terminal 1: Rodar o servidor MCP
make mcp

# Terminal 2: Rodar o inspector
make mcp-inspect
```

### Ou manualmente:
```bash
# Terminal 1: Servidor
uv run python mcp_server.py

# Terminal 2: Inspector  
npx @modelcontextprotocol/inspector python mcp_server.py
```

## 4. Testando as Funcionalidades

### 4.1 Upload de Dados CSV
```bash
# No MCP Inspector, use a tool:
Tool: upload_csv_data
Parameters:
- csv_content: "name,age,city\nJohn,25,NYC\nMary,30,LA\nBob,35,Chicago"
- table_name: "users"
- description: "User data for testing"
```

### 4.2 Chat Regular
```bash
Tool: chat_with_data  
Parameters:
- message: "Tell me about this dataset"
- thread_id: "test-1"
```

### 4.3 Chat com Streaming 🌟
```bash
Tool: chat_with_data_stream
Parameters:
- message: "Analyze the age distribution and find patterns"
- thread_id: "test-stream-1"  
- stream_thinking: false
```

### 4.4 Chat com Thinking Stream (Debug) 🔍
```bash
Tool: chat_with_data_stream
Parameters:
- message: "Find outliers in this data"
- thread_id: "test-debug-1"
- stream_thinking: true
```

## 5. Diferenças Entre Modos

### Chat Regular (`chat_with_data`):
- Retorna: `[TextContent("Complete response text")]`
- Comportamento: Espera resposta completa do LLM

### Chat Streaming (`chat_with_data_stream`):
- Retorna: `[TextContent("chunk1"), TextContent("chunk2"), TextContent("chunk3"), ...]`
- Comportamento: Coleta chunks do streaming do LangGraph

### Com Thinking Stream:
- Retorna: `[TextContent("[Thinking: reasoning]"), TextContent("response chunk1"), ...]`
- Comportamento: Inclui processo de raciocínio do AI

## 6. Exemplo de Teste Completo

1. **Upload dados:**
```csv
product,sales,region,month
Laptop,1500,North,Jan  
Phone,2000,South,Jan
Tablet,800,North,Feb
Laptop,1200,South,Feb
```

2. **Chat Streaming:**
"Compare sales performance between regions and identify trends"

3. **Observe a diferença:**
- Chat regular: Uma resposta completa
- Chat streaming: Múltiplos chunks mostrando construção da resposta

## 7. Debugging

Se o streaming não funcionar:

1. **Verificar logs do servidor:**
```bash
# Rodar com logs detalhados
LOGURU_LEVEL=DEBUG uv run python mcp_server.py
```

2. **Verificar .env:**
- ANTHROPIC_API_KEY deve estar configurada
- Configurações de DB (mesmo sendo fake para teste)

3. **Testar chat regular primeiro:**
- Se `chat_with_data` funciona mas `chat_with_data_stream` não, é problema específico de streaming
- Se ambos falham, é problema de configuração geral

## 8. Como Identificar Streaming Funcionando

### No MCP Inspector:
- **Streaming OFF**: Resposta única e longa
- **Streaming ON**: Lista de múltiplas TextContent entries

### Exemplo de Output Esperado:

**chat_with_data (regular):**
```json
[
  {
    "type": "text", 
    "text": "Based on the data analysis, I found that the North region has higher laptop sales while South region excels in phone sales..."
  }
]
```

**chat_with_data_stream (streaming):**
```json
[
  {"type": "text", "text": "Based on"},
  {"type": "text", "text": " the data"}, 
  {"type": "text", "text": " analysis,"},
  {"type": "text", "text": " I found"},
  {"type": "text", "text": " that the North region..."}
]
```

## 9. Próximos Passos

Depois de verificar que funciona:

1. **Integrar com Claude Desktop:** 
   - Adicionar ao `claude_desktop_config.json`
   - Testar streaming direto no Claude

2. **Usar em aplicações:**
   - Clients MCP podem processar chunks em tempo real
   - Melhor UX para análises longas