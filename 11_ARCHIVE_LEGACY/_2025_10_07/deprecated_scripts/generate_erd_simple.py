#!/usr/bin/env python3
"""
Script simplificado para generar ERD del esquema SECURITY_ANALYTICS
Genera el archivo DOT que puede ser convertido a imagen
"""

import os
from datetime import datetime

def generate_dot_file():
    """Genera archivo DOT con el diagrama ERD"""

    print("="*60)
    print(" GENERANDO ERD - SCHEMA SECURITY_ANALYTICS")
    print("="*60)

    # Contenido del archivo DOT
    dot_content = """digraph "Snowflake ERD - SECURITY_ANALYTICS Schema" {
    rankdir=TB;
    node [shape=none fontname=Arial];
    graph [bgcolor=white pad=0.5 splines=ortho];

    // ========================================
    // DEV_LANDING Layer
    // ========================================
    subgraph cluster_landing {
        label="DEV_LANDING";
        style=filled;
        fillcolor="#FFF5F0";
        fontsize=14;
        fontname="Arial Bold";

        // RAW_KPI_METRICS Table
        landing_RAW_KPI_METRICS [label=<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#FFE5CC">
            <TR><TD COLSPAN="2" BGCOLOR="#FF9933" ALIGN="CENTER">
            <FONT COLOR="WHITE"><B>RAW_KPI_METRICS</B></FONT><BR/>
            <FONT COLOR="WHITE" POINT-SIZE="9">(TABLE)</FONT>
            </TD></TR>
            <TR>
                <TD BGCOLOR="#E8E8E8"><B>Column</B></TD>
                <TD BGCOLOR="#E8E8E8"><B>Type</B></TD>
            </TR>
            <TR><TD ALIGN="LEFT">LOAD_ID</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">NUMBER</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">KPI_CODE</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">VARCHAR(50)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">KPI_VALUE</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">NUMBER(18,2)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">MEASUREMENT_DATE</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">TIMESTAMP</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">SOURCE_SYSTEM</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">VARCHAR(100)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">RAW_DATA</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">VARIANT</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">LOAD_TIMESTAMP</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">TIMESTAMP</FONT></TD></TR>
        </TABLE>>];

        // RAW_SYSTEM_EVENTS Table
        landing_RAW_SYSTEM_EVENTS [label=<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#FFE5CC">
            <TR><TD COLSPAN="2" BGCOLOR="#FF9933" ALIGN="CENTER">
            <FONT COLOR="WHITE"><B>RAW_SYSTEM_EVENTS</B></FONT><BR/>
            <FONT COLOR="WHITE" POINT-SIZE="9">(TABLE)</FONT>
            </TD></TR>
            <TR>
                <TD BGCOLOR="#E8E8E8"><B>Column</B></TD>
                <TD BGCOLOR="#E8E8E8"><B>Type</B></TD>
            </TR>
            <TR><TD ALIGN="LEFT">EVENT_ID</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">VARCHAR(100)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">SYSTEM_ID</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">VARCHAR(50)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">EVENT_TYPE</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">VARCHAR(50)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">EVENT_TIMESTAMP</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">TIMESTAMP</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">EVENT_DATA</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">VARIANT</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">LOAD_DATE</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">DATE</FONT></TD></TR>
        </TABLE>>];
    }

    // ========================================
    // DEV_TRANSFORMATION Layer
    // ========================================
    subgraph cluster_transformation {
        label="DEV_TRANSFORMATION";
        style=filled;
        fillcolor="#F0F5FF";
        fontsize=14;
        fontname="Arial Bold";

        // DIM_KPI Table
        trans_DIM_KPI [label=<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#CCE5FF">
            <TR><TD COLSPAN="2" BGCOLOR="#3399FF" ALIGN="CENTER">
            <FONT COLOR="WHITE"><B>DIM_KPI</B></FONT><BR/>
            <FONT COLOR="WHITE" POINT-SIZE="9">(TABLE)</FONT>
            </TD></TR>
            <TR>
                <TD BGCOLOR="#E8E8E8"><B>Column</B></TD>
                <TD BGCOLOR="#E8E8E8"><B>Type</B></TD>
            </TR>
            <TR><TD ALIGN="LEFT">KPI_KEY</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">NUMBER</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">KPI_CODE</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">VARCHAR(50)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">KPI_NAME</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">VARCHAR(200)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">KPI_CATEGORY</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">VARCHAR(100)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">UNIT_OF_MEASURE</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">VARCHAR(50)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">TARGET_VALUE</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">NUMBER(18,2)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">IS_ACTIVE</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">BOOLEAN</FONT></TD></TR>
        </TABLE>>];

        // DIM_SYSTEM Table
        trans_DIM_SYSTEM [label=<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#CCE5FF">
            <TR><TD COLSPAN="2" BGCOLOR="#3399FF" ALIGN="CENTER">
            <FONT COLOR="WHITE"><B>DIM_SYSTEM</B></FONT><BR/>
            <FONT COLOR="WHITE" POINT-SIZE="9">(TABLE)</FONT>
            </TD></TR>
            <TR>
                <TD BGCOLOR="#E8E8E8"><B>Column</B></TD>
                <TD BGCOLOR="#E8E8E8"><B>Type</B></TD>
            </TR>
            <TR><TD ALIGN="LEFT">SYSTEM_KEY</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">NUMBER</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">SYSTEM_ID</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">VARCHAR(50)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">SYSTEM_NAME</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">VARCHAR(200)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">SYSTEM_TYPE</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">VARCHAR(100)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">DEPARTMENT</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">VARCHAR(100)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">IS_CRITICAL</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">BOOLEAN</FONT></TD></TR>
        </TABLE>>];

        // FACT_KPI_MEASUREMENTS Table
        trans_FACT_KPI_MEASUREMENTS [label=<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#CCE5FF">
            <TR><TD COLSPAN="2" BGCOLOR="#3399FF" ALIGN="CENTER">
            <FONT COLOR="WHITE"><B>FACT_KPI_MEASUREMENTS</B></FONT><BR/>
            <FONT COLOR="WHITE" POINT-SIZE="9">(TABLE)</FONT>
            </TD></TR>
            <TR>
                <TD BGCOLOR="#E8E8E8"><B>Column</B></TD>
                <TD BGCOLOR="#E8E8E8"><B>Type</B></TD>
            </TR>
            <TR><TD ALIGN="LEFT">MEASUREMENT_KEY</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">NUMBER</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">KPI_KEY</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">NUMBER</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">SYSTEM_KEY</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">NUMBER</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">DATE_KEY</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">NUMBER</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">ACTUAL_VALUE</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">NUMBER(18,2)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">TARGET_VALUE</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">NUMBER(18,2)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">VARIANCE_PCT</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">NUMBER(5,2)</FONT></TD></TR>
        </TABLE>>];
    }

    // ========================================
    // DEV_REPORTING Layer
    // ========================================
    subgraph cluster_reporting {
        label="DEV_REPORTING";
        style=filled;
        fillcolor="#F0FFF0";
        fontsize=14;
        fontname="Arial Bold";

        // VW_KPI_DASHBOARD View
        report_VW_KPI_DASHBOARD [label=<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#CCFFCC">
            <TR><TD COLSPAN="2" BGCOLOR="#33CC33" ALIGN="CENTER">
            <FONT COLOR="WHITE"><B>VW_KPI_DASHBOARD</B></FONT><BR/>
            <FONT COLOR="WHITE" POINT-SIZE="9">(VIEW)</FONT>
            </TD></TR>
            <TR>
                <TD BGCOLOR="#E8E8E8"><B>Column</B></TD>
                <TD BGCOLOR="#E8E8E8"><B>Type</B></TD>
            </TR>
            <TR><TD ALIGN="LEFT">KPI_CODE</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">VARCHAR(50)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">KPI_NAME</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">VARCHAR(200)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">CURRENT_VALUE</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">NUMBER(18,2)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">TARGET_VALUE</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">NUMBER(18,2)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">ACHIEVEMENT_PCT</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">NUMBER(5,2)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">TREND</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">VARCHAR(10)</FONT></TD></TR>
        </TABLE>>];

        // AGG_MONTHLY_KPI Table
        report_AGG_MONTHLY_KPI [label=<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#CCFFCC">
            <TR><TD COLSPAN="2" BGCOLOR="#33CC33" ALIGN="CENTER">
            <FONT COLOR="WHITE"><B>AGG_MONTHLY_KPI</B></FONT><BR/>
            <FONT COLOR="WHITE" POINT-SIZE="9">(TABLE)</FONT>
            </TD></TR>
            <TR>
                <TD BGCOLOR="#E8E8E8"><B>Column</B></TD>
                <TD BGCOLOR="#E8E8E8"><B>Type</B></TD>
            </TR>
            <TR><TD ALIGN="LEFT">YEAR_MONTH</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">VARCHAR(7)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">KPI_CODE</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">VARCHAR(50)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">AVG_VALUE</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">NUMBER(18,2)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">MAX_VALUE</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">NUMBER(18,2)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT">MIN_VALUE</TD><TD ALIGN="LEFT"><FONT POINT-SIZE="9">NUMBER(18,2)</FONT></TD></TR>
        </TABLE>>];
    }

    // ========================================
    // Relationships
    // ========================================

    // Landing -> Transformation
    landing_RAW_KPI_METRICS -> trans_DIM_KPI [label=" KPI_CODE " style=dashed color="#FF9933" fontsize=8 fontcolor="#FF9933"];
    landing_RAW_KPI_METRICS -> trans_FACT_KPI_MEASUREMENTS [label=" Load " style=dashed color="#FF9933" fontsize=8 fontcolor="#FF9933"];
    landing_RAW_SYSTEM_EVENTS -> trans_DIM_SYSTEM [label=" SYSTEM_ID " style=dashed color="#FF9933" fontsize=8 fontcolor="#FF9933"];

    // Transformation relationships (Star Schema)
    trans_DIM_KPI -> trans_FACT_KPI_MEASUREMENTS [label=" KPI_KEY " style=solid color="#3399FF" fontsize=8 fontcolor="#3399FF"];
    trans_DIM_SYSTEM -> trans_FACT_KPI_MEASUREMENTS [label=" SYSTEM_KEY " style=solid color="#3399FF" fontsize=8 fontcolor="#3399FF"];

    // Transformation -> Reporting
    trans_FACT_KPI_MEASUREMENTS -> report_VW_KPI_DASHBOARD [label=" Aggregate " style=dotted color="#33CC33" fontsize=8 fontcolor="#33CC33"];
    trans_FACT_KPI_MEASUREMENTS -> report_AGG_MONTHLY_KPI [label=" Aggregate " style=dotted color="#33CC33" fontsize=8 fontcolor="#33CC33"];
    trans_DIM_KPI -> report_VW_KPI_DASHBOARD [label=" Join " style=dotted color="#33CC33" fontsize=8 fontcolor="#33CC33"];
}"""

    # Guardar archivo DOT
    with open('snowflake_itseckpi_erd.dot', 'w', encoding='utf-8') as f:
        f.write(dot_content)

    print("OK Archivo DOT generado: snowflake_itseckpi_erd.dot")

    # Generar reporte
    generate_markdown_report()

    # Generar archivo HTML con visualización
    generate_html_viewer()

    print("\n" + "="*60)
    print(" PROCESO COMPLETADO")
    print("="*60)
    print("\nArchivos generados:")
    print("  - snowflake_itseckpi_erd.dot (Archivo fuente)")
    print("  - snowflake_itseckpi_report.md (Documentacion)")
    print("  - snowflake_itseckpi_viewer.html (Visualizador web)")
    print("\n" + "="*60)
    print(" PARA GENERAR EL DIAGRAMA VISUAL:")
    print("="*60)
    print("\nOpcion 1: Instalar Graphviz")
    print("  1. Descargar: https://graphviz.org/download/")
    print("  2. Instalar y reiniciar el terminal")
    print("  3. Ejecutar: dot -Tpng snowflake_itseckpi_erd.dot -o erd.png")
    print("\nOpcion 2: Usar herramienta online")
    print("  1. Ir a: https://dreampuf.github.io/GraphvizOnline/")
    print("  2. Copiar el contenido de snowflake_itseckpi_erd.dot")
    print("  3. Pegar y visualizar")
    print("\nOpcion 3: Abrir snowflake_itseckpi_viewer.html en tu navegador")

def generate_markdown_report():
    """Genera reporte en Markdown"""

    report = f"""# Snowflake ERD Report - SECURITY_ANALYTICS Schema

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
*Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""

    with open('snowflake_itseckpi_report.md', 'w', encoding='utf-8') as f:
        f.write(report)

    print("OK Reporte generado: snowflake_itseckpi_report.md")

def generate_html_viewer():
    """Genera un visualizador HTML usando Viz.js"""

    # Leer el contenido del archivo DOT
    with open('snowflake_itseckpi_erd.dot', 'r', encoding='utf-8') as f:
        dot_content = f.read()

    html_content = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Snowflake ERD - SECURITY_ANALYTICS Schema</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/viz.js/2.1.2/viz.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/viz.js/2.1.2/full.render.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        #graph {
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            overflow: auto;
            text-align: center;
        }
        .info {
            background: #e8f4ff;
            border: 1px solid #0066cc;
            border-radius: 4px;
            padding: 15px;
            margin: 20px 0;
        }
        .loading {
            text-align: center;
            padding: 50px;
            color: #666;
        }
        svg {
            max-width: 100%;
            height: auto;
        }
    </style>
</head>
<body>
    <h1>Snowflake ERD - SECURITY_ANALYTICS Schema</h1>

    <div class="info">
        <strong>Visualizacion del Esquema SECURITY_ANALYTICS</strong><br>
        Este diagrama muestra las relaciones entre las tablas en las 3 capas:
        DEV_LANDING, DEV_TRANSFORMATION y DEV_REPORTING
    </div>

    <div id="graph">
        <div class="loading">Cargando diagrama...</div>
    </div>

    <script>
        // DOT content embedded
        const dotContent = `""" + dot_content + """`;

        // Render the graph
        try {
            var viz = new Viz();
            viz.renderSVGElement(dotContent)
                .then(function(element) {
                    document.getElementById('graph').innerHTML = '';
                    document.getElementById('graph').appendChild(element);
                })
                .catch(function(error) {
                    document.getElementById('graph').innerHTML =
                        '<div style="color: red; padding: 20px;">Error al renderizar el diagrama: ' + error + '</div>';
                });
        } catch(e) {
            document.getElementById('graph').innerHTML =
                '<div style="color: red; padding: 20px;">Error: ' + e + '</div>';
        }
    </script>
</body>
</html>"""

    with open('snowflake_itseckpi_viewer.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("OK Visualizador HTML generado: snowflake_itseckpi_viewer.html")

if __name__ == "__main__":
    generate_dot_file()