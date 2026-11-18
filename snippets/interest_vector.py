"""Vector de interés a partir de interacciones (ejemplo ilustrativo).

El embedding del producto se guarda con cada interacción, así que no hace falta
pedir 20 vectores a Elasticsearch: el cálculo es local y luego hay una sola búsqueda kNN.
"""
from datetime import timedelta

import numpy as np

WEIGHTS = {"purchase": 4.0, "cart": 2.0, "wishlist": 1.5, "view": 1.0}
MAX_INTERACTIONS = 20
VIEW_DEDUP_WINDOW = timedelta(minutes=10)


def dedupe_views(interactions):
    """Visitas repetidas al mismo producto en menos de 10 minutos cuentan una vez
    (recargar la página no debe inflar el interés). Se asume orden descendente por fecha."""
    last_view = {}
    result = []
    for i in interactions:
        if i.kind == "view":
            prev = last_view.get(i.product_id)
            if prev and prev - i.created_at < VIEW_DEDUP_WINDOW:
                continue
            last_view[i.product_id] = i.created_at
        result.append(i)
    return result


def interest_vector(interactions):
    recent = dedupe_views(interactions)[:MAX_INTERACTIONS]
    if not recent:
        return None  # sin historial: no se muestra "Para ti"
    total = sum(WEIGHTS[i.kind] for i in recent)
    weighted = sum(WEIGHTS[i.kind] * np.asarray(i.embedding) for i in recent)
    return (weighted / total).tolist()
