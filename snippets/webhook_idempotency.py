"""Webhook de pago con firma verificada e idempotencia (ejemplo ilustrativo).

Cada pasarela define su propio esquema de firma; aquí se muestra el patrón con HMAC-SHA256.
"""
import hashlib
import hmac
import json

from django.db import IntegrityError, transaction
from django.http import HttpResponse


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)  # comparación en tiempo constante


def payment_webhook(request):
    if not verify_signature(request.body, request.headers.get("X-Signature", ""), SECRET):
        return HttpResponse(status=401)

    event = json.loads(request.body)
    try:
        with transaction.atomic():
            # ProcessedEvent.event_id tiene restricción UNIQUE.
            # Si el procesamiento falla, la transacción revierte también este
            # registro y el reintento de la pasarela vuelve a procesarlo.
            ProcessedEvent.objects.create(event_id=event["id"])
            process_payment_event(event)
    except IntegrityError:
        # Evento ya procesado: responder 200 para que la pasarela deje de reintentar.
        return HttpResponse(status=200)
    return HttpResponse(status=200)
