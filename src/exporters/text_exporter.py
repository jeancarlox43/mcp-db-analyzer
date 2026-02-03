"""
Exportador a formato texto legible.
Genera reportes formateados para consumo humano.
"""
from typing import Any, Dict, List
from datetime import datetime


def export_to_text(data: Any, analysis: Dict[str, Any]) -> str:
    """
    Exporta los datos a formato texto legible y bien estructurado.
    
    Args:
        data: Datos a exportar (lista de dicts o dict)
        analysis: Metadatos del análisis
    
    Returns:
        String con el reporte formateado
    """
    lines = []
    
    # Header
    lines.append("═" * 70)
    lines.append("  📊 REPORTE DE ANÁLISIS DE BASE DE DATOS")
    lines.append("═" * 70)
    lines.append(f"  Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("═" * 70)
    lines.append("")
    
    # Tipo de análisis
    analysis_type = analysis.get("type", "query")
    
    if analysis_type == "table_analysis":
        _format_table_analysis(lines, data, analysis)
    elif analysis_type == "database_report":
        _format_database_report(lines, data, analysis)
    else:
        _format_query_results(lines, data, analysis)
    
    # Insights
    insights = analysis.get("insights", [])
    if insights:
        lines.append("")
        lines.append("─" * 70)
        lines.append("  💡 INSIGHTS Y OBSERVACIONES")
        lines.append("─" * 70)
        for insight in insights:
            lines.append(f"  • {insight}")
    
    # Footer
    lines.append("")
    lines.append("═" * 70)
    lines.append("  Fin del reporte")
    lines.append("═" * 70)
    
    return "\n".join(lines)


def _format_query_results(lines: List[str], data: Any, analysis: Dict[str, Any]):
    """Formatea resultados de una query."""
    
    # Información de la query
    query_info = analysis.get("query_info", {})
    if query_info:
        lines.append("  📋 INFORMACIÓN DE LA QUERY")
        lines.append("─" * 70)
        lines.append(f"    Tipo:        {query_info.get('type', 'N/A')}")
        lines.append(f"    Tablas:      {', '.join(query_info.get('tables', ['N/A']))}")
        lines.append(f"    Complejidad: {query_info.get('complexity', 'N/A')}")
        
        features = query_info.get("features", {})
        active_features = [k.replace("has_", "") for k, v in features.items() if v]
        if active_features:
            lines.append(f"    Características: {', '.join(active_features)}")
        lines.append("")
    
    # Resumen de resultados
    results_info = analysis.get("results_info", {})
    if results_info:
        lines.append("  📈 RESUMEN DE RESULTADOS")
        lines.append("─" * 70)
        lines.append(f"    Total registros: {results_info.get('row_count', 0):,}")
        lines.append(f"    Total columnas:  {results_info.get('column_count', 0)}")
        
        columns = results_info.get("columns", [])
        if columns:
            lines.append(f"    Columnas: {', '.join(columns[:10])}")
            if len(columns) > 10:
                lines.append(f"              ... y {len(columns) - 10} más")
        lines.append("")
    
    # Datos
    if isinstance(data, list) and data:
        lines.append("  📝 DATOS (primeros 15 registros)")
        lines.append("─" * 70)
        
        for i, row in enumerate(data[:15], 1):
            lines.append(f"    ┌─ Registro {i}")
            for key, value in row.items():
                value_str = str(value)[:50]
                if len(str(value)) > 50:
                    value_str += "..."
                lines.append(f"    │  {key}: {value_str}")
            lines.append("    └" + "─" * 40)
        
        if len(data) > 15:
            lines.append(f"    ... y {len(data) - 15} registros más")


def _format_table_analysis(lines: List[str], data: Dict[str, Any], analysis: Dict[str, Any]):
    """Formatea análisis de una tabla."""
    table_name = data.get("table_name", "Unknown")
    
    lines.append(f"  🗃️  ANÁLISIS DE TABLA: {table_name}")
    lines.append("─" * 70)
    
    # Estructura
    structure = data.get("structure", {})
    columns = structure.get("columns", [])
    
    lines.append("")
    lines.append("  📐 ESTRUCTURA")
    lines.append("─" * 70)
    
    if columns:
        lines.append(f"    {'Columna':<25} {'Tipo':<20} {'Nullable':<10} {'PK'}")
        lines.append("    " + "-" * 60)
        for col in columns:
            name = col.get("name", "")[:24]
            col_type = str(col.get("type", ""))[:19]
            nullable = "Sí" if col.get("nullable") else "No"
            pk = "✓" if col.get("primary_key") else ""
            lines.append(f"    {name:<25} {col_type:<20} {nullable:<10} {pk}")
    
    # Estadísticas
    stats = data.get("statistics", {})
    if stats:
        lines.append("")
        lines.append("  📊 ESTADÍSTICAS")
        lines.append("─" * 70)
        lines.append(f"    Total de filas: {stats.get('total_rows', 'N/A'):,}")
        if stats.get("table_size"):
            lines.append(f"    Tamaño: {stats.get('table_size')}")
    
    # Distribución
    distribution = data.get("distribution", {})
    if distribution:
        lines.append("")
        lines.append("  📉 DISTRIBUCIÓN DE DATOS")
        lines.append("─" * 70)
        
        for col_name, dist in list(distribution.items())[:5]:
            lines.append(f"    {col_name}:")
            if isinstance(dist, dict):
                if dist.get("type") == "numeric":
                    lines.append(f"      Min: {dist.get('min')} | Max: {dist.get('max')} | Avg: {dist.get('avg')}")
                elif dist.get("type") == "categorical":
                    top_vals = dist.get("top_values", [])[:3]
                    for tv in top_vals:
                        lines.append(f"      - {tv.get('value')}: {tv.get('frequency')} ocurrencias")
                elif "error" in dist:
                    lines.append(f"      Error: {dist.get('error')}")


def _format_database_report(lines: List[str], data: Dict[str, Any], analysis: Dict[str, Any]):
    """Formatea reporte general de base de datos."""
    overview = data.get("database_overview", {})
    
    lines.append("  🗄️  REPORTE DE BASE DE DATOS")
    lines.append("─" * 70)
    lines.append(f"    Total de tablas: {overview.get('total_tables', 0)}")
    lines.append("")
    
    # Lista de tablas con info
    table_analyses = data.get("table_analyses", [])
    if table_analyses:
        lines.append("  📋 TABLAS")
        lines.append("─" * 70)
        lines.append(f"    {'Tabla':<30} {'Columnas':<12} {'Filas':<15}")
        lines.append("    " + "-" * 55)
        
        for ta in table_analyses:
            name = ta.get("table_name", "")[:29]
            cols = ta.get("columns", "N/A")
            rows = ta.get("rows", "N/A")
            if ta.get("error"):
                lines.append(f"    {name:<30} Error: {ta.get('error')[:30]}")
            else:
                rows_str = f"{rows:,}" if isinstance(rows, int) else str(rows)
                lines.append(f"    {name:<30} {cols:<12} {rows_str:<15}")
