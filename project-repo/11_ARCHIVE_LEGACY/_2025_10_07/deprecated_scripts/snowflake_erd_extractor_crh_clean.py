#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Snowflake ERD Extractor para GenericCorp
Versión adaptada para trabajar con 3 bases de datos y autenticación SSO
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
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Configurar logging
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

class SnowflakeERDExtractorCRH:
    """Extractor de metadata para el esquema SECURITY_ANALYTICS en las 3 bases de datos de GenericCorp"""

    def __init__(self):
        """Inicializa el extractor con configuración desde .env"""
        from dotenv import load_dotenv
        load_dotenv()

        self.config = {
            'account': os.getenv('SNOWFLAKE_ACCOUNT', 'GenericCorp-CRH_EDW'),
            'user': os.getenv('SNOWFLAKE_USER', 'FUAD.ONATE@CompanyX.COM'),
            'authenticator': os.getenv('SNOWFLAKE_AUTHENTICATOR', 'externalbrowser'),
            'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', 'DEV_WH'),
            'role': os.getenv('SNOWFLAKE_ROLE', 'DEV_DEVELOPER'),
            'schema': os.getenv('SNOWFLAKE_SCHEMA', 'SECURITY_ANALYTICS')
        }

        self.databases = {
            'landing': os.getenv('SNOWFLAKE_DATABASE_LANDING', 'DEV_LANDING'),
            'transformation': os.getenv('SNOWFLAKE_DATABASE_TRANSFORM', 'DEV_TRANSFORMATION'),
            'reporting': os.getenv('SNOWFLAKE_DATABASE_REPORTING', 'DEV_REPORTING')
        }

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
            'landing': {'database': 'DEV_LANDING', 'color': '#FF9933', 'tables': []},
            'transformation': {'database': 'DEV_TRANSFORMATION', 'color': '#3399FF', 'tables': []},
            'reporting': {'database': 'DEV_REPORTING', 'color': '#33CC33', 'tables': []}
        }

    def connect(self):
        """Establece conexión con Snowflake usando autenticación externa"""
        try:
            logger.info("Conectando a Snowflake con autenticación externa...")
            logger.info(f"Account: {self.config['account']}")
            logger.info(f"User: {self.config['user']}")
            logger.info(f"Warehouse: {self.config['warehouse']}")
            logger.info(f"Role: {self.config['role']}")

            # Conexión con autenticación externa (abrirá el browser)
            self.conn = snowflake.connector.connect(
                account=self.config['account'],
                user=self.config['user'],
                authenticator=self.config['authenticator'],
                warehouse=self.config['warehouse'],
                role=self.config['role']
            )
            self.cursor = self.conn.cursor()

            logger.info("[OK] Conexión establecida exitosamente")

            # Verificar contexto
            self.cursor.execute("SELECT CURRENT_WAREHOUSE(), CURRENT_ROLE(), CURRENT_USER()")
            result = self.cursor.fetchone()
            logger.info(f"Contexto: Warehouse={result[0]}, Role={result[1]}, User={result[2]}")

        except Exception as e:
            logger.error(f"[ERROR] Error al conectar a Snowflake: {str(e)}")
            raise

    def extract_metadata_from_all_databases(self):
        """Extrae metadata de las 3 bases de datos"""
        logger.info("=" * 60)
        logger.info("Iniciando extracción de metadata de las 3 bases de datos")
        logger.info("=" * 60)

        for layer_name, database in self.databases.items():
            logger.info(f"\n[DATA] Procesando {layer_name.upper()} ({database})...")

            try:
                # Cambiar a la base de datos
                self.cursor.execute(f"USE DATABASE {database}")
                logger.info(f"  [OK] Usando database: {database}")

                # Verificar si el esquema existe
                self.cursor.execute(f"""
                    SELECT COUNT(*)
                    FROM INFORMATION_SCHEMA.SCHEMATA
                    WHERE SCHEMA_NAME = '{self.config['schema']}'
                """)
                schema_exists = self.cursor.fetchone()[0] > 0

                if not schema_exists:
                    logger.warning(f"  [WARNING] El esquema {self.config['schema']} no existe en {database}")
                    continue

                # Usar el esquema
                self.cursor.execute(f"USE SCHEMA {self.config['schema']}")
                logger.info(f"  [OK] Usando schema: {self.config['schema']}")

                # Extraer metadata de esta base de datos
                self._extract_tables_for_database(layer_name, database)
                self._extract_columns_for_database(layer_name, database)
                self._extract_views_for_database(layer_name, database)

            except Exception as e:
                logger.error(f"  [ERROR] Error procesando {database}: {str(e)}")
                continue

        # Después de extraer todo, analizar relaciones y linaje
        self._analyze_cross_database_relationships()
        self._analyze_data_lineage()
        self._perform_quality_checks()

    def _extract_tables_for_database(self, layer_name: str, database: str):
        """Extrae metadata de tablas para una base de datos específica"""
        logger.info(f"  [LIST] Extrayendo tablas...")

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
        WHERE TABLE_SCHEMA = %s
        AND TABLE_TYPE IN ('BASE TABLE', 'TABLE')
        ORDER BY TABLE_NAME
        """

        try:
            self.cursor.execute(query, (self.config['schema'],))
            tables = self.cursor.fetchall()

            for table in tables:
                table_name = table[2]
                full_table_name = f"{database}.{self.config['schema']}.{table_name}"

                self.metadata['tables'][full_table_name] = {
                    'database': database,
                    'schema': table[1],
                    'name': table_name,
                    'type': table[3],
                    'row_count': table[4],
                    'bytes': table[5],
                    'created': str(table[6]) if table[6] else None,
                    'last_altered': str(table[7]) if table[7] else None,
                    'comment': table[8],
                    'layer': layer_name
                }

                self.layers[layer_name]['tables'].append(full_table_name)

            logger.info(f"    [OK] {len(tables)} tablas encontradas")

        except Exception as e:
            logger.error(f"    [ERROR] Error extrayendo tablas: {str(e)}")

    def _extract_columns_for_database(self, layer_name: str, database: str):
        """Extrae metadata de columnas para una base de datos específica"""
        logger.info(f"  [DATA] Extrayendo columnas...")

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
        WHERE TABLE_SCHEMA = %s
        ORDER BY TABLE_NAME, ORDINAL_POSITION
        """

        try:
            self.cursor.execute(query, (self.config['schema'],))
            columns = self.cursor.fetchall()

            for col in columns:
                table_name = col[0]
                full_table_name = f"{database}.{self.config['schema']}.{table_name}"

                if full_table_name not in self.metadata['columns']:
                    self.metadata['columns'][full_table_name] = []

                self.metadata['columns'][full_table_name].append({
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

            total_cols = sum(len(cols) for table, cols in self.metadata['columns'].items()
                           if table.startswith(database))
            logger.info(f"    [OK] {total_cols} columnas extraídas")

        except Exception as e:
            logger.error(f"    [ERROR] Error extrayendo columnas: {str(e)}")

    def _extract_views_for_database(self, layer_name: str, database: str):
        """Extrae metadata de vistas para una base de datos específica"""
        logger.info(f"  [VIEW] Extrayendo vistas...")

        query = """
        SELECT
            TABLE_NAME as VIEW_NAME,
            VIEW_DEFINITION
        FROM INFORMATION_SCHEMA.VIEWS
        WHERE TABLE_SCHEMA = %s
        """

        try:
            self.cursor.execute(query, (self.config['schema'],))
            views = self.cursor.fetchall()

            for view in views:
                view_name = view[0]
                full_view_name = f"{database}.{self.config['schema']}.{view_name}"

                self.metadata['views'][full_view_name] = {
                    'database': database,
                    'schema': self.config['schema'],
                    'name': view_name,
                    'definition': view[1],
                    'layer': layer_name
                }

                # También agregar a la lista de tablas del layer
                self.layers[layer_name]['tables'].append(full_view_name)

            logger.info(f"    [OK] {len(views)} vistas encontradas")

        except Exception as e:
            logger.error(f"    [ERROR] Error extrayendo vistas: {str(e)}")

    def _analyze_cross_database_relationships(self):
        """Analiza relaciones entre tablas de diferentes bases de datos"""
        logger.info("\n[LINK] Analizando relaciones entre bases de datos...")

        self.metadata['relationships'] = {}

        # Patrones para detectar relaciones
        patterns = {
            'id_columns': ['_ID', '_KEY', '_CODE'],
            'fk_patterns': ['DIM_', 'FACT_', 'REF_']
        }

        # Detectar relaciones basadas en nombres de columnas
        for source_table, columns in self.metadata['columns'].items():
            self.metadata['relationships'][source_table] = []

            for col in columns:
                col_name = col['column_name'].upper()

                # Buscar posibles foreign keys
                for pattern in patterns['id_columns']:
                    if pattern in col_name:
                        # Buscar tabla destino
                        potential_table_name = col_name.replace(pattern, '')

                        for target_table in self.metadata['tables']:
                            target_short_name = target_table.split('.')[-1].upper()

                            if potential_table_name in target_short_name or \
                               target_short_name in potential_table_name:
                                self.metadata['relationships'][source_table].append({
                                    'source_column': col['column_name'],
                                    'target_table': target_table,
                                    'target_column': 'ID',  # Asumido
                                    'type': 'detected',
                                    'confidence': 'medium'
                                })

        relationships_count = sum(len(rels) for rels in self.metadata['relationships'].values())
        logger.info(f"  [OK] {relationships_count} relaciones detectadas")

    def _analyze_data_lineage(self):
        """Analiza el flujo de datos entre las capas"""
        logger.info("\n[CHART] Analizando linaje de datos...")

        self.metadata['data_lineage'] = {
            'landing_to_transform': [],
            'transform_to_reporting': []
        }

        # Analizar flujo Landing -> Transformation
        for landing_table in self.layers['landing']['tables']:
            landing_name = landing_table.split('.')[-1].upper()

            for transform_table in self.layers['transformation']['tables']:
                transform_name = transform_table.split('.')[-1].upper()

                # Buscar coincidencias en nombres
                if any(part in transform_name for part in landing_name.split('_')) or \
                   any(part in landing_name for part in transform_name.split('_')):
                    self.metadata['data_lineage']['landing_to_transform'].append({
                        'source': landing_table,
                        'target': transform_table,
                        'confidence': 'high' if landing_name in transform_name else 'medium'
                    })

        # Analizar flujo Transformation -> Reporting
        for transform_table in self.layers['transformation']['tables']:
            transform_name = transform_table.split('.')[-1].upper()

            for reporting_table in self.layers['reporting']['tables']:
                reporting_name = reporting_table.split('.')[-1].upper()

                if any(part in reporting_name for part in transform_name.split('_')) or \
                   any(part in transform_name for part in reporting_name.split('_')):
                    self.metadata['data_lineage']['transform_to_reporting'].append({
                        'source': transform_table,
                        'target': reporting_table,
                        'confidence': 'high' if transform_name in reporting_name else 'medium'
                    })

        logger.info(f"  [OK] Landing->Transform: {len(self.metadata['data_lineage']['landing_to_transform'])} flujos")
        logger.info(f"  [OK] Transform->Reporting: {len(self.metadata['data_lineage']['transform_to_reporting'])} flujos")

    def _perform_quality_checks(self):
        """Realiza validaciones de calidad"""
        logger.info("\n[SEARCH] Realizando validaciones de calidad...")

        self.metadata['quality_issues'] = {
            'empty_tables': [],
            'large_tables': [],
            'orphaned_tables': [],
            'missing_in_layers': []
        }

        for table_name, table_info in self.metadata['tables'].items():
            # Tablas vacías
            if table_info.get('row_count') == 0:
                self.metadata['quality_issues']['empty_tables'].append(table_name)

            # Tablas muy grandes (> 1GB)
            if table_info.get('bytes') and table_info['bytes'] > 1024*1024*1024:
                self.metadata['quality_issues']['large_tables'].append({
                    'table': table_name,
                    'size_gb': round(table_info['bytes'] / 1024 / 1024 / 1024, 2)
                })

            # Tablas sin relaciones
            if table_name not in self.metadata['relationships'] or \
               not self.metadata['relationships'][table_name]:
                has_incoming = False
                for _, rels in self.metadata['relationships'].items():
                    if any(r['target_table'] == table_name for r in rels):
                        has_incoming = True
                        break
                if not has_incoming:
                    self.metadata['quality_issues']['orphaned_tables'].append(table_name)

        logger.info(f"  [OK] Tablas vacías: {len(self.metadata['quality_issues']['empty_tables'])}")
        logger.info(f"  [OK] Tablas grandes: {len(self.metadata['quality_issues']['large_tables'])}")
        logger.info(f"  [OK] Tablas huérfanas: {len(self.metadata['quality_issues']['orphaned_tables'])}")

    def generate_complete_report(self):
        """Genera reporte completo con todos los diagramas y documentación"""
        logger.info("\n" + "=" * 60)
        logger.info("[DOC] Generando reportes y diagramas...")
        logger.info("=" * 60)

        # Crear estructura de directorios
        output_dirs = {
            'root': Path("snowflake_erd_output"),
            'diagrams': Path("snowflake_erd_output/diagrams"),
            'documentation': Path("snowflake_erd_output/documentation"),
            'scripts': Path("snowflake_erd_output/scripts")
        }

        for dir_path in output_dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)

        # Generar diagramas
        self._generate_mermaid_diagrams(output_dirs['scripts'])
        self._generate_dbml_schemas(output_dirs['scripts'])
        self._generate_plantuml_diagrams(output_dirs['scripts'])
        self._generate_graphviz_diagrams(output_dirs['diagrams'])

        # Generar documentación
        self._generate_excel_documentation(output_dirs['documentation'])
        self._generate_markdown_documentation(output_dirs['documentation'])
        self._save_json_metadata(output_dirs['documentation'])

        logger.info("\n[SUCCESS] Generación completada!")
        logger.info(f"📁 Resultados en: {output_dirs['root']}")

    def _generate_mermaid_diagrams(self, output_dir: Path):
        """Genera diagramas en formato Mermaid"""
        logger.info("  [ART] Generando diagramas Mermaid...")

        # Diagrama completo
        mermaid_full = ["erDiagram"]
        mermaid_full.append("    %% Diagrama completo SECURITY_ANALYTICS")

        # Diagramas por capa
        for layer_name, layer_info in self.layers.items():
            mermaid_layer = ["erDiagram"]
            mermaid_layer.append(f"    %% {layer_name.upper()} Layer")

            for table in layer_info['tables'][:20]:  # Limitar para no sobrecargar
                table_short = table.split('.')[-1]
                if table in self.metadata['columns']:
                    mermaid_layer.append(f"    {table_short} {{")
                    mermaid_full.append(f"    {table_short} {{")

                    for col in self.metadata['columns'][table][:10]:
                        col_def = f"        {col['data_type']} {col['column_name']}"
                        mermaid_layer.append(col_def)
                        mermaid_full.append(col_def)

                    mermaid_layer.append("    }")
                    mermaid_full.append("    }")

            # Guardar diagrama de la capa
            layer_file = output_dir / f"mermaid_{layer_name}.md"
            with open(layer_file, 'w', encoding='utf-8') as f:
                f.write(f"# ERD {layer_name.title()} Layer\n\n")
                f.write("```mermaid\n")
                f.write('\n'.join(mermaid_layer))
                f.write("\n```")

        # Guardar diagrama completo
        full_file = output_dir / "mermaid_complete.md"
        with open(full_file, 'w', encoding='utf-8') as f:
            f.write("# ERD Completo SECURITY_ANALYTICS\n\n")
            f.write("```mermaid\n")
            f.write('\n'.join(mermaid_full))
            f.write("\n```")

        logger.info("    [OK] Diagramas Mermaid generados")

    def _generate_dbml_schemas(self, output_dir: Path):
        """Genera esquemas en formato DBML"""
        logger.info("  [FOLDER] Generando esquemas DBML...")

        for layer_name, layer_info in self.layers.items():
            dbml = []
            dbml.append(f"// DBML Schema - {layer_name.upper()} Layer")
            dbml.append(f"// Database: {layer_info.get('database', 'N/A')}")
            dbml.append(f"// Generated: {datetime.now().isoformat()}\n")

            for table in layer_info['tables'][:30]:
                table_short = table.split('.')[-1]
                table_info = self.metadata['tables'].get(table, {})

                dbml.append(f"Table {table_short} {{")
                if table_info.get('comment'):
                    dbml.append(f"  Note: '{table_info['comment']}'")

                if table in self.metadata['columns']:
                    for col in self.metadata['columns'][table]:
                        col_def = f"  {col['column_name']} {col['data_type']}"
                        if col['is_nullable'] == 'NO':
                            col_def += " [not null]"
                        dbml.append(col_def)

                dbml.append("}\n")

            # Guardar archivo DBML
            dbml_file = output_dir / f"dbml_{layer_name}.dbml"
            with open(dbml_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(dbml))

        logger.info("    [OK] Esquemas DBML generados")

    def _generate_plantuml_diagrams(self, output_dir: Path):
        """Genera diagramas en formato PlantUML"""
        logger.info("  [RULER] Generando diagramas PlantUML...")

        for layer_name, layer_info in self.layers.items():
            plantuml = ["@startuml"]
            plantuml.append(f"title {layer_name.upper()} Layer - SECURITY_ANALYTICS")
            plantuml.append("skinparam linetype ortho")
            plantuml.append(f"skinparam class BackgroundColor {layer_info['color']}")
            plantuml.append("")

            for table in layer_info['tables'][:20]:
                table_short = table.split('.')[-1]
                if table in self.metadata['columns']:
                    plantuml.append(f"class {table_short} {{")
                    for col in self.metadata['columns'][table][:15]:
                        plantuml.append(f"  {col['column_name']} : {col['data_type']}")
                    plantuml.append("}")

            # Agregar relaciones
            for source, rels in self.metadata['relationships'].items():
                if source in layer_info['tables']:
                    source_short = source.split('.')[-1]
                    for rel in rels[:10]:
                        if rel['target_table'] in layer_info['tables']:
                            target_short = rel['target_table'].split('.')[-1]
                            plantuml.append(f"{source_short} --> {target_short}")

            plantuml.append("@enduml")

            # Guardar archivo
            puml_file = output_dir / f"plantuml_{layer_name}.puml"
            with open(puml_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(plantuml))

        logger.info("    [OK] Diagramas PlantUML generados")

    def _generate_graphviz_diagrams(self, output_dir: Path):
        """Genera diagramas con Graphviz"""
        logger.info("  [TARGET] Generando diagramas Graphviz...")

        for layer_name, layer_info in self.layers.items():
            dot = []
            dot.append("digraph G {")
            dot.append('  rankdir=LR;')
            dot.append('  node [shape=record, style=filled];')
            dot.append(f'  node [fillcolor="{layer_info["color"]}"];')

            for table in layer_info['tables'][:25]:
                table_short = table.split('.')[-1]
                if table in self.metadata['columns']:
                    columns = [f"{c['column_name']}:{c['data_type']}"
                             for c in self.metadata['columns'][table][:10]]
                    label = f"{table_short}|" + "\\l".join(columns) + "\\l"
                    dot.append(f'  "{table_short}" [label="{{{label}}}"];')

            # Relaciones
            for source, rels in self.metadata['relationships'].items():
                if source in layer_info['tables']:
                    source_short = source.split('.')[-1]
                    for rel in rels[:15]:
                        if rel['target_table'] in layer_info['tables']:
                            target_short = rel['target_table'].split('.')[-1]
                            dot.append(f'  "{source_short}" -> "{target_short}";')

            dot.append("}")

            # Guardar archivo DOT
            dot_file = output_dir / f"{layer_name}_erd.dot"
            with open(dot_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(dot))

            # Intentar generar PNG si graphviz está instalado
            try:
                import graphviz
                graph = graphviz.Source('\n'.join(dot))
                graph.render(filename=f"{layer_name}_erd", directory=str(output_dir),
                           format='png', cleanup=True)
                logger.info(f"    [OK] PNG generado para {layer_name}")
            except:
                pass

        logger.info("    [OK] Diagramas Graphviz generados")

    def _generate_excel_documentation(self, output_dir: Path):
        """Genera documentación en Excel"""
        logger.info("  [DATA] Generando documentación Excel...")

        excel_file = output_dir / f"itseckpi_analysis_{datetime.now().strftime('%Y%m%d')}.xlsx"

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
                    'Empty Tables',
                    'Orphaned Tables',
                    'Total Size (GB)'
                ],
                'Value': [
                    len(self.metadata['tables']),
                    len(self.layers['landing']['tables']),
                    len(self.layers['transformation']['tables']),
                    len(self.layers['reporting']['tables']),
                    len(self.metadata['views']),
                    sum(len(cols) for cols in self.metadata['columns'].values()),
                    len(self.metadata['quality_issues']['empty_tables']),
                    len(self.metadata['quality_issues']['orphaned_tables']),
                    round(sum(t.get('bytes', 0) for t in self.metadata['tables'].values()) / 1024**3, 2)
                ]
            }
            pd.DataFrame(overview_data).to_excel(writer, sheet_name='Overview', index=False)

            # 2. Tables
            tables_data = []
            for table_name, info in self.metadata['tables'].items():
                tables_data.append({
                    'Database': info.get('database', ''),
                    'Schema': info.get('schema', ''),
                    'Table': info.get('name', ''),
                    'Layer': info.get('layer', ''),
                    'Type': info.get('type', ''),
                    'Rows': info.get('row_count', 0),
                    'Size (MB)': round(info.get('bytes', 0) / 1024**2, 2),
                    'Created': info.get('created', ''),
                    'Modified': info.get('last_altered', ''),
                    'Comment': info.get('comment', '')
                })
            pd.DataFrame(tables_data).to_excel(writer, sheet_name='Tables', index=False)

            # 3. Data Lineage
            lineage_data = []
            for flow_type, flows in self.metadata.get('data_lineage', {}).items():
                if isinstance(flows, list):
                    for flow in flows:
                        lineage_data.append({
                            'Flow Type': flow_type.replace('_', ' ').title(),
                            'Source': flow['source'].split('.')[-1],
                            'Target': flow['target'].split('.')[-1],
                            'Confidence': flow.get('confidence', 'medium')
                        })
            if lineage_data:
                pd.DataFrame(lineage_data).to_excel(writer, sheet_name='Data Lineage', index=False)

            # 4. Quality Issues
            issues_data = []
            for issue_type, items in self.metadata['quality_issues'].items():
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict):
                            issues_data.append({
                                'Issue Type': issue_type.replace('_', ' ').title(),
                                'Object': item.get('table', ''),
                                'Details': str(item.get('size_gb', ''))
                            })
                        else:
                            issues_data.append({
                                'Issue Type': issue_type.replace('_', ' ').title(),
                                'Object': item.split('.')[-1] if '.' in item else item,
                                'Details': ''
                            })
            if issues_data:
                pd.DataFrame(issues_data).to_excel(writer, sheet_name='Quality Issues', index=False)

        logger.info(f"    [OK] Excel generado: {excel_file.name}")

    def _generate_markdown_documentation(self, output_dir: Path):
        """Genera documentación en Markdown"""
        logger.info("  [DOC] Generando documentación Markdown...")

        md_file = output_dir / f"itseckpi_documentation_{datetime.now().strftime('%Y%m%d')}.md"

        md = []
        md.append("# Documentación del Esquema SECURITY_ANALYTICS - GenericCorp")
        md.append(f"\nGenerado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Resumen ejecutivo
        md.append("## [DATA] Resumen Ejecutivo\n")
        md.append(f"- **Account**: {self.config['account']}")
        md.append(f"- **Role**: {self.config['role']}")
        md.append(f"- **Warehouse**: {self.config['warehouse']}")
        md.append(f"- **Schema**: {self.config['schema']}\n")

        md.append("### Estadísticas Generales\n")
        md.append(f"- **Total de tablas**: {len(self.metadata['tables'])}")
        md.append(f"- **Total de vistas**: {len(self.metadata['views'])}")
        md.append(f"- **Total de columnas**: {sum(len(cols) for cols in self.metadata['columns'].values())}")

        total_bytes = sum(t.get('bytes', 0) for t in self.metadata['tables'].values())
        md.append(f"- **Volumen total**: {round(total_bytes / 1024**3, 2)} GB\n")

        # Información por capa
        for layer_name, layer_info in self.layers.items():
            md.append(f"\n## [BUILD] {layer_name.title()} Layer")
            md.append(f"\n**Database**: `{layer_info.get('database', 'N/A')}`")
            md.append(f"\n**Tablas**: {len(layer_info['tables'])}\n")

            if layer_info['tables']:
                md.append("| Tabla | Filas | Tamaño (MB) | Tipo |")
                md.append("|-------|-------|-------------|------|")

                for table in layer_info['tables'][:10]:
                    info = self.metadata['tables'].get(table, {})
                    table_name = table.split('.')[-1]
                    rows = info.get('row_count', 0)
                    size_mb = round(info.get('bytes', 0) / 1024**2, 2)
                    table_type = 'VIEW' if table in self.metadata['views'] else 'TABLE'
                    md.append(f"| {table_name} | {rows:,} | {size_mb:,.2f} | {table_type} |")

                if len(layer_info['tables']) > 10:
                    md.append(f"\n*... y {len(layer_info['tables']) - 10} más*")

        # Linaje de datos
        md.append("\n## [SYNC] Linaje de Datos\n")

        lineage = self.metadata.get('data_lineage', {})
        if lineage.get('landing_to_transform'):
            md.append("### Landing → Transformation\n")
            md.append("| Origen | Destino | Confianza |")
            md.append("|--------|---------|-----------|")
            for flow in lineage['landing_to_transform'][:10]:
                source = flow['source'].split('.')[-1]
                target = flow['target'].split('.')[-1]
                md.append(f"| {source} | {target} | {flow['confidence']} |")

        if lineage.get('transform_to_reporting'):
            md.append("\n### Transformation → Reporting\n")
            md.append("| Origen | Destino | Confianza |")
            md.append("|--------|---------|-----------|")
            for flow in lineage['transform_to_reporting'][:10]:
                source = flow['source'].split('.')[-1]
                target = flow['target'].split('.')[-1]
                md.append(f"| {source} | {target} | {flow['confidence']} |")

        # Issues de calidad
        md.append("\n## [WARNING] Issues de Calidad\n")

        issues = self.metadata.get('quality_issues', {})
        if issues.get('empty_tables'):
            md.append(f"\n### Tablas Vacías ({len(issues['empty_tables'])})\n")
            for table in issues['empty_tables'][:5]:
                md.append(f"- {table.split('.')[-1]}")

        if issues.get('orphaned_tables'):
            md.append(f"\n### Tablas Huérfanas ({len(issues['orphaned_tables'])})\n")
            for table in issues['orphaned_tables'][:5]:
                md.append(f"- {table.split('.')[-1]}")

        if issues.get('large_tables'):
            md.append(f"\n### Tablas Grandes ({len(issues['large_tables'])})\n")
            md.append("| Tabla | Tamaño (GB) |")
            md.append("|-------|-------------|")
            for item in issues['large_tables'][:5]:
                table_name = item['table'].split('.')[-1]
                md.append(f"| {table_name} | {item['size_gb']} |")

        # Guardar archivo
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md))

        logger.info(f"    [OK] Markdown generado: {md_file.name}")

    def _save_json_metadata(self, output_dir: Path):
        """Guarda toda la metadata en formato JSON"""
        logger.info("  [SAVE] Guardando metadata JSON...")

        json_file = output_dir / f"metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # Convertir datetime a string
        def serialize(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return str(obj)

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, default=serialize)

        logger.info(f"    [OK] JSON guardado: {json_file.name}")

    def close(self):
        """Cierra la conexión a Snowflake"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("[PLUG] Conexión cerrada")


def main():
    """Función principal"""
    print("\n" + "=" * 60)
    print("   SNOWFLAKE ERD EXTRACTOR - GenericCorp")
    print("   SECURITY_ANALYTICS Schema Analysis")
    print("=" * 60)

    extractor = SnowflakeERDExtractorCRH()

    try:
        print("\n[PLUG] Conectando a Snowflake...")
        print("   (Se abrirá tu navegador para autenticación SSO)")
        extractor.connect()

        print("\n[DATA] Extrayendo metadata de las 3 bases de datos...")
        print("   - DEV_LANDING")
        print("   - DEV_TRANSFORMATION")
        print("   - DEV_REPORTING")
        extractor.extract_metadata_from_all_databases()

        print("\n[DOC] Generando reportes y diagramas...")
        extractor.generate_complete_report()

        print("\n" + "=" * 60)
        print("[SUCCESS] PROCESO COMPLETADO EXITOSAMENTE!")
        print("=" * 60)
        print("\n📁 Resultados guardados en: snowflake_erd_output/")
        print("   ├─ [DATA] diagrams/       - Diagramas ERD")
        print("   ├─ 📚 documentation/  - Excel, Markdown, JSON")
        print("   ├─ [DOC] scripts/        - Mermaid, PlantUML, DBML")
        print("   └─ [LIST] logs/           - Logs de ejecución")

        return 0

    except Exception as e:
        print(f"\n[ERROR] Error: {str(e)}")
        logger.error(f"Error en ejecución: {str(e)}", exc_info=True)
        return 1

    finally:
        extractor.close()


if __name__ == "__main__":
    sys.exit(main())
