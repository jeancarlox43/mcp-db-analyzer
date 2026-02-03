"""
Módulo de conexión y operaciones con la base de datos.
Soporta PostgreSQL por defecto, extensible a otras BDs.
"""
import os
from typing import Any, Dict, List, Optional
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import Engine


class DatabaseConnection:
    """Gestiona la conexión y operaciones con la base de datos."""
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Inicializa la conexión a la base de datos.
        
        Args:
            connection_string: URL de conexión. Si no se proporciona,
                             se usa DATABASE_URL del entorno.
        """
        self.connection_string = connection_string or os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/analytics"
        )
        self._engine: Optional[Engine] = None
        self._inspector = None
    
    @property
    def engine(self) -> Engine:
        """Lazy initialization del engine."""
        if self._engine is None:
            self._engine = create_engine(
                self.connection_string,
                pool_pre_ping=True,  # Verificar conexión antes de usar
                pool_size=5,
                max_overflow=10
            )
        return self._engine
    
    @property
    def inspector(self):
        """Lazy initialization del inspector."""
        if self._inspector is None:
            self._inspector = inspect(self.engine)
        return self._inspector
    
    async def execute(self, query: str, params: Dict = None) -> List[Dict[str, Any]]:
        """
        Ejecuta una query y retorna los resultados como lista de diccionarios.
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros opcionales para la query
        
        Returns:
            Lista de diccionarios con los resultados
        """
        with self.engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            columns = result.keys()
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            return rows
    
    async def get_tables(self, schema: str = "public") -> List[str]:
        """
        Obtiene la lista de tablas en el esquema especificado.
        
        Args:
            schema: Nombre del esquema (default: public)
        
        Returns:
            Lista de nombres de tablas
        """
        return self.inspector.get_table_names(schema=schema)
    
    async def get_table_structure(self, table_name: str, schema: str = "public") -> Dict[str, Any]:
        """
        Obtiene la estructura completa de una tabla.
        
        Args:
            table_name: Nombre de la tabla
            schema: Nombre del esquema
        
        Returns:
            Diccionario con columnas, PKs, FKs e índices
        """
        try:
            columns = self.inspector.get_columns(table_name, schema=schema)
            pk = self.inspector.get_pk_constraint(table_name, schema=schema)
            fks = self.inspector.get_foreign_keys(table_name, schema=schema)
            indexes = self.inspector.get_indexes(table_name, schema=schema)
            
            # Simplificar la información de columnas
            simplified_columns = []
            for col in columns:
                simplified_columns.append({
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col.get("nullable", True),
                    "default": str(col.get("default", "")) if col.get("default") else None,
                    "primary_key": col["name"] in (pk.get("constrained_columns", []) if pk else [])
                })
            
            return {
                "columns": simplified_columns,
                "primary_key": pk,
                "foreign_keys": fks,
                "indexes": indexes,
                "column_count": len(columns)
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_table_stats(self, table_name: str) -> Dict[str, Any]:
        """
        Obtiene estadísticas básicas de una tabla.
        
        Args:
            table_name: Nombre de la tabla
        
        Returns:
            Diccionario con estadísticas
        """
        stats = {}
        
        with self.engine.connect() as conn:
            # Contar filas totales
            try:
                result = conn.execute(text(f"SELECT COUNT(*) as total FROM {table_name}"))
                stats["total_rows"] = result.scalar()
            except Exception as e:
                stats["total_rows"] = f"Error: {e}"
            
            # Obtener tamaño aproximado (PostgreSQL específico)
            try:
                result = conn.execute(text(f"""
                    SELECT pg_size_pretty(pg_total_relation_size('{table_name}')) as size
                """))
                stats["table_size"] = result.scalar()
            except Exception:
                stats["table_size"] = "N/A"
        
        return stats
    
    async def get_column_distributions(
        self, 
        table_name: str, 
        max_columns: int = 5,
        top_values: int = 10
    ) -> Dict[str, Any]:
        """
        Analiza la distribución de valores en las columnas de una tabla.
        
        Args:
            table_name: Nombre de la tabla
            max_columns: Máximo de columnas a analizar
            top_values: Cantidad de valores top a mostrar
        
        Returns:
            Diccionario con distribuciones por columna
        """
        columns = self.inspector.get_columns(table_name)
        distributions = {}
        
        with self.engine.connect() as conn:
            for col in columns[:max_columns]:
                col_name = col['name']
                col_type = str(col['type']).upper()
                
                try:
                    # Para columnas numéricas, obtener estadísticas
                    if any(t in col_type for t in ['INT', 'FLOAT', 'DECIMAL', 'NUMERIC', 'DOUBLE']):
                        query = text(f"""
                            SELECT 
                                MIN({col_name}) as min_val,
                                MAX({col_name}) as max_val,
                                AVG({col_name}::numeric) as avg_val,
                                COUNT(DISTINCT {col_name}) as unique_count
                            FROM {table_name}
                            WHERE {col_name} IS NOT NULL
                        """)
                        result = conn.execute(query)
                        row = result.fetchone()
                        distributions[col_name] = {
                            "type": "numeric",
                            "min": float(row[0]) if row[0] else None,
                            "max": float(row[1]) if row[1] else None,
                            "avg": round(float(row[2]), 2) if row[2] else None,
                            "unique_values": row[3]
                        }
                    else:
                        # Para otras columnas, obtener top valores
                        query = text(f"""
                            SELECT {col_name}, COUNT(*) as freq 
                            FROM {table_name} 
                            WHERE {col_name} IS NOT NULL
                            GROUP BY {col_name} 
                            ORDER BY freq DESC 
                            LIMIT {top_values}
                        """)
                        result = conn.execute(query)
                        distributions[col_name] = {
                            "type": "categorical",
                            "top_values": [
                                {"value": str(row[0])[:50], "frequency": row[1]} 
                                for row in result.fetchall()
                            ]
                        }
                except Exception as e:
                    distributions[col_name] = {"error": str(e)}
        
        return distributions
    
    async def get_sample_data(
        self, 
        table_name: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Obtiene una muestra de datos de la tabla.
        
        Args:
            table_name: Nombre de la tabla
            limit: Cantidad de filas a retornar
        
        Returns:
            Lista de diccionarios con los datos
        """
        return await self.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
    
    def close(self):
        """Cierra la conexión a la base de datos."""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            self._inspector = None
