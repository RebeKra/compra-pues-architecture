"""Eliminación de consultas N+1 en variantes (ejemplo ilustrativo, modelos simplificados)."""
from django.db.models import Prefetch


def get_variants(product_id: int):
    # Antes: 1 consulta por variante + 1 por cada atributo (N+1).
    # Ahora: pocas consultas por petición, sin importar cuántas variantes haya.
    return (
        ProductVariant.objects.filter(product_id=product_id)
        .prefetch_related(
            Prefetch(
                "attribute_values",
                queryset=AttributeValue.objects.select_related("attribute"),
            )
        )
    )
