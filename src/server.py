"""
MCP Server para análisis de base de datos con múltiples formatos de salida.
Soporta: texto, JSON, PPTX
"""
import argparse
import asyncio
import json
import os
import sys
from typing import Any

from mcp.server.fastmcp import FastMCP, Context

from .database import DatabaseConnection
from .analyzer import QueryAnalyzer
from .exporters.text_exporter import export_to_text
from .exporters.json_exporter import export_to_json
from .exporters.pptx_exporter import export_to_pptx

# Configuración
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/app/outputs")

# Inicializar el servidor MCP
mcp = FastMCP(
    "Database Analyzer",
    description="MCP Server para análisis de base de datos con salida en texto, JSON y PPTX"
)

# Instancias globales (se inicializan con lifespan)
db: DatabaseConnection = None
analyzer: QueryAnalyzer = None


@mcp.tool()
async def execute_query(
    query: str,
    output_format: str = "text",
    ctx: Context = None
) -> str:
    """
    Ejecuta una query SQL y devuelve los resultados analizados.
    
    Args:
        query: Consulta SQL a ejecutar (solo SELECT para seguridad)
        output_format: Formato de salida - "text", "json", o "pptx"
    
    Returns:
        Resultados en el formato especificado con análisis incluido
    """
    global db, analyzer
    
    if db is None:
        db = DatabaseConnection()
        analyzer = QueryAnalyzer()
    
    # Validar que sea SELECT (seguridad básica)
    query_upper = query.strip().upper()
    if not query_upper.startswith("SELECT"):
        return "Error: Solo se permiten consultas SELECT por seguridad."
    
    try:
        # Ejecutar la query
        results = await db.execute(query)
        
        # Analizar la query y resultados
        analysis = analyzer.analyze(query, results)
        
        # Exportar según el formato solicitado
        if output_format.lower() == "json":
            return export_to_json(results, analysis)
        elif output_format.lower() == "pptx":
            filepath = export_to_pptx(results, analysis, OUTPUT_DIR)
            return f"✅ Presentación generada exitosamente:\n📁 {filepath}"
        else:
            return export_to_text(results, analysis)
            
    except Exception as e:
        return f"❌ Error ejecutando query: {str(e)}"


@mcp.tool()
async def analyze_table(
    table_name: str,
    output_format: str = "text"
) -> str:
    """
    Analiza una tabla completa: estructura, estadísticas y distribución de datos.
    
    Args:
        table_name: Nombre de la tabla a analizar
        output_format: Formato de salida - "text", "json", o "pptx"
    
    Returns:
        Análisis completo de la tabla en el formato especificado
    """
    global db, analyzer
    
    if db is None:
        db = DatabaseConnection()
        analyzer = QueryAnalyzer()
    
    try:
        # Obtener información de la tabla
        structure = await db.get_table_structure(table_name)
        stats = await db.get_table_stats(table_name)
        distribution = await db.get_column_distributions(table_name)
        
        # Obtener muestra de datos
        sample_data = await db.execute(f"SELECT * FROM {table_name} LIMIT 5")
        
        analysis_data = {
            "table_name": table_name,
            "structure": structure,
            "statistics": stats,
            "distribution": distribution,
            "sample_data": sample_data
        }
        
        analysis_meta = {
            "type": "table_analysis",
            "insights": _generate_table_insights(structure, stats, distribution)
        }
        
        if output_format.lower() == "json":
            return export_to_json(analysis_data, analysis_meta)
        elif output_format.lower() == "pptx":
            filepath = export_to_pptx(analysis_data, analysis_meta, OUTPUT_DIR)
            return f"✅ Presentación generada:\n📁 {filepath}"
        else:
            return export_to_text(analysis_data, analysis_meta)
            
    except Exception as e:
        return f"❌ Error analizando tabla: {str(e)}"


@mcp.tool()
async def list_tables() -> str:
    """
    Lista todas las tablas disponibles en la base de datos.
    
    Returns:
        Lista de tablas en formato JSON
    """
    global db
    
    if db is None:
        db = DatabaseConnection()
    
    try:
        tables = await db.get_tables()
        return json.dumps({
            "tables": tables,
            "count": len(tables)
        }, indent=2)
    except Exception as e:
        return f"❌ Error listando tablas: {str(e)}"


@mcp.tool()
async def get_table_schema(table_name: str) -> str:
    """
    Obtiene el esquema detallado de una tabla específica.
    
    Args:
        table_name: Nombre de la tabla
    
    Returns:
        Esquema de la tabla en formato JSON
    """
    global db
    
    if db is None:
        db = DatabaseConnection()
    
    try:
        schema = await db.get_table_structure(table_name)
        return json.dumps(schema, indent=2, default=str)
    except Exception as e:
        return f"❌ Error obteniendo esquema: {str(e)}"


@mcp.tool()
async def run_analysis_report(
    tables: str = "",
    output_format: str = "pptx"
) -> str:
    """
    Genera un reporte completo de análisis de la base de datos.
    
    Args:
        tables: Lista de tablas separadas por coma (vacío = todas)
        output_format: Formato de salida - "text", "json", o "pptx"
    
    Returns:
        Reporte completo en el formato especificado
    """
    global db, analyzer
    
    if db is None:
        db = DatabaseConnection()
        analyzer = QueryAnalyzer()
    
    try:
        # Obtener lista de tablas
        if tables:
            table_list = [t.strip() for t in tables.split(",")]
        else:
            table_list = await db.get_tables()
        
        report_data = {
            "database_overview": {
                "total_tables": len(table_list),
                "tables": table_list
            },
            "table_analyses": []
        }
        
        # Analizar cada tabla
        for table in table_list[:10]:  # Limitar a 10 tablas
            try:
                structure = await db.get_table_structure(table)
                stats = await db.get_table_stats(table)
                report_data["table_analyses"].append({
                    "table_name": table,
                    "columns": len(structure.get("columns", [])),
                    "rows": stats.get("total_rows", 0)
                })
            except Exception as e:
                report_data["table_analyses"].append({
                    "table_name": table,
                    "error": str(e)
                })
        
        analysis_meta = {
            "type": "database_report",
            "insights": [
                f"Base de datos con {len(table_list)} tablas",
                "Reporte generado automáticamente"
            ]
        }
        
        if output_format.lower() == "json":
            return export_to_json(report_data, analysis_meta)
        elif output_format.lower() == "pptx":
            filepath = export_to_pptx(report_data, analysis_meta, OUTPUT_DIR)
            return f"✅ Reporte generado:\n📁 {filepath}"
        else:
            return export_to_text(report_data, analysis_meta)
            
    except Exception as e:
        return f"❌ Error generando reporte: {str(e)}"


# Resources para exponer información como contexto
@mcp.resource("db://tables")
async def resource_tables() -> str:
    """Resource que expone la lista de tablas como contexto para el LLM."""
    global db
    if db is None:
        db = DatabaseConnection()
    tables = await db.get_tables()
    return json.dumps({"available_tables": tables})


@mcp.resource("db://schema/{table_name}")
async def resource_schema(table_name: str) -> str:
    """Resource que expone el esquema de una tabla específica."""
    global db
    if db is None:
        db = DatabaseConnection()
    schema = await db.get_table_structure(table_name)
    return json.dumps(schema, default=str)


def _generate_table_insights(structure, stats, distribution):
    """Genera insights sobre una tabla."""
    insights = []
    
    columns = structure.get("columns", [])
    total_rows = stats.get("total_rows", 0)
    
    insights.append(f"La tabla tiene {len(columns)} columnas y {total_rows:,} registros")
    
    # Detectar posibles PKs
    for col in columns:
        if "id" in col.get("name", "").lower():
            insights.append(f"'{col['name']}' parece ser un identificador")
    
    # Analizar distribuciones
    for col_name, dist in distribution.items():
        if isinstance(dist, list) and len(dist) == 1:
            insights.append(f"'{col_name}' tiene un único valor en todos los registros")
    
    return insights


def main():
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(description="MCP Database Analyzer Server")
    parser.add_argument(
        "--transport", 
        choices=["stdio", "sse"], 
        default="stdio",
        help="Tipo de transporte (default: stdio)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000,
        help="Puerto para SSE transport (default: 8000)"
    )
    
    args = parser.parse_args()
    
    if args.transport == "sse":
        mcp.run(transport="sse", port=args.port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
