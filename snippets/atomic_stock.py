"""Stock consistente y contadores atómicos (ejemplo ilustrativo, modelos simplificados)."""
from django.db import transaction
from django.db.models import F


class InsufficientStock(Exception):
    pass


@transaction.atomic
def reserve_stock(variant_id: int, quantity: int) -> None:
    # select_for_update() bloquea la fila hasta el fin de la transacción:
    # dos compras simultáneas no pueden vender la misma unidad.
    variant = ProductVariant.objects.select_for_update().get(pk=variant_id)
    if variant.stock < quantity:
        raise InsufficientStock(f"Stock disponible: {variant.stock}")
    variant.stock = F("stock") - quantity
    variant.save(update_fields=["stock"])


def register_view(product_id: int) -> None:
    # La suma ocurre en SQL (UPDATE ... SET views_count = views_count + 1),
    # sin leer-sumar-guardar en Python, que pierde incrementos concurrentes.
    Product.objects.filter(pk=product_id).update(views_count=F("views_count") + 1)
