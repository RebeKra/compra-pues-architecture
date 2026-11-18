"""Recomendaciones con degradación elegante (ejemplo ilustrativo, Elasticsearch 8.x)."""
import logging

from elasticsearch import ApiError
from elastic_transport import TransportError

logger = logging.getLogger(__name__)


def get_recommendations(es, vector, seen_product_ids, size=10):
    if vector is None:
        return []
    try:
        response = es.search(
            index="products",
            knn={
                "field": "embedding",
                "query_vector": vector,
                "k": size,
                "num_candidates": 100,
                # Filtros dentro del índice, no en Python.
                "filter": [
                    {"term": {"is_active": True}},
                    {"range": {"stock": {"gt": 0}}},
                    {"bool": {"must_not": {"ids": {"values": [str(p) for p in seen_product_ids]}}}},
                ],
            },
        )
        return [hit["_source"] for hit in response["hits"]["hits"]]
    except (TransportError, ApiError):
        # Si Elasticsearch falla, devolver lista vacía: el frontend oculta
        # la sección "Para ti" y el catálogo y el checkout siguen funcionando.
        logger.warning("Elasticsearch no disponible; se omiten recomendaciones", exc_info=True)
        return []
