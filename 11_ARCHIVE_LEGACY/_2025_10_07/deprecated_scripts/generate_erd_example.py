#!/usr/bin/env python3
"""
Script para generar un ERD de ejemplo del esquema SECURITY_ANALYTICS en Snowflake
Ejecutar directamente: python generate_erd_example.py
"""

import graphviz
import os

def create_snowflake_erd():
    """Genera un diagrama ERD de ejemplo basado en la estructura típica de SECURITY_ANALYTICS"""

    print("="*60)
    print(" GENERANDO ERD DE EJEMPLO - SCHEMA SECURITY_ANALYTICS")
    print("="*60)

    # Crear el grafo
    dot = graphviz.Digraph(comment='Snowflake ERD - SECURITY_ANALYTICS Schema')
    dot.attr(rankdir='TB')  # Top to Bottom
    dot.attr('node', shape='none', fontname='Arial')
    dot.attr('graph', bgcolor='white', pad='0.5', splines='ortho')

    # Definir tablas de ejemplo por capa
    # Estas son tablas típicas que podrías tener en tu esquema SECURITY_ANALYTICS

    # DEV_LANDING - Datos crudos
    landing_tables = [
        {
            'name': 'RAW_KPI_METRICS',
            'columns': [
                ('LOAD_ID', 'NUMBER'),
                ('KPI_CODE', 'VARCHAR(50)'),
                ('KPI_VALUE', 'NUMBER(18,2)'),
                ('MEASUREMENT_DATE', 'TIMESTAMP'),
                ('SOURCE_SYSTEM', 'VARCHAR(100)'),
                ('RAW_DATA', 'VARIANT'),
                ('LOAD_TIMESTAMP', 'TIMESTAMP')
            ]
        },
        {
            'name': 'RAW_SYSTEM_EVENTS',
            'columns': [
                ('EVENT_ID', 'VARCHAR(100)'),
                ('SYSTEM_ID', 'VARCHAR(50)'),
                ('EVENT_TYPE', 'VARCHAR(50)'),
                ('EVENT_TIMESTAMP', 'TIMESTAMP'),
                ('EVENT_DATA', 'VARIANT'),
                ('LOAD_DATE', 'DATE')
            ]
        },
        {
            'name': 'RAW_PERFORMANCE_DATA',
            'columns': [
                ('RECORD_ID', 'NUMBER'),
                ('SYSTEM_ID', 'VARCHAR(50)'),
                ('METRIC_NAME', 'VARCHAR(100)'),
                ('METRIC_VALUE', 'FLOAT'),
                ('CAPTURE_TIME', 'TIMESTAMP')
            ]
        }
    ]

    # DEV_TRANSFORMATION - Datos transformados
    transformation_tables = [
        {
            'name': 'DIM_KPI',
            'columns': [
                ('KPI_KEY', 'NUMBER'),
                ('KPI_CODE', 'VARCHAR(50)'),
                ('KPI_NAME', 'VARCHAR(200)'),
                ('KPI_CATEGORY', 'VARCHAR(100)'),
                ('UNIT_OF_MEASURE', 'VARCHAR(50)'),
                ('TARGET_VALUE', 'NUMBER(18,2)'),
                ('IS_ACTIVE', 'BOOLEAN'),
                ('CREATED_DATE', 'DATE'),
                ('UPDATED_DATE', 'DATE')
            ]
        },
        {
            'name': 'DIM_SYSTEM',
            'columns': [
                ('SYSTEM_KEY', 'NUMBER'),
                ('SYSTEM_ID', 'VARCHAR(50)'),
                ('SYSTEM_NAME', 'VARCHAR(200)'),
                ('SYSTEM_TYPE', 'VARCHAR(100)'),
                ('DEPARTMENT', 'VARCHAR(100)'),
                ('IS_CRITICAL', 'BOOLEAN')
            ]
        },
        {
            'name': 'DIM_DATE',
            'columns': [
                ('DATE_KEY', 'NUMBER'),
                ('DATE', 'DATE'),
                ('YEAR', 'NUMBER'),
                ('QUARTER', 'NUMBER'),
                ('MONTH', 'NUMBER'),
                ('WEEK', 'NUMBER'),
                ('DAY_OF_WEEK', 'NUMBER'),
                ('IS_WEEKEND', 'BOOLEAN')
            ]
        },
        {
            'name': 'FACT_KPI_MEASUREMENTS',
            'columns': [
                ('MEASUREMENT_KEY', 'NUMBER'),
                ('KPI_KEY', 'NUMBER'),
                ('SYSTEM_KEY', 'NUMBER'),
                ('DATE_KEY', 'NUMBER'),
                ('ACTUAL_VALUE', 'NUMBER(18,2)'),
                ('TARGET_VALUE', 'NUMBER(18,2)'),
                ('VARIANCE', 'NUMBER(18,2)'),
                ('VARIANCE_PCT', 'NUMBER(5,2)')
            ]
        }
    ]

    # DEV_REPORTING - Vistas y agregaciones para reportes
    reporting_tables = [
        {
            'name': 'VW_KPI_DASHBOARD',
            'type': 'VIEW',
            'columns': [
                ('KPI_CODE', 'VARCHAR(50)'),
                ('KPI_NAME', 'VARCHAR(200)'),
                ('CURRENT_VALUE', 'NUMBER(18,2)'),
                ('TARGET_VALUE', 'NUMBER(18,2)'),
                ('ACHIEVEMENT_PCT', 'NUMBER(5,2)'),
                ('TREND', 'VARCHAR(10)'),
                ('LAST_UPDATED', 'TIMESTAMP')
            ]
        },
        {
            'name': 'VW_SYSTEM_PERFORMANCE',
            'type': 'VIEW',
            'columns': [
                ('SYSTEM_NAME', 'VARCHAR(200)'),
                ('AVG_PERFORMANCE', 'NUMBER(18,2)'),
                ('MAX_PERFORMANCE', 'NUMBER(18,2)'),
                ('MIN_PERFORMANCE', 'NUMBER(18,2)'),
                ('TOTAL_EVENTS', 'NUMBER')
            ]
        },
        {
            'name': 'AGG_MONTHLY_KPI',
            'columns': [
                ('YEAR_MONTH', 'VARCHAR(7)'),
                ('KPI_CODE', 'VARCHAR(50)'),
                ('AVG_VALUE', 'NUMBER(18,2)'),
                ('MAX_VALUE', 'NUMBER(18,2)'),
                ('MIN_VALUE', 'NUMBER(18,2)'),
                ('TOTAL_MEASUREMENTS', 'NUMBER')
            ]
        },
        {
            'name': 'RPT_EXECUTIVE_SUMMARY',
            'columns': [
                ('REPORT_DATE', 'DATE'),
                ('TOTAL_KPIS', 'NUMBER'),
                ('KPIS_ON_TARGET', 'NUMBER'),
                ('KPIS_BELOW_TARGET', 'NUMBER'),
                ('OVERALL_PERFORMANCE', 'NUMBER(5,2)')
            ]
        }
    ]

    # Colores por capa
    colors = {
        'landing': ('#FFE5CC', '#FF9933'),
        'transformation': ('#CCE5FF', '#3399FF'),
        'reporting': ('#CCFFCC', '#33CC33')
    }

    # Crear subgrafo para DEV_LANDING
    with dot.subgraph(name='cluster_landing') as sub:
        sub.attr(label='DEV_LANDING', style='filled', fillcolor='#FFF5F0', fontsize='14', fontname='Arial Bold')

        for table in landing_tables:
            bgcolor, header_color = colors['landing']
            create_table_node(sub, f"landing_{table['name']}", table, bgcolor, header_color, 'TABLE')

    # Crear subgrafo para DEV_TRANSFORMATION
    with dot.subgraph(name='cluster_transformation') as sub:
        sub.attr(label='DEV_TRANSFORMATION', style='filled', fillcolor='#F0F5FF', fontsize='14', fontname='Arial Bold')

        for table in transformation_tables:
            bgcolor, header_color = colors['transformation']
            create_table_node(sub, f"trans_{table['name']}", table, bgcolor, header_color, 'TABLE')

    # Crear subgrafo para DEV_REPORTING
    with dot.subgraph(name='cluster_reporting') as sub:
        sub.attr(label='DEV_REPORTING', style='filled', fillcolor='#F0FFF0', fontsize='14', fontname='Arial Bold')

        for table in reporting_tables:
            bgcolor, header_color = colors['reporting']
            table_type = table.get('type', 'TABLE')
            create_table_node(sub, f"report_{table['name']}", table, bgcolor, header_color, table_type)

    # Definir relaciones
    relationships = [
        # Landing -> Transformation
        ('landing_RAW_KPI_METRICS', 'trans_DIM_KPI', 'KPI_CODE'),
        ('landing_RAW_KPI_METRICS', 'trans_FACT_KPI_MEASUREMENTS', 'Load'),
        ('landing_RAW_SYSTEM_EVENTS', 'trans_DIM_SYSTEM', 'SYSTEM_ID'),
        ('landing_RAW_PERFORMANCE_DATA', 'trans_FACT_KPI_MEASUREMENTS', 'Load'),

        # Transformation -> Transformation (Star Schema)
        ('trans_DIM_KPI', 'trans_FACT_KPI_MEASUREMENTS', 'KPI_KEY'),
        ('trans_DIM_SYSTEM', 'trans_FACT_KPI_MEASUREMENTS', 'SYSTEM_KEY'),
        ('trans_DIM_DATE', 'trans_FACT_KPI_MEASUREMENTS', 'DATE_KEY'),

        # Transformation -> Reporting
        ('trans_FACT_KPI_MEASUREMENTS', 'report_VW_KPI_DASHBOARD', 'Aggregate'),
        ('trans_FACT_KPI_MEASUREMENTS', 'report_AGG_MONTHLY_KPI', 'Aggregate'),
        ('trans_DIM_SYSTEM', 'report_VW_SYSTEM_PERFORMANCE', 'Join'),
        ('trans_DIM_KPI', 'report_VW_KPI_DASHBOARD', 'Join'),
        ('report_AGG_MONTHLY_KPI', 'report_RPT_EXECUTIVE_SUMMARY', 'Aggregate'),
    ]

    # Agregar relaciones al grafo
    for from_table, to_table, label in relationships:
        if 'landing' in from_table and 'trans' in to_table:
            # Landing a Transformation
            style = 'dashed'
            color = '#FF9933'
        elif 'trans' in from_table and 'trans' in to_table:
            # Dentro de Transformation (FK)
            style = 'solid'
            color = '#3399FF'
        else:
            # Transformation a Reporting
            style = 'dotted'
            color = '#33CC33'

        dot.edge(from_table, to_table,
                label=f' {label} ',
                style=style,
                color=color,
                fontsize='8',
                fontcolor=color,
                arrowhead='normal')

    # Agregar leyenda
    with dot.subgraph(name='cluster_legend') as legend:
        legend.attr(label='Leyenda', style='filled', fillcolor='#F8F8F8')
        legend_html = '''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
            <TR><TD COLSPAN="2" BGCOLOR="#E0E0E0"><B>Tipos de Relación</B></TD></TR>
            <TR><TD>Landing → Transform</TD><TD>Línea punteada naranja</TD></TR>
            <TR><TD>Foreign Keys</TD><TD>Línea sólida azul</TD></TR>
            <TR><TD>Transform → Report</TD><TD>Línea punteada verde</TD></TR>
            <TR><TD>🔑</TD><TD>Primary Key</TD></TR>
            <TR><TD>🔗</TD><TD>Foreign Key</TD></TR>
        </TABLE>>'''
        legend.node('legend', label=legend_html, shape='none')

    # Renderizar el diagrama
    try:
        # PNG
        dot.render('snowflake_itseckpi_erd', format='png', cleanup=True, view=False)
        print("✅ Diagrama PNG generado: snowflake_itseckpi_erd.png")

        # SVG
        dot.render('snowflake_itseckpi_erd', format='svg', cleanup=True, view=False)
        print("✅ Diagrama SVG generado: snowflake_itseckpi_erd.svg")

        # DOT file
        with open('snowflake_itseckpi_erd.dot', 'w', encoding='utf-8') as f:
            f.write(dot.source)
        print("✅ Archivo DOT generado: snowflake_itseckpi_erd.dot")

    except Exception as e:
        print(f"⚠️ Error generando diagrama: {e}")
        # Guardar al menos el archivo DOT
        with open('snowflake_itseckpi_erd.dot', 'w', encoding='utf-8') as f:
            f.write(dot.source)
        print("✅ Archivo DOT guardado (puedes convertirlo manualmente)")

    # Generar reporte
    generate_report()

    print("\n" + "="*60)
    print(" PROCESO COMPLETADO")
    print("="*60)
    print("\n📁 Archivos generados:")
    print("  ├── 📊 snowflake_itseckpi_erd.png - Diagrama visual")
    print("  ├── 📊 snowflake_itseckpi_erd.svg - Versión web")
    print("  ├── 📝 snowflake_itseckpi_erd.dot - Archivo editable")
    print("  └── 📄 snowflake_itseckpi_report.md - Documentación")
    print("\n💡 Este es un ERD de ejemplo basado en patrones típicos de ITSEC KPI.")
    print("   Para generar el ERD real, ejecuta las queries SQL en tu sesión de Snowflake.")


def create_table_node(subgraph, node_id, table_info, bgcolor, header_color, table_type):
    """Crea un nodo de tabla con formato HTML"""

    # Crear HTML para la tabla
    label = f'''<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" BGCOLOR="{bgcolor}">
        <TR><TD COLSPAN="2" BGCOLOR="{header_color}" ALIGN="CENTER">
        <FONT COLOR="WHITE"><B>{table_info['name']}</B></FONT><BR/>
        <FONT COLOR="WHITE" POINT-SIZE="9">({table_type})</FONT>
        </TD></TR>
        <TR>
            <TD BGCOLOR="#E8E8E8"><B>Column</B></TD>
            <TD BGCOLOR="#E8E8E8"><B>Type</B></TD>
        </TR>'''

    # Agregar columnas
    for i, (col_name, col_type) in enumerate(table_info['columns']):
        # Identificar PKs y FKs
        icon = ''
        if i == 0 and ('KEY' in col_name or 'ID' in col_name):
            icon = '🔑 '
        elif 'KEY' in col_name and i > 0:
            icon = '🔗 '

        label += f'''<TR>
            <TD ALIGN="LEFT">{icon}{col_name}</TD>
            <TD ALIGN="LEFT"><FONT POINT-SIZE="9">{col_type}</FONT></TD>
        </TR>'''

    label += '</TABLE>>'

    subgraph.node(node_id, label=label, shape='none')


def generate_report():
    """Genera un reporte en Markdown"""

    report = """# 📊 Snowflake ERD Report - SECURITY_ANALYTICS Schema

## 📋 Resumen Ejecutivo

Este documento describe la arquitectura de datos del esquema **SECURITY_ANALYTICS** en Snowflake,
diseñado para el monitoreo y análisis de KPIs de seguridad IT.

## 🏗️ Arquitectura de Capas

### 1️⃣ DEV_LANDING (Capa de Ingesta)
- **Propósito**: Almacenar datos crudos desde sistemas fuente
- **Características**:
  - Datos en formato raw/variant
  - Mínima transformación
  - Historial completo de cargas

**Tablas principales**:
- `RAW_KPI_METRICS`: Métricas de KPI sin procesar
- `RAW_SYSTEM_EVENTS`: Eventos de sistemas
- `RAW_PERFORMANCE_DATA`: Datos de rendimiento

### 2️⃣ DEV_TRANSFORMATION (Capa de Transformación)
- **Propósito**: Datos limpios y modelados (Star Schema)
- **Características**:
  - Modelo dimensional
  - Datos validados y enriquecidos
  - Optimizado para análisis

**Componentes**:
- **Dimensiones**:
  - `DIM_KPI`: Catálogo de KPIs
  - `DIM_SYSTEM`: Sistemas monitoreados
  - `DIM_DATE`: Dimensión temporal
- **Hechos**:
  - `FACT_KPI_MEASUREMENTS`: Mediciones de KPIs

### 3️⃣ DEV_REPORTING (Capa de Reporte)
- **Propósito**: Vistas y agregaciones para consumo
- **Características**:
  - Vistas materializadas
  - Agregaciones pre-calculadas
  - Optimizado para dashboards

**Objetos principales**:
- `VW_KPI_DASHBOARD`: Vista principal para dashboards
- `VW_SYSTEM_PERFORMANCE`: Performance por sistema
- `AGG_MONTHLY_KPI`: Agregaciones mensuales
- `RPT_EXECUTIVE_SUMMARY`: Resumen ejecutivo

## 🔗 Flujo de Datos

```
Landing → Transformation → Reporting
   ↓           ↓              ↓
Raw Data → Clean/Model → Dashboards
```

## 📊 Patrones de Diseño

1. **ELT Pattern**: Extract-Load-Transform
2. **Star Schema**: Dimensiones + Hechos
3. **Slowly Changing Dimensions**: Tipo 2 para dimensiones
4. **Incremental Loading**: Cargas incrementales basadas en timestamps

## 🎯 KPIs Principales

- **Disponibilidad del Sistema**
- **Tiempo de Respuesta**
- **Incidentes de Seguridad**
- **Cumplimiento de SLA**
- **Utilización de Recursos**

## 💡 Recomendaciones

1. **Gobernanza de Datos**:
   - Implementar data quality checks
   - Documentar business rules
   - Establecer data lineage

2. **Performance**:
   - Usar clustering keys en tablas grandes
   - Implementar materialized views
   - Optimizar warehouse sizing

3. **Seguridad**:
   - Row-level security para datos sensibles
   - Auditoría de acceso
   - Encriptación de datos PII

## 📈 Métricas del Schema

- **Total de Objetos**: 11
- **Tablas Base**: 7
- **Views**: 4
- **Relaciones Identificadas**: 12
- **Capas de Datos**: 3

---
*Generado automáticamente por Snowflake ERD Generator*
*Fecha: $(date)*
"""

    with open('snowflake_itseckpi_report.md', 'w', encoding='utf-8') as f:
        f.write(report)

    print("✅ Reporte generado: snowflake_itseckpi_report.md")


if __name__ == "__main__":
    create_snowflake_erd()