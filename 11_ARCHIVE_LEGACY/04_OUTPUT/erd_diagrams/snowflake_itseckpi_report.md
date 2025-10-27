# Snowflake ERD Report - SECURITY_ANALYTICS Schema

## Resumen Ejecutivo

Arquitectura de datos del esquema **SECURITY_ANALYTICS** en Snowflake para monitoreo de KPIs de seguridad IT.

## Arquitectura de Capas

### DEV_LANDING (Capa de Ingesta)
- **Proposito**: Almacenar datos crudos desde sistemas fuente
- **Tablas**:
  - RAW_KPI_METRICS: Metricas de KPI sin procesar
  - RAW_SYSTEM_EVENTS: Eventos de sistemas
  - RAW_PERFORMANCE_DATA: Datos de rendimiento

### DEV_TRANSFORMATION (Capa de Transformacion)
- **Proposito**: Datos limpios y modelados (Star Schema)
- **Dimensiones**:
  - DIM_KPI: Catalogo de KPIs
  - DIM_SYSTEM: Sistemas monitoreados
  - DIM_DATE: Dimension temporal
- **Hechos**:
  - FACT_KPI_MEASUREMENTS: Mediciones de KPIs

### DEV_REPORTING (Capa de Reporte)
- **Proposito**: Vistas y agregaciones para consumo
- **Objetos**:
  - VW_KPI_DASHBOARD: Vista principal para dashboards
  - VW_SYSTEM_PERFORMANCE: Performance por sistema
  - AGG_MONTHLY_KPI: Agregaciones mensuales
  - RPT_EXECUTIVE_SUMMARY: Resumen ejecutivo

## Flujo de Datos

```
Landing -> Transformation -> Reporting
   |            |              |
Raw Data -> Clean/Model -> Dashboards
```

## Relaciones Identificadas

- **Landing a Transformation**: Carga y transformacion de datos crudos
- **Star Schema**: Relaciones entre dimensiones y hechos
- **Transformation a Reporting**: Agregaciones y vistas materializadas

---
*Generado: 2025-10-06 06:46*
