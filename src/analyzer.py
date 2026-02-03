"""
Módulo de análisis de queries SQL y resultados.
Genera insights automáticos sobre los datos.
"""
import re
from typing import Any, Dict, List
from datetime import datetime


class QueryAnalyzer:
    """Analiza queries SQL y sus resultados para generar insights."""
    
    def analyze(self, query: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analiza una query y sus resultados.
        
        Args:
            query: La consulta SQL ejecutada
            results: Lista de resultados de la query
        
        Returns:
            Diccionario con análisis completo
        """
        return {
            "query_info": self._analyze_query(query),
            "results_info": self._analyze_results(results),
            "insights": self._generate_insights(query, results),
            "timestamp": datetime.now().isoformat(),
            "summary": self._generate_summary(results)
        }
    
    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analiza la estructura y características de la query."""
        query_clean = " ".join(query.split())  # Normalizar espacios
        query_upper = query_clean.upper()
        
        # Detectar tipo de operación
        query_type = self._detect_query_type(query_upper)
        
        # Extraer tablas
        tables = self._extract_tables(query_upper)
        
        # Detectar características
        features = {
            "has_joins": bool(re.search(r'\bJOIN\b', query_upper)),
            "has_subquery": query_upper.count('SELECT') > 1,
            "has_aggregations": bool(re.search(r'\b(COUNT|SUM|AVG|MAX|MIN)\s*\(', query_upper)),
            "has_grouping": 'GROUP BY' in query_upper,
            "has_having": 'HAVING' in query_upper,
            "has_ordering": 'ORDER BY' in query_upper,
            "has_limit": 'LIMIT' in query_upper,
            "has_distinct": 'DISTINCT' in query_upper,
            "has_where": 'WHERE' in query_upper,
            "has_union": 'UNION' in query_upper,
            "has_case": 'CASE' in query_upper
        }
        
        # Contar JOINs
        join_count = len(re.findall(r'\bJOIN\b', query_upper))
        
        return {
            "type": query_type,
            "tables": tables,
            "features": features,
            "join_count": join_count,
            "complexity": self._calculate_complexity(features, join_count),
            "query_length": len(query_clean)
        }
    
    def _detect_query_type(self, query_upper: str) -> str:
        """Detecta el tipo de operación SQL."""
        query_start = query_upper.strip()[:20]
        
        if query_start.startswith('SELECT'):
            return 'SELECT'
        elif query_start.startswith('INSERT'):
            return 'INSERT'
        elif query_start.startswith('UPDATE'):
            return 'UPDATE'
        elif query_start.startswith('DELETE'):
            return 'DELETE'
        elif query_start.startswith('CREATE'):
            return 'CREATE'
        elif query_start.startswith('ALTER'):
            return 'ALTER'
        elif query_start.startswith('DROP'):
            return 'DROP'
        elif query_start.startswith('WITH'):
            return 'CTE'  # Common Table Expression
        else:
            return 'UNKNOWN'
    
    def _extract_tables(self, query_upper: str) -> List[str]:
        """Extrae los nombres de tablas de la query."""
        # Buscar tablas después de FROM y JOIN
        patterns = [
            r'FROM\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'INTO\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'UPDATE\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        ]
        
        tables = set()
        for pattern in patterns:
            matches = re.findall(pattern, query_upper)
            tables.update(m.lower() for m in matches)
        
        # Filtrar palabras reservadas comunes
        reserved = {'select', 'from', 'where', 'and', 'or', 'on', 'as', 'in', 'not', 'null'}
        tables = [t for t in tables if t not in reserved]
        
        return list(tables)
    
    def _calculate_complexity(self, features: Dict[str, bool], join_count: int) -> str:
        """Calcula la complejidad de la query."""
        score = 0
        
        # Sumar puntos por cada característica
        if features.get('has_joins'):
            score += join_count
        if features.get('has_subquery'):
            score += 3
        if features.get('has_aggregations'):
            score += 1
        if features.get('has_grouping'):
            score += 1
        if features.get('has_having'):
            score += 1
        if features.get('has_union'):
            score += 2
        if features.get('has_case'):
            score += 1
        
        if score == 0:
            return 'simple'
        elif score <= 2:
            return 'moderate'
        elif score <= 5:
            return 'complex'
        else:
            return 'very_complex'
    
    def _analyze_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analiza los resultados de la query."""
        if not results:
            return {
                "row_count": 0,
                "columns": [],
                "column_count": 0,
                "column_analysis": {}
            }
        
        columns = list(results[0].keys())
        column_analysis = {}
        
        for col in columns:
            values = [r[col] for r in results]
            non_null_values = [v for v in values if v is not None]
            
            analysis = {
                "null_count": len(values) - len(non_null_values),
                "null_percentage": round((len(values) - len(non_null_values)) / len(values) * 100, 2)
            }
            
            if non_null_values:
                sample = non_null_values[0]
                
                if isinstance(sample, (int, float)):
                    numeric_values = [v for v in non_null_values if isinstance(v, (int, float))]
                    if numeric_values:
                        analysis.update({
                            "type": "numeric",
                            "min": min(numeric_values),
                            "max": max(numeric_values),
                            "avg": round(sum(numeric_values) / len(numeric_values), 2),
                            "unique_count": len(set(numeric_values))
                        })
                elif isinstance(sample, bool):
                    analysis.update({
                        "type": "boolean",
                        "true_count": sum(1 for v in non_null_values if v),
                        "false_count": sum(1 for v in non_null_values if not v)
                    })
                else:
                    str_values = [str(v) for v in non_null_values]
                    analysis.update({
                        "type": "text",
                        "unique_count": len(set(str_values)),
                        "avg_length": round(sum(len(s) for s in str_values) / len(str_values), 1),
                        "max_length": max(len(s) for s in str_values),
                        "sample_values": list(set(str_values))[:5]
                    })
            else:
                analysis["type"] = "all_null"
            
            column_analysis[col] = analysis
        
        return {
            "row_count": len(results),
            "columns": columns,
            "column_count": len(columns),
            "column_analysis": column_analysis
        }
    
    def _generate_insights(self, query: str, results: List[Dict[str, Any]]) -> List[str]:
        """Genera insights automáticos sobre la query y resultados."""
        insights = []
        
        if not results:
            insights.append("⚠️ La query no retornó resultados. Verifica los filtros.")
            return insights
        
        row_count = len(results)
        
        # Insights sobre cantidad de resultados
        if row_count == 1:
            insights.append("📌 Resultado único - posiblemente una búsqueda específica")
        elif row_count < 10:
            insights.append(f"📊 Conjunto pequeño: {row_count} registros")
        elif row_count > 100:
            insights.append(f"📈 Conjunto grande: {row_count:,} registros. Considera paginar.")
        elif row_count > 1000:
            insights.append(f"⚠️ {row_count:,} registros es un volumen alto. Optimiza la query.")
        
        # Análisis de columnas
        columns = list(results[0].keys())
        
        for col in columns:
            values = [r[col] for r in results]
            non_null = [v for v in values if v is not None]
            
            # Detectar columnas con todos valores únicos (posible PK)
            if len(non_null) == len(set(str(v) for v in non_null)) and len(non_null) > 1:
                if 'id' in col.lower():
                    insights.append(f"🔑 '{col}' parece ser la clave primaria")
                else:
                    insights.append(f"🆔 '{col}' tiene valores únicos - posible identificador")
            
            # Detectar columnas con un solo valor
            if len(set(str(v) for v in non_null)) == 1 and len(non_null) > 1:
                insights.append(f"⚡ '{col}' tiene el mismo valor en todos los registros")
            
            # Detectar alto porcentaje de nulls
            null_pct = (len(values) - len(non_null)) / len(values) * 100
            if null_pct > 50:
                insights.append(f"⚠️ '{col}' tiene {null_pct:.0f}% de valores nulos")
        
        # Detectar posibles duplicados
        if row_count > 1:
            first_row_str = str(results[0])
            duplicates = sum(1 for r in results if str(r) == first_row_str)
            if duplicates > 1:
                insights.append(f"🔄 Se detectaron {duplicates} filas idénticas")
        
        return insights
    
    def _generate_summary(self, results: List[Dict[str, Any]]) -> str:
        """Genera un resumen ejecutivo de los resultados."""
        if not results:
            return "No se encontraron datos para los criterios especificados."
        
        row_count = len(results)
        col_count = len(results[0].keys())
        
        return (
            f"Se obtuvieron {row_count:,} registros con {col_count} columnas. "
            f"Los datos fueron procesados y analizados exitosamente."
        )
