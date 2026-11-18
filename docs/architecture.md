# Arquitectura de CompraPues (vista simplificada)

Diagrama enfocado en los servicios relevantes para las decisiones documentadas. El sistema completo tiene 11 microservicios.

```mermaid
flowchart LR
  FE[Frontend React + TS] --> CAT[Catálogo]
  FE --> PAY[Checkout y pagos]
  FE --> REC[Recomendaciones]
  CAT --> DB1[(PostgreSQL)]
  PAY --> DB2[(PostgreSQL)]
  PAY <-. webhooks .-> GW[Pasarelas de pago]
  REC --> DB3[(PostgreSQL)]
  REC --> ES[(Elasticsearch kNN)]
  EMB[Servicio de embeddings] --> ES
```

## Principios

| Principio | Cómo se aplica |
|---|---|
| Una base por servicio | Cada microservicio tiene su PostgreSQL, con Row Level Security |
| Aislamiento de carga pesada | Embeddings y kNN fuera del camino crítico de compra |
| Degradar sin romper | Si falla la búsqueda semántica, la compra sigue funcionando |
| Idempotencia en integraciones | Webhooks de pago con firma verificada e ID de evento único |
| Consistencia en escritura | Stock con bloqueo de fila y contadores atómicos |
| Observabilidad | Sentry para errores de producción y endpoint de diagnóstico |
