#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Snowflake ERD Complete Extractor
Extrae metadata completa de Snowflake y genera ERDs en múltiples formatos
con documentación exhaustiva y análisis de calidad.
"""

import snowflake.connector
import pandas as pd
import networkx as nx
from datetime import datetime
import json
import logging
import os
import sys
from pathlib import Path
import getpass
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Configure logging
def setup_logging():
    """Configura el sistema de logging"""
    log_dir = Path("snowflake_erd_output/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"extraction_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

class SnowflakeERDExtractor:
    """Extractor completo de metadata y generador de ERDs for Snowflake"""

    def __init__(self, connection_forms: dict):
        """Initialize el extractor with parameters of connection"""
        self.connection_forms = connection_forms
        self.conn = None
        self.cursor = None
        self.metadata = {
            'tables': {},
            'columns': {},
            'constraints': {},
            'relationships': {},
            'views': {},
            'statistics': {},
            'data_lineage': {}
        }
        self.layers = {
            'landing': {'prefix': 'L_', 'color': '#3399FF', 'tables': []},
            'transformation': {'prefix': 'T_', 'color': '#FFFF33', 'tables': []},
            'reporting': {'prefix': 'R_', 'color': '#33CC33', 'tables': []}
        }

    def connect(self):
        """Establish connection con Snowflake"""
        try:
            logger.info("Conectando a Snowflake...")
            self.conn = snowflake.connector.connect(
                account=self.connection_forms['account'],
                user=self.connection_forms['user'],
                password=self.connection_forms['password'],
                warehouse=self.connection_forms['warehouse'],
                database=self.connection_forms['database'],
                schema=self.connection_forms['schema']
            )
            self.cursor = self.conn.cursor()
            logger.info("Conexión establecida exitosamente")

            # Verificar el esquema actual
            self.cursor.execute("SELECT CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA()")
            result = self.cursor.fetchone()
            logger.info(f"Contexto: Warehouse={result[0]}, Database={result[1]}, Schema={result[2]}")

        except Exception as e:
            logger.error(f"Error al conectar a Snowflake: {str(e)}")
            raise

    def extract_tables_metadata(self):
        """Extrae metadata de todas las tables del esquema"""
        logger.info("Extrayendo metadata de tables...")

        query = """
        SELECT
            TABLE_CATALOG,
            TABLE_SCHEMA,
            TABLE_NAME,
            TABLE_TYPE,
            ROW_COUNT,
            BYTES,
            CREATED,
            LAST_ALTERED,
            COMMENT
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = UPPER(%(schema)s)
        ORDER BY TABLE_NAME
        """

        try:
            self.cursor.execute(query, {'schema': self.connection_forms['schema']})
            tables = self.cursor.fetchall()

            for table in tables:
                table_name = table[2]
                self.metadata['tables'][table_name] = {
                    'catalog': table[0],
                    'schema': table[1],
                    'name': table[2],
                    'type': table[3],
                    'row_count': table[4],
                    'bytes': table[5],
                    'createted': str(table[6]) if table[6] else None,
                    'last_altered': str(table[7]) if table[7] else None,
                    'comment': table[8],
                    'layer': self._identify_layer(table_name)
                }

                # Clasificar por capa
                layer = self._identify_layer(table_name)
                if layer:
                    self.layers[layer]['tables'].append(table_name)

            logger.info(f"Extraídas {len(tables)} tables")
            logger.info(f"  - Landing: {len(self.layers['landing']['tables'])} tables")
            logger.info(f"  - Transformation: {len(self.layers['transformation']['tables'])} tables")
            logger.info(f"  - Reporting: {len(self.layers['reporting']['tables'])} tables")

        except Exception as e:
            logger.error(f"Error extrayendo metadata de tables: {str(e)}")
            raise

    def extract_columns_metadata(self):
        """Extrae metadata de todas las columns"""
        logger.info("Extrayendo metadata de columns...")

        query = """
        SELECT
            TABLE_NAME,
            COLUMN_NAME,
            ORDINAL_POSITION,
            COLUMN_DEFAULT,
            IS_NULLABLE,
            DATA_TYPE,
            CHARACTER_MAXIMUM_LENGTH,
            NUMERIC_PRECISION,
            NUMERIC_SCALE,
            COMMENT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = UPPER(%(schema)s)
        ORDER BY TABLE_NAME, ORDINAL_POSITION
        """

        try:
            self.cursor.execute(query, {'schema': self.connection_forms['schema']})
            columns = self.cursor.fetchall()

            for col in columns:
                table_name = col[0]
                if table_name not in self.metadata['columns']:
                    self.metadata['columns'][table_name] = []

                self.metadata['columns'][table_name].append({
                    'column_name': col[1],
                    'ordinal_position': col[2],
                    'column_default': col[3],
                    'is_nullable': col[4],
                    'data_type': col[5],
                    'max_length': col[6],
                    'numeric_precision': col[7],
                    'numeric_scale': col[8],
                    'comment': col[9]
                })

            logger.info(f"Extraídas columns de {len(self.metadata['columns'])} tables")

        except Exception as e:
            logger.error(f"Error extrayendo metadata de columns: {str(e)}")
            raise

    def extract_constraints_and_relationships(self):
        """Extrae constraints y relaciones entre tables"""
        logger.info("Extrayendo constraints y relaciones...")

        # Primary Keys y Unique constraints
        pk_query = """
        SELECT DISTINCT
            tc.TABLE_NAME,
            tc.CONSTRAINT_NAME,
            tc.CONSTRAINT_TYPE,
            LISTAGG(kcu.COLUMN_NAME, ', ') WITHIN GROUP (ORDER BY kcu.ORDINAL_POSITION) as COLUMNS
        FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
        JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
            ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
            AND tc.TABLE_SCHEMA = kcu.TABLE_SCHEMA
        WHERE tc.TABLE_SCHEMA = UPPER(%(schema)s)
            AND tc.CONSTRAINT_TYPE IN ('PRIMARY KEY', 'UNIQUE')
        GROUP BY tc.TABLE_NAME, tc.CONSTRAINT_NAME, tc.CONSTRAINT_TYPE
        """

        try:
            self.cursor.execute(pk_query, {'schema': self.connection_forms['schema']})
            constraints = self.cursor.fetchall()

            for constraint in constraints:
                table_name = constraint[0]
                if table_name not in self.metadata['constraints']:
                    self.metadata['constraints'][table_name] = []

                self.metadata['constraints'][table_name].append({
                    'constraint_name': constraint[1],
                    'constraint_type': constraint[2],
                    'columns': constraint[3]
                })

            logger.info(f"Extraídos constraints de {len(self.metadata['constraints'])} tables")

            # Detectar relaciones implícitas basadas en nombres
            self._detect_implicit_relationships()

        except Exception as e:
            logger.error(f"Error extrayendo constraints: {str(e)}")
            raise

    def extract_views_metadata(self):
        """Extrae metadata de vistas y sus dependencias"""
        logger.info("Extrayendo metadata de vistas...")

        query = """
        SELECT
            TABLE_NAME as VIEW_NAME,
            VIEW_DEFINITION
        FROM INFORMATION_SCHEMA.VIEWS
        WHERE TABLE_SCHEMA = UPPER(%(schema)s)
        """

        try:
            self.cursor.execute(query, {'schema': self.connection_forms['schema']})
            views = self.cursor.fetchall()

            for view in views:
                view_name = view[0]
                self.metadata['views'][view_name] = {
                    'definition': view[1],
                    'dependencies': self._extract_view_dependencies(view[1])
                }

            logger.info(f"Extraídas {len(views)} vistas")

        except Exception as e:
            logger.error(f"Error extrayendo metadata de vistas: {str(e)}")
            # No es crítico si falla
            pass

    def analyze_data_lineage(self):
        """Analiza el linaje de data entre las capas"""
        logger.info("Analizando linaje de data entre capas...")

        self.metadata['data_lineage'] = {
            'landing_to_transform': [],
            'transform_to_reporting': [],
            'cross_layer_dependencies': []
        }

        # Analizar flujos basados en nombres y patrones
        for landing_table in self.layers['landing']['tables']:
            # Buscar tables relacionadas en transformation
            base_name = landing_table.replace('L_', '')
            transform_candidates = [t for t in self.layers['transformation']['tables']
                                   if base_name.lower() in t.lower()]

            for transform_table in transform_candidates:
                self.metadata['data_lineage']['landing_to_transform'].append({
                    'source': landing_table,
                    'target': transform_table,
                    'confidence': 'high' if base_name.lower() == transform_table.replace('T_', '').lower() else 'medium'
                })

        # Similar for transformation a reporting
        for transform_table in self.layers['transformation']['tables']:
            base_name = transform_table.replace('T_', '')
            reporting_candidates = [t for t in self.layers['reporting']['tables']
                                  if base_name.lower() in t.lower()]

            for reporting_table in reporting_candidates:
                self.metadata['data_lineage']['transform_to_reporting'].append({
                    'source': transform_table,
                    'target': reporting_table,
                    'confidence': 'high' if base_name.lower() == reporting_table.replace('R_', '').lower() else 'medium'
                })

        logger.info(f"Identificados {len(self.metadata['data_lineage']['landing_to_transform'])} flujos Landing->Transform")
        logger.info(f"Identificados {len(self.metadata['data_lineage']['transform_to_reporting'])} flujos Transform->Reporting")

    def perform_quality_checks(self):
        """Realiza validaciones de calidad en el esquema"""
        logger.info("Realizando validaciones de calidad...")

        issues = {
            'orphaned_tables': [],
            'missing_primary_keys': [],
            'naming_inconsistencies': [],
            'unused_columns': [],
            'duplicate_patterns': []
        }

        # Tablas huérfanas (sin relaciones)
        for table_name in self.metadata['tables']:
            if table_name not in self.metadata['relationships']:
                has_relationships = False
                for _, rels in self.metadata['relationships'].items():
                    if any(r['target_table'] == table_name for r in rels):
                        has_relationships = True
                        break

                if not has_relationships:
                    issues['orphaned_tables'].append(table_name)

        # Tablas sin primary key
        for table_name in self.metadata['tables']:
            if table_name not in self.metadata['constraints']:
                issues['missing_primary_keys'].append(table_name)
            else:
                has_pk = any(c['constraint_type'] == 'PRIMARY KEY'
                           for c in self.metadata['constraints'][table_name])
                if not has_pk:
                    issues['missing_primary_keys'].append(table_name)

        # Inconsistencias de nomenclatura
        for table_name in self.metadata['tables']:
            layer = self._identify_layer(table_name)
            if not layer and not table_name.startswith(('VW_', 'V_')):
                issues['naming_inconsistencies'].append({
                    'table': table_name,
                    'issue': 'No sigue convención de prefijos (L_, T_, R_)'
                })

        self.metadata['quality_issues'] = issues

        logger.info(f"Validaciones completadas:")
        logger.info(f"  - Tablas huérfanas: {len(issues['orphaned_tables'])}")
        logger.info(f"  - Sin primary key: {len(issues['missing_primary_keys'])}")
        logger.info(f"  - Inconsistencias de nomenclatura: {len(issues['naming_inconsistencies'])}")

    def generate_mermaid_erd(self, layer: Optional[str] = None) -> str:
        """Genera diagrama ERD en formato Mermaid"""
        logger.info(f"Generando ERD Mermaid for capa: {layer or 'completo'}")

        mermaid = ["erDiagram"]

        # Filtrar tables por capa si se especifica
        tables_to_include = []
        if layer:
            tables_to_include = self.layers[layer]['tables']
        else:
            tables_to_include = list(self.metadata['tables'].keys())

        # Agregar entidades
        for table_name in tables_to_include:
            if table_name in self.metadata['columns']:
                mermaid.append(f"    {table_name} {{")
                for col in self.metadata['columns'][table_name][:10]:  # Limitar a 10 columns
                    dtype = col['data_type']
                    nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                    mermaid.append(f"        {dtype} {col['column_name']} \"{nullable}\"")
                mermaid.append("    }")

        # Agregar relaciones
        for source_table, relationships in self.metadata['relationships'].items():
            if source_table in tables_to_include:
                for rel in relationships:
                    if rel['target_table'] in tables_to_include:
                        mermaid.append(f"    {source_table} ||--o{{ {rel['target_table']} : \"{rel['relationship_type']}\"")

        return "\n".join(mermaid)

    def generate_plantuml_erd(self, layer: Optional[str] = None) -> str:
        """Genera diagrama ERD en formato PlantUML"""
        logger.info(f"Generando ERD PlantUML for capa: {layer or 'completo'}")

        plantuml = ["@startuml"]
        plantuml.append("!define Table(name,desc) class name as desc << (T,#FFAAAA) >>")
        plantuml.append("!define primary_key(x) <b>x</b>")
        plantuml.append("!define foreign_key(x) <i>x</i>")
        plantuml.append("hide methods")
        plantuml.append("hide stereotypes")

        # Filtrar tables por capa
        tables_to_include = []
        if layer:
            tables_to_include = self.layers[layer]['tables']
            color = self.layers[layer]['color']
            plantuml.append(f"skinform class BackgroundColor {color}")
        else:
            tables_to_include = list(self.metadata['tables'].keys())

        # Agregar entidades
        for table_name in tables_to_include:
            if table_name in self.metadata['columns']:
                plantuml.append(f"class {table_name} {{")

                # Identificar PKs
                pk_columns = []
                if table_name in self.metadata['constraints']:
                    for constraint in self.metadata['constraints'][table_name]:
                        if constraint['constraint_type'] == 'PRIMARY KEY':
                            pk_columns = constraint['columns'].split(', ')

                # Agregar columns
                for col in self.metadata['columns'][table_name]:
                    col_name = col['column_name']
                    if col_name in pk_columns:
                        plantuml.append(f"  primary_key({col_name}) : {col['data_type']}")
                    else:
                        plantuml.append(f"  {col_name} : {col['data_type']}")

                plantuml.append("}")

        # Agregar relaciones
        for source_table, relationships in self.metadata['relationships'].items():
            if source_table in tables_to_include:
                for rel in relationships:
                    if rel['target_table'] in tables_to_include:
                        plantuml.append(f"{source_table} --> {rel['target_table']}")

        plantuml.append("@enduml")
        return "\n".join(plantuml)

    def generate_dbml(self, layer: Optional[str] = None) -> str:
        """Genera esquema en formato DBML for dbdiagram.io"""
        logger.info(f"Generando DBML for capa: {layer or 'completo'}")

        dbml = []
        dbml.append(f"// DBML Schema for {self.connection_forms['schema']}")
        dbml.append(f"// Generated: {datetime.now().isoformat()}")
        dbml.append("")

        # Filtrar tables por capa
        tables_to_include = []
        if layer:
            tables_to_include = self.layers[layer]['tables']
            dbml.append(f"// Layer: {layer.upper()}")
        else:
            tables_to_include = list(self.metadata['tables'].keys())

        # Agregar tables
        for table_name in tables_to_include:
            if table_name in self.metadata['columns']:
                table_info = self.metadata['tables'].get(table_name, {})

                dbml.append(f"Table {table_name} {{")

                # Nota con information de la table
                if table_info.get('comment'):
                    dbml.append(f"  Note: '{table_info['comment']}'")

                # Columnas
                for col in self.metadata['columns'][table_name]:
                    col_def = f"  {col['column_name']} {col['data_type']}"

                    # Agregar modificadores
                    modifiers = []
                    if col['is_nullable'] == 'NO':
                        modifiers.append('not null')
                    if col['column_default']:
                        modifiers.append(f"default: {col['column_default']}")

                    if modifiers:
                        col_def += f" [{', '.join(modifiers)}]"

                    dbml.append(col_def)

                dbml.append("}")
                dbml.append("")

        # Agregar referencias (foreign keys)
        dbml.append("// References")
        for source_table, relationships in self.metadata['relationships'].items():
            if source_table in tables_to_include:
                for rel in relationships:
                    if rel['target_table'] in tables_to_include:
                        dbml.append(f"Ref: {source_table}.{rel['source_column']} > {rel['target_table']}.{rel['target_column']}")

        return "\n".join(dbml)

    def generate_graphviz_dot(self, layer: Optional[str] = None) -> str:
        """Genera diagrama en formato DOT de Graphviz"""
        logger.info(f"Generando DOT for capa: {layer or 'completo'}")

        dot = []
        dot.append("digraph ERD {")
        dot.append('  rankdir=LR;')
        dot.append('  node [shape=record, style=filled];')
        dot.append('  edge [arrowhead=crow];')

        # Filtrar tables por capa
        tables_to_include = []
        if layer:
            tables_to_include = self.layers[layer]['tables']
            color = self.layers[layer]['color']
        else:
            tables_to_include = list(self.metadata['tables'].keys())

        # Agregar nodos (tables)
        for table_name in tables_to_include:
            if table_name in self.metadata['columns']:
                # Determinar color
                table_layer = self._identify_layer(table_name)
                if table_layer:
                    fillcolor = self.layers[table_layer]['color']
                else:
                    fillcolor = '#FFFFFF'

                # Construir label de la table
                columns = []
                for col in self.metadata['columns'][table_name][:15]:  # Limitar columns
                    col_str = f"{col['column_name']} : {col['data_type']}"
                    columns.append(col_str)

                label = f"{table_name}|" + "\\l".join(columns) + "\\l"

                dot.append(f'  "{table_name}" [label="{{{label}}}", fillcolor="{fillcolor}"];')

        # Agregar edges (relaciones)
        for source_table, relationships in self.metadata['relationships'].items():
            if source_table in tables_to_include:
                for rel in relationships:
                    if rel['target_table'] in tables_to_include:
                        dot.append(f'  "{source_table}" -> "{rel["target_table"]}" [label="{rel["relationship_type"]}"];')

        dot.append("}")
        return "\n".join(dot)

    def createte_excel_documentation(self):
        """Create documentación completa en Excel"""
        logger.info("Createndo documentación Excel...")

        output_dir = Path("snowflake_erd_output/documentation")
        output_dir.mkdir(parents=True, exist_ok=True)

        excel_file = output_dir / f"snowflake_erd_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # 1. Overview
            overview_data = {
                'Metric': [
                    'Total Tables',
                    'Landing Tables',
                    'Transformation Tables',
                    'Reporting Tables',
                    'Total Views',
                    'Total Columns',
                    'Orphaned Tables',
                    'Tables without PK'
                ],
                'Value': [
                    len(self.metadata['tables']),
                    len(self.layers['landing']['tables']),
                    len(self.layers['transformation']['tables']),
                    len(self.layers['reporting']['tables']),
                    len(self.metadata['views']),
                    sum(len(cols) for cols in self.metadata['columns'].values()),
                    len(self.metadata.get('quality_issues', {}).get('orphaned_tables', [])),
                    len(self.metadata.get('quality_issues', {}).get('missing_primary_keys', []))
                ]
            }
            pd.DataFrame(overview_data).to_excel(writer, sheet_name='Overview', index=False)

            # 2. Tables
            tables_data = []
            for table_name, table_info in self.metadata['tables'].items():
                tables_data.append({
                    'Table Name': table_name,
                    'Layer': self._identify_layer(table_name) or 'Unknown',
                    'Type': table_info['type'],
                    'Row Count': table_info['row_count'],
                    'Size (MB)': round(table_info['bytes'] / 1024 / 1024, 2) if table_info['bytes'] else 0,
                    'Createted': table_info['createted'],
                    'Last Modified': table_info['last_altered'],
                    'Comment': table_info['comment']
                })
            pd.DataFrame(tables_data).to_excel(writer, sheet_name='Tables', index=False)

            # 3. Columns
            columns_data = []
            for table_name, columns in self.metadata['columns'].items():
                for col in columns:
                    columns_data.append({
                        'Table': table_name,
                        'Column': col['column_name'],
                        'Position': col['ordinal_position'],
                        'Data Type': col['data_type'],
                        'Nullable': col['is_nullable'],
                        'Default': col['column_default'],
                        'Comment': col['comment']
                    })
            pd.DataFrame(columns_data).to_excel(writer, sheet_name='Columns', index=False)

            # 4. Relationships
            relationships_data = []
            for source_table, rels in self.metadata['relationships'].items():
                for rel in rels:
                    relationships_data.append({
                        'Source Table': source_table,
                        'Source Column': rel['source_column'],
                        'Target Table': rel['target_table'],
                        'Target Column': rel['target_column'],
                        'Type': rel['relationship_type'],
                        'Confidence': rel.get('confidence', 'detected')
                    })
            pd.DataFrame(relationships_data).to_excel(writer, sheet_name='Relationships', index=False)

            # 5. Data Lineage
            lineage_data = []
            for flow_type, flows in self.metadata.get('data_lineage', {}).items():
                if isinstance(flows, list):
                    for flow in flows:
                        lineage_data.append({
                            'Flow Type': flow_type.replace('_', ' ').title(),
                            'Source': flow['source'],
                            'Target': flow['target'],
                            'Confidence': flow.get('confidence', 'medium')
                        })
            pd.DataFrame(lineage_data).to_excel(writer, sheet_name='Data Lineage', index=False)

            # 6. Issues
            issues_data = []
            for issue_type, issue_list in self.metadata.get('quality_issues', {}).items():
                if isinstance(issue_list, list):
                    for item in issue_list:
                        if isinstance(item, dict):
                            issues_data.append({
                                'Issue Type': issue_type.replace('_', ' ').title(),
                                'Object': item.get('table', ''),
                                'Description': item.get('issue', '')
                            })
                        else:
                            issues_data.append({
                                'Issue Type': issue_type.replace('_', ' ').title(),
                                'Object': item,
                                'Description': ''
                            })
            pd.DataFrame(issues_data).to_excel(writer, sheet_name='Issues', index=False)

        logger.info(f"Documentación Excel createda: {excel_file}")

    def createte_markdown_documentation(self):
        """Genera documentación completa en Markdown"""
        logger.info("Createndo documentación Markdown...")

        output_dir = Path("snowflake_erd_output/documentation")
        output_dir.mkdir(parents=True, exist_ok=True)

        md_file = output_dir / f"database_documentation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        md = []
        md.append(f"# Documentación del Esquema {self.connection_forms['schema'].upper()}")
        md.append(f"\nGenerado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # 1. Resumen Ejecutivo
        md.append("## 1. Resumen Ejecutivo\n")
        md.append(f"- **Total de tables**: {len(self.metadata['tables'])}")
        md.append(f"- **Tablas Landing**: {len(self.layers['landing']['tables'])}")
        md.append(f"- **Tablas Transformation**: {len(self.layers['transformation']['tables'])}")
        md.append(f"- **Tablas Reporting**: {len(self.layers['reporting']['tables'])}")
        md.append(f"- **Total de vistas**: {len(self.metadata['views'])}")
        md.append(f"- **Total de columns**: {sum(len(cols) for cols in self.metadata['columns'].values())}")

        total_bytes = sum(t['bytes'] for t in self.metadata['tables'].values() if t['bytes'])
        md.append(f"- **Volumen total de data**: {round(total_bytes / 1024 / 1024 / 1024, 2)} GB")

        # 2. Landing Layer
        md.append("\n## 2. Landing Layer\n")
        md.append("### 2.1 Propósito")
        md.append("Capa de ingesta de data crudos from sistemas fuente.\n")

        md.append("### 2.2 Tablas\n")
        if self.layers['landing']['tables']:
            md.append("| Tabla | Filas | Tamaño (MB) | Descripción |")
            md.append("|-------|-------|-------------|-------------|")
            for table_name in sorted(self.layers['landing']['tables']):
                info = self.metadata['tables'][table_name]
                size_mb = round(info['bytes'] / 1024 / 1024, 2) if info['bytes'] else 0
                md.append(f"| {table_name} | {info['row_count'] or 0:,} | {size_mb:,.2f} | {info['comment'] or 'N/A'} |")
        else:
            md.append("*No se encontraron tables en la capa Landing*")

        md.append("\n### 2.3 ERD Landing Layer\n")
        md.append("```mermaid")
        md.append(self.generate_mermaid_erd('landing'))
        md.append("```")

        # 3. Transformation Layer
        md.append("\n## 3. Transformation Layer\n")
        md.append("### 3.1 Propósito")
        md.append("Capa de transformación con modelado dimensional (estrella/copo de nieve).\n")

        md.append("### 3.2 Tablas\n")
        if self.layers['transformation']['tables']:
            md.append("| Tabla | Filas | Tamaño (MB) | Descripción |")
            md.append("|-------|-------|-------------|-------------|")
            for table_name in sorted(self.layers['transformation']['tables']):
                info = self.metadata['tables'][table_name]
                size_mb = round(info['bytes'] / 1024 / 1024, 2) if info['bytes'] else 0
                md.append(f"| {table_name} | {info['row_count'] or 0:,} | {size_mb:,.2f} | {info['comment'] or 'N/A'} |")
        else:
            md.append("*No se encontraron tables en la capa Transformation*")

        md.append("\n### 3.3 ERD Transformation Layer\n")
        md.append("```mermaid")
        md.append(self.generate_mermaid_erd('transformation'))
        md.append("```")

        # 4. Reporting Layer
        md.append("\n## 4. Reporting Layer\n")
        md.append("### 4.1 Propósito")
        md.append("Capa de reportes y agregaciones for consumo final.\n")

        md.append("### 4.2 Tablas y Vistas\n")
        if self.layers['reporting']['tables']:
            md.append("| Objeto | Tipo | Filas | Descripción |")
            md.append("|--------|------|-------|-------------|")
            for table_name in sorted(self.layers['reporting']['tables']):
                info = self.metadata['tables'][table_name]
                md.append(f"| {table_name} | {info['type']} | {info['row_count'] or 'N/A'} | {info['comment'] or 'N/A'} |")
        else:
            md.append("*No se encontraron objetos en la capa Reporting*")

        md.append("\n### 4.3 ERD Reporting Layer\n")
        md.append("```mermaid")
        md.append(self.generate_mermaid_erd('reporting'))
        md.append("```")

        # 5. Data Lineage
        md.append("\n## 5. Data Lineage\n")
        md.append("### 5.1 Flujo Landing → Transformation\n")

        lineage = self.metadata.get('data_lineage', {})
        if lineage.get('landing_to_transform'):
            md.append("| Origen (Landing) | Destino (Transform) | Confianza |")
            md.append("|------------------|---------------------|-----------|")
            for flow in lineage['landing_to_transform']:
                md.append(f"| {flow['source']} | {flow['target']} | {flow['confidence']} |")
        else:
            md.append("*No se detectaron flujos directos*")

        md.append("\n### 5.2 Flujo Transformation → Reporting\n")
        if lineage.get('transform_to_reporting'):
            md.append("| Origen (Transform) | Destino (Reporting) | Confianza |")
            md.append("|-------------------|---------------------|-----------|")
            for flow in lineage['transform_to_reporting']:
                md.append(f"| {flow['source']} | {flow['target']} | {flow['confidence']} |")
        else:
            md.append("*No se detectaron flujos directos*")

        # 6. Diccionario de Datos (Top 20 tables importantes)
        md.append("\n## 6. Diccionario de Datos\n")
        md.append("### Principales Entidades del Sistema\n")

        # Seleccionar las tables más importantes (con más columns o relaciones)
        important_tables = sorted(
            self.metadata['tables'].keys(),
            key=lambda x: len(self.metadata['columns'].get(x, [])),
            reverse=True
        )[:5]

        for table_name in important_tables:
            md.append(f"\n#### {table_name}")
            info = self.metadata['tables'][table_name]
            if info['comment']:
                md.append(f"*{info['comment']}*\n")

            md.append("| Columna | Tipo | Nullable | Descripción |")
            md.append("|---------|------|----------|-------------|")

            for col in self.metadata['columns'].get(table_name, [])[:15]:
                md.append(f"| {col['column_name']} | {col['data_type']} | {col['is_nullable']} | {col['comment'] or ''} |")

        # 7. Reglas de Negocio
        md.append("\n## 7. Reglas de Negocio Identifieachs\n")

        # Analizar constraints
        md.append("### 7.1 Constraints y Validaciones\n")
        constraint_count = sum(len(c) for c in self.metadata['constraints'].values())
        md.append(f"- Total de constraints definidos: {constraint_count}")

        pk_tables = [t for t, c in self.metadata['constraints'].items()
                    if any(con['constraint_type'] == 'PRIMARY KEY' for con in c)]
        md.append(f"- Tablas con Primary Key: {len(pk_tables)}")

        # 8. Recomendaciones
        md.append("\n## 8. Recomendaciones de Optimización\n")

        issues = self.metadata.get('quality_issues', {})

        if issues.get('orphaned_tables'):
            md.append(f"\n### 8.1 Tablas Huérfanas ({len(issues['orphaned_tables'])})")
            md.append("Las followings tables no tienen relaciones detectadas:")
            for table in issues['orphaned_tables'][:10]:
                md.append(f"- {table}")

        if issues.get('missing_primary_keys'):
            md.append(f"\n### 8.2 Tablas sin Primary Key ({len(issues['missing_primary_keys'])})")
            md.append("Se recomienda agregar primary keys a:")
            for table in issues['missing_primary_keys'][:10]:
                md.append(f"- {table}")

        if issues.get('naming_inconsistencies'):
            md.append(f"\n### 8.3 Inconsistencias de Nomenclatura ({len(issues['naming_inconsistencies'])})")
            md.append("Las followings tables no siguen el estándar de nomenclatura:")
            for item in issues['naming_inconsistencies'][:10]:
                md.append(f"- {item['table']}: {item['issue']}")

        # Guardar file
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md))

        logger.info(f"Documentación Markdown createda: {md_file}")

    def save_all_diagrams(self):
        """Guarda all los diagramas en diferentes formatos"""
        logger.info("Generando all los diagramas...")

        diagrams_dir = Path("snowflake_erd_output/diagrams")
        diagrams_dir.mkdir(parents=True, exist_ok=True)

        scripts_dir = Path("snowflake_erd_output/scripts")
        scripts_dir.mkdir(parents=True, exist_ok=True)

        # Generate diagramas for each capa y el completo
        for layer in [None, 'landing', 'transformation', 'reporting']:
            layer_name = layer or 'full_schema'

            # Mermaid
            mermaid_file = scripts_dir / f"mermaid_{layer_name}.md"
            with open(mermaid_file, 'w', encoding='utf-8') as f:
                f.write(f"# ERD {layer_name.replace('_', ' ').title()}\n\n")
                f.write("```mermaid\n")
                f.write(self.generate_mermaid_erd(layer))
                f.write("\n```")

            # PlantUML
            plantuml_file = scripts_dir / f"plantuml_{layer_name}.puml"
            with open(plantuml_file, 'w', encoding='utf-8') as f:
                f.write(self.generate_plantuml_erd(layer))

            # DBML
            dbml_file = scripts_dir / f"dbml_{layer_name}.dbml"
            with open(dbml_file, 'w', encoding='utf-8') as f:
                f.write(self.generate_dbml(layer))

            # Graphviz DOT
            dot_file = diagrams_dir / f"{layer_name}.dot"
            with open(dot_file, 'w', encoding='utf-8') as f:
                f.write(self.generate_graphviz_dot(layer))

            # Intentar generate PNG from DOT si graphviz está instalado
            try:
                import graphviz
                graph = graphviz.Source(self.generate_graphviz_dot(layer))
                graph.render(filename=f"{layer_name}", directory=str(diagrams_dir),
                           format='png', cleanup=True)
                logger.info(f"PNG generado for {layer_name}")
            except Exception as e:
                logger.warning(f"No se pudo generate PNG for {layer_name}: {str(e)}")

        # Generate diagrama de flujo de data
        self._generate_data_flow_diagram()

    def _generate_data_flow_diagram(self):
        """Genera diagrama de flujo de data entre capas"""
        logger.info("Generando diagrama de flujo de data...")

        diagrams_dir = Path("snowflake_erd_output/diagrams")

        mermaid_flow = ["graph LR"]
        mermaid_flow.append("    subgraph Landing[Landing Layer]")
        for table in self.layers['landing']['tables'][:5]:
            mermaid_flow.append(f"        {table}")
        mermaid_flow.append("    end")

        mermaid_flow.append("    subgraph Transform[Transformation Layer]")
        for table in self.layers['transformation']['tables'][:5]:
            mermaid_flow.append(f"        {table}")
        mermaid_flow.append("    end")

        mermaid_flow.append("    subgraph Reporting[Reporting Layer]")
        for table in self.layers['reporting']['tables'][:5]:
            mermaid_flow.append(f"        {table}")
        mermaid_flow.append("    end")

        # Agregar flujos
        for flow in self.metadata.get('data_lineage', {}).get('landing_to_transform', [])[:10]:
            mermaid_flow.append(f"    {flow['source']} --> {flow['target']}")

        for flow in self.metadata.get('data_lineage', {}).get('transform_to_reporting', [])[:10]:
            mermaid_flow.append(f"    {flow['source']} --> {flow['target']}")

        flow_file = diagrams_dir / "data_flow.md"
        with open(flow_file, 'w', encoding='utf-8') as f:
            f.write("# Data Flow Diagram\n\n")
            f.write("```mermaid\n")
            f.write('\n'.join(mermaid_flow))
            f.write("\n```")

    def save_metadata_json(self):
        """Guarda toda la metadata en formato JSON"""
        output_dir = Path("snowflake_erd_output/documentation")
        output_dir.mkdir(parents=True, exist_ok=True)

        json_file = output_dir / f"metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # Convertir datetime a string en metadata
        def serialize(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return str(obj)

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, default=serialize)

        logger.info(f"Metadata JSON guardada: {json_file}")

    def _identify_layer(self, table_name: str) -> Optional[str]:
        """Identifica a qué capa pertenece una table basándose en su nombre"""
        table_upper = table_name.upper()

        if table_upper.startswith('L_') or 'LANDING' in table_upper or 'RAW' in table_upper:
            return 'landing'
        elif table_upper.startswith('T_') or 'TRANSFORM' in table_upper or 'DIM_' in table_upper or 'FACT_' in table_upper:
            return 'transformation'
        elif table_upper.startswith('R_') or 'REPORT' in table_upper or table_upper.startswith('VW_') or table_upper.startswith('V_'):
            return 'reporting'

        # Verificar por esquema si está en el nombre
        if 'DEV_LANDING' in table_upper:
            return 'landing'
        elif 'DEV_TRANSFORMATION' in table_upper:
            return 'transformation'
        elif 'DEV_REPORTING' in table_upper:
            return 'reporting'

        return None

    def _detect_implicit_relationships(self):
        """Detecta relaciones implícitas basadas en patrones de nombres"""
        logger.info("Detectando relaciones implícitas...")

        # Patrones comunes de foreign keys
        fk_patterns = ['_id', '_key', '_code', '_num', '_no']

        for source_table in self.metadata['columns']:
            if source_table not in self.metadata['relationships']:
                self.metadata['relationships'][source_table] = []

            for col in self.metadata['columns'][source_table]:
                col_name = col['column_name'].lower()

                # Buscar columns que parezcan foreign keys
                for pattern in fk_patterns:
                    if pattern in col_name:
                        # Extract el posible nombre de table referenciada
                        potential_table = col_name.replace(pattern, '')

                        # Buscar tables que coincidan
                        for target_table in self.metadata['tables']:
                            if potential_table in target_table.lower():
                                # Buscar column id en table destino
                                target_cols = self.metadata['columns'].get(target_table, [])
                                for target_col in target_cols:
                                    if 'id' in target_col['column_name'].lower() or \
                                       target_col['column_name'].lower() == col_name:

                                        # Agregar relationship detectada
                                        self.metadata['relationships'][source_table].append({
                                            'source_column': col['column_name'],
                                            'target_table': target_table,
                                            'target_column': target_col['column_name'],
                                            'relationship_type': 'implicit',
                                            'confidence': 'medium'
                                        })
                                        break
                                break

    def _extract_view_dependencies(self, view_definition: str) -> List[str]:
        """Extrae las tables referenciadas en una vista"""
        dependencies = []
        if view_definition:
            # Buscar patrones de FROM y JOIN
            import re
            pattern = r'(?:FROM|JOIN)\s+([A-Za-z0-9_\.]+)'
            matches = re.findall(pattern, view_definition, re.IGNORECASE)
            dependencies = list(set(matches))
        return dependencies

    def extract_all_metadata(self):
        """Método main for extract toda la metadata"""
        try:
            self.extract_tables_metadata()
            self.extract_columns_metadata()
            self.extract_constraints_and_relationships()
            self.extract_views_metadata()
            self.analyze_data_lineage()
            self.perform_quality_checks()
            logger.info("Extracción de metadata completada exitosamente")
        except Exception as e:
            logger.error(f"Error durante la extracción: {str(e)}")
            raise

    def generate_all_outputs(self):
        """Genera all los outputs y documentación"""
        try:
            self.save_all_diagrams()
            self.createte_excel_documentation()
            self.createte_markdown_documentation()
            self.save_metadata_json()
            logger.info("Generación de outputs completada exitosamente")
        except Exception as e:
            logger.error(f"Error generando outputs: {str(e)}")
            raise

    def close(self):
        """Close la connection a Snowflake"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Conexión cerrada")


def main():
    """Function main"""
    print("=" * 60)
    print("Snowflake ERD Complete Extractor")
    print("=" * 60)

    # Verificar si existe file .env
    env_file = Path(".env")

    if env_file.exists():
        # Cargar from .env
        from dotenv import load_dotenv
        import os

        load_dotenv()

        connection_forms = {
            'account': os.getenv('SNOWFLAKE_ACCOUNT'),
            'user': os.getenv('SNOWFLAKE_USER'),
            'password': os.getenv('SNOWFLAKE_PASSWORD'),
            'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),
            'database': input("Database [ENTER for usar default]: ").strip() or 'DEV_ITSECKPI',
            'schema': input("Schema [ENTER for 'SECURITY_ANALYTICS']: ").strip() or 'SECURITY_ANALYTICS'
        }
    else:
        # Solicitar credenciales interactivamente
        print("\nNo se encontró file .env. Por favor ingrese las credenciales:")
        connection_forms = {
            'account': input("Snowflake Account: ").strip(),
            'user': input("Username: ").strip(),
            'password': getpass("Password: "),
            'warehouse': input("Warehouse: ").strip(),
            'database': input("Database: ").strip(),
            'schema': input("Schema [ENTER for 'SECURITY_ANALYTICS']: ").strip() or 'SECURITY_ANALYTICS'
        }

    # Createte extractor y executer
    extractor = SnowflakeERDExtractor(connection_forms)

    try:
        print("\n🔌 Conectando a Snowflake...")
        extractor.connect()

        print("\n📊 Extrayendo metadata...")
        extractor.extract_all_metadata()

        print("\n📝 Generando documentación y diagramas...")
        extractor.generate_all_outputs()

        print("\n✅ Proceso completado exitosamente!")
        print("\n📁 Outputs generados en: snowflake_erd_output/")
        print("   - diagrams/    : Diagramas ERD en varios formatos")
        print("   - documentation/: Excel, Markdown y JSON")
        print("   - scripts/     : Scripts Mermaid, PlantUML, DBML")
        print("   - logs/        : Logs de ejecución")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logger.error(f"Error en ejecución main: {str(e)}")
        return 1
    finally:
        extractor.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())