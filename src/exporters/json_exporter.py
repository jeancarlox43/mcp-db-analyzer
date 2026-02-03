"""
Exportador a formato JSON estructurado.
Genera salida JSON con metadata para integración programática.
"""
import json
from typing import Any, Dict
from datetime import datetime


def export_to_json(data: Any, analysis: Dict[str, Any]) -> str:
    """
    Exporta los datos a formato JSON estructurado.
    
    Args:
        data: Datos a exportar
        analysis: Metadatos del análisis
    
    Returns:
        String JSON formateado
    """
    output = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "format_version": "1.0",
            "generator": "mcp-db-analyzer"
        },
        "analysis": _clean_for_json(analysis),
        "data": _clean_for_json(data)
    }
    
    return json.dumps(output, indent=2, ensure_ascii=False, default=_json_serializer)


def _json_serializer(obj: Any) -> Any:
    """Serializa objetos no estándar a JSON."""
    if hasattr(obj, 'isoformat'):  # datetime, date
        return obj.isoformat()
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    else:
        return str(obj)


def _clean_for_json(obj: Any) -> Any:
    """
    Limpia recursivamente un objeto para serialización JSON.
    Convierte tipos no serializables a strings.
    """
    if obj is None:
        return None
    elif isinstance(obj, (str, int, float, bool)):
        return obj
    elif isinstance(obj, dict):
        return {str(k): _clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_clean_for_json(item) for item in obj]
    elif hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        return str(obj)
