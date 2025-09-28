# Guia de Testes - FastMCP 2.0 SQL Agent

Este guia explica como testar o Snapture SQL Agent com FastMCP 2.0, incluindo as novas capacidades HTTP nativas.

## ✨ Novidades do FastMCP 2.0

- 🌐 **HTTP nativo**: Suporte completo para HTTP sem fallbacks
- 🚀 **Decorators simplificados**: `@mcp.tool` ao invés de classes complexas  
- 📝 **Type hints automáticos**: Esquemas JSON gerados automaticamente
- 🔧 **FastMCP CLI**: Ferramentas de linha de comando integradas
- 🎯 **Melhor performance**: Arquitetura otimizada para produção

## 🛠️ Pré-requisitos

```bash
# Instalar dependências (inclui FastMCP 2.12.4)
uv sync

# Verificar instalação do FastMCP
uv run fastmcp version

# Resultado esperado:
# FastMCP version: 2.12.4
# MCP version: 1.15.0
```

## 🎯 Ferramentas Disponíveis

O servidor MCP fornece estas ferramentas:

1. **execute_sql_query** - Execute consultas SQL contra dados carregados
2. **upload_csv_data** - Carregue dados CSV diretamente 
3. **upload_csv_from_url** - Carregue CSV de uma URL
4. **get_database_schema** - Visualize esquema do banco
5. **chat_with_data** - Chat conversacional com dados
6. **chat_with_data_stream** - Chat com streaming (chunks)

## 🖥️ Modo STDIO (Integração MCP)

### Usando Python diretamente:
```bash
# Método tradicional
uv run python mcp_server.py

# Resultado esperado: Interface FastMCP bonita com logo ASCII
```

### Usando FastMCP CLI:
```bash
# Recomendado para produção  
uv run fastmcp run mcp_server.py:mcp --transport stdio

# Via Makefile
make mcp-cli-stdio
```

## 🌐 Modo HTTP (Interface Web)

### Usando Python diretamente:
```bash
# HTTP na porta padrão (3000)
uv run python mcp_server.py --http

# HTTP em porta customizada
uv run python mcp_server.py --http --port 8080

# HTTP acessível externamente
uv run python mcp_server.py --http --host 0.0.0.0 --port 9000
```

### Usando FastMCP CLI:
```bash
# CLI com HTTP
uv run fastmcp run mcp_server.py:mcp --transport http --port 8080

# Via Makefile
make mcp-cli-http
```

### URLs de Acesso HTTP:
- Servidor local: `http://localhost:3000/mcp`
- Porta customizada: `http://localhost:8080/mcp`
- Acesso externo: `http://YOUR_IP:PORT/mcp`

## 🔍 Testando com MCP Inspector

### Instalação e Uso:
```bash
# Via Makefile (recomendado)
make mcp-inspect

# Manualmente
npx @modelcontextprotocol/inspector ./run_mcp_server.sh
```

### Workflow de Teste Completo:

1. **Inicie o servidor** (escolha um método):
   ```bash
   make mcp                    # STDIO
   make mcp-http              # HTTP porta 3000  
   make mcp-http-port         # HTTP porta 8080
   ```

2. **Abra outro terminal** e execute:
   ```bash
   make mcp-inspect
   ```

3. **No MCP Inspector**, teste as ferramentas:

   **Upload de dados CSV:**
   ```json
   {
     "tool": "upload_csv_data",
     "arguments": {
       "csv_content": "name,age,city\\nJohn,30,NYC\\nJane,25,LA",
       "table_name": "users",  
       "description": "User data sample"
     }
   }
   ```

   **Consulta SQL:**
   ```json
   {
     "tool": "execute_sql_query",
     "arguments": {
       "query": "SELECT * FROM users WHERE age > 25",
       "purpose": "final"
     }
   }
   ```

   **Chat com dados:**
   ```json
   {
     "tool": "chat_with_data",
     "arguments": {
       "question": "Quantos usuários temos e qual a idade média?"
     }
   }
   ```

   **Chat com streaming:**
   ```json
   {
     "tool": "chat_with_data_stream", 
     "arguments": {
       "question": "Análise detalhada dos dados por cidade",
       "include_thinking": true
     }
   }
   ```

## 🧪 Testes de Desenvolvimento

### Verificar ferramentas disponíveis:
```bash
make mcp-list-tools
```

### Testar diferentes transportes:
```bash
# STDIO + HTTP em paralelo
make mcp &          # Terminal 1
make mcp-http &     # Terminal 2  
```

### Debug e logs:
```bash
# Servidor com logs verbose
LOGURU_LEVEL=DEBUG make mcp

# FastMCP CLI com debug
uv run fastmcp run mcp_server.py:mcp --transport stdio --verbose
```

## 🎮 Exemplos Práticos

### 1. Upload e análise de vendas:
```bash
# 1. Inicie o servidor HTTP
make mcp-http

# 2. No browser, vá para http://localhost:3000/mcp

# 3. Use upload_csv_from_url:
{
  "url": "https://raw.githubusercontent.com/datasets/sample-data/main/sales.csv",
  "table_name": "sales",
  "description": "Sample sales data"  
}

# 4. Chat sobre os dados:
"Quais são os produtos mais vendidos este mês?"
```

### 2. Análise streaming com thinking:
```json
{
  "tool": "chat_with_data_stream",
  "arguments": {
    "question": "Faça uma análise completa dos padrões de venda",
    "include_thinking": true
  }
}
```

## 📚 Comandos Úteis do Makefile

```bash
# Básicos
make mcp                # Servidor STDIO  
make mcp-http          # Servidor HTTP
make mcp-help          # Ajuda do servidor
make mcp-version       # Versão FastMCP

# FastMCP CLI
make mcp-cli-stdio     # CLI STDIO
make mcp-cli-http      # CLI HTTP  

# Testes
make mcp-inspect       # MCP Inspector
make mcp-list-tools    # Listar ferramentas

# Qualidade
make lint              # Linting
make format            # Formatação
make mypy             # Type checking
make all              # Todos os checks
```

## 🐛 Troubleshooting

### Erro "Cannot import FastMCP":
```bash
# Reinstalar dependências
uv sync --reinstall
uv add fastmcp  # Se necessário
```

### HTTP não conecta:
```bash
# Verificar se porta está livre
netstat -an | grep :3000

# Tentar porta diferente
make mcp-http-port  # usa porta 8080
```

### Problemas com MCP Inspector:
```bash
# Atualizar inspector
npm install -g @modelcontextprotocol/inspector@latest

# Verificar se run_mcp_server.sh existe
ls -la run_mcp_server.sh
```

### Logs de debug:
```bash
# Ativar logs detalhados
LOGURU_LEVEL=DEBUG make mcp

# Ver apenas erros
LOGURU_LEVEL=ERROR make mcp-http
```

## 🚀 Deploy e Produção

### FastMCP Cloud (Recomendado):
1. Suba código para GitHub
2. Conecte em https://fastmcp.cloud/
3. Configure `mcp_server.py:mcp` como entrypoint
4. Deploy automático com HTTPS

### Docker:
```bash
# Build e run
make docker_build
make docker_run

# Logs
make docker_logs
```

### Claude Desktop Integration:
```json
// claude_desktop_config.json
{
  "mcpServers": {
    "snapture-sql-agent": {
      "command": "python", 
      "args": ["/absolute/path/to/mcp_server.py"]
    }
  }
}
```

---

**🎉 Agora você tem um MCP Server moderno com FastMCP 2.0!**

- HTTP nativo ✅
- Streaming de chat ✅  
- Type safety ✅
- Performance otimizada ✅