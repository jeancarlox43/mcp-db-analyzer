# 🗄️ MCP Database Analyzer

Un servidor MCP (Model Context Protocol) que se conecta a bases de datos, ejecuta queries, analiza los resultados y genera reportes en múltiples formatos: **texto**, **JSON** y **PowerPoint (PPTX)**.

## 🚀 Características

- ✅ Conexión a PostgreSQL (extensible a MySQL, SQLite, etc.)
- ✅ Ejecución segura de queries (solo SELECT)
- ✅ Análisis automático de queries y resultados
- ✅ Generación de insights inteligentes
- ✅ Exportación a múltiples formatos:
  - 📝 Texto legible
  - 📊 JSON estructurado
  - 📑 Presentaciones PowerPoint
- ✅ Containerizado con Docker
- ✅ Compatible con Claude Desktop, Cursor, y otros clientes MCP

## 📁 Estructura del Proyecto

```
mcp-db-analyzer/
├── src/
│   ├── __init__.py
│   ├── server.py           # MCP Server principal
│   ├── database.py         # Conexión a BD
│   ├── analyzer.py         # Análisis de queries
│   └── exporters/
│       ├── text_exporter.py
│       ├── json_exporter.py
│       └── pptx_exporter.py
├── scripts/
│   └── init-db.sql         # Datos de ejemplo
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🐳 Uso con Docker

### Inicio rápido

```bash
# Clonar el repositorio
git clone <repo-url>
cd mcp-db-analyzer

# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f mcp-db-analyzer
```

Esto levanta:
- **PostgreSQL** en puerto `5432` con datos de ejemplo
- **MCP Server (stdio)** para Claude Desktop
- **MCP Server (SSE)** en puerto `8000` para acceso remoto
- **Adminer** en `http://localhost:8080` para gestión visual de BD

### Conectar tu propia base de datos

```bash
# Crear archivo .env
cp .env.example .env

# Editar con tu connection string
DATABASE_URL=postgresql://user:password@host:5432/database

# Iniciar solo el MCP server
docker-compose up mcp-db-analyzer
```

## ⚙️ Configuración de Clientes MCP

### Claude Desktop

Editar `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) o `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "db-analyzer": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--network", "mcp-db-analyzer_mcp-network",
        "-e", "DATABASE_URL=postgresql://postgres:postgres@db:5432/analytics",
        "mcp-db-analyzer"
      ]
    }
  }
}
```

### Cursor IDE

Crear archivo `.cursor/mcp.json` en tu proyecto:

```json
{
  "mcpServers": {
    "db-analyzer": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "DATABASE_URL=postgresql://user:pass@host:5432/db",
        "mcp-db-analyzer"
      ]
    }
  }
}
```

### Conexión remota (SSE)

Para clientes que soportan SSE transport:

```json
{
  "mcpServers": {
    "db-analyzer": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

## 🛠️ Tools Disponibles

### `execute_query`
Ejecuta una query SQL y retorna resultados analizados.

```
Parámetros:
- query: string - Consulta SQL (solo SELECT)
- output_format: "text" | "json" | "pptx" (default: "text")
```

### `analyze_table`
Analiza una tabla completa: estructura, estadísticas y distribución.

```
Parámetros:
- table_name: string - Nombre de la tabla
- output_format: "text" | "json" | "pptx" (default: "text")
```

### `list_tables`
Lista todas las tablas disponibles.

### `get_table_schema`
Obtiene el esquema detallado de una tabla.

### `run_analysis_report`
Genera un reporte completo de la base de datos.

```
Parámetros:
- tables: string - Lista de tablas separadas por coma (vacío = todas)
- output_format: "text" | "json" | "pptx" (default: "pptx")
```

## 📝 Ejemplos de Uso

Una vez conectado, puedes pedirle al LLM:

```
"Lista las tablas de la base de datos"

"Ejecuta SELECT * FROM users WHERE status = 'active' y dame el resultado en JSON"

"Analiza la tabla orders y genera una presentación PowerPoint"

"Dame un reporte completo de la base de datos en formato PPTX"
```

## 🏗️ Desarrollo Local

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# o: .\venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
export DATABASE_URL="postgresql://user:pass@localhost:5432/db"
export OUTPUT_DIR="./outputs"

# Ejecutar servidor
python -m src.server
```

## 🔒 Seguridad

- Solo se permiten queries SELECT (lectura)
- Las conexiones a BD usan connection pooling
- Los archivos generados se almacenan en directorio configurable
- Se recomienda usar credenciales de solo lectura en producción

## 📦 Extensiones Futuras

- [ ] Soporte para MySQL, SQLite, SQL Server
- [ ] Generación de gráficos en presentaciones
- [ ] Exportación a Excel (.xlsx)
- [ ] Caché de queries frecuentes
- [ ] Autenticación para acceso remoto
- [ ] Dashboard web para visualización

## 📄 Licencia

MIT License
