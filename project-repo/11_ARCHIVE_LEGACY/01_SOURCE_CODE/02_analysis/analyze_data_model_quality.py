#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis Profundo del Modelo de Datos SECURITY_ANALYTICS
Verifica constraints, relaciones, integridad referencial y calidad del modelo dimensional
"""

import snowflake.connector
import pandas as pd
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv
import json

# Cargar configuración
load_dotenv()

class DataModelAnalyzer:
    """Analizador especializado en la calidad del modelo de data"""

    def __init__(self):
        self.config = {
            'account': os.getenv('SNOWFLAKE_ACCOUNT', 'GenericCorp-CRH_EDW'),
            'user': os.getenv('SNOWFLAKE_USER', 'FUAD.ONATE@CompanyX.COM'),
            'authenticator': os.getenv('SNOWFLAKE_AUTHENTICATOR', 'externalbrowser'),
            'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', 'DEV_WH'),
            'role': os.getenv('SNOWFLAKE_ROLE', 'DEV_DEVELOPER')
        }

        self.conn = None
        self.cursor = None
        self.analysis_results = {
            'constraints_summary': {},
            'missing_keys': {},
            'relationship_analysis': {},
            'dimensional_model_issues': {},
            'recommendations': []
        }

    def connect(self):
        """Conecta a Snowflake"""
        print("[INFO] Conectando a Snowflake...")
        self.conn = snowflake.connector.connect(**self.config)
        self.cursor = self.conn.cursor()
        print("[OK] Conexión establecida")

    def analyze_constraints_per_layer(self):
        """Analiza constraints (PK, FK, UK, NOT NULL) por each capa"""
        print("\n" + "="*60)
        print("ANÁLISIS DE CONSTRAINTS POR CAPA")
        print("="*60)

        databases = {
            'DEV_LANDING': 'Landing Layer',
            'DEV_TRANSFORMATION': 'Transformation Layer',
            'DEV_REPORTING': 'Reporting Layer'
        }

        for db, layer_name in databases.items():
            print(f"\n[ANALYZING] {layer_name} ({db})...")

            try:
                self.cursor.execute(f"USE DATABASE {db}")
                self.cursor.execute("USE SCHEMA SECURITY_ANALYTICS")

                # Query for obtener todas las constraints
                constraint_query = """
                SELECT
                    tc.TABLE_NAME,
                    tc.CONSTRAINT_NAME,
                    tc.CONSTRAINT_TYPE,
                    LISTAGG(kcu.COLUMN_NAME, ', ') WITHIN GROUP (ORDER BY kcu.ORDINAL_POSITION) as COLUMNS
                FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                LEFT JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
                    ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
                    AND tc.TABLE_SCHEMA = kcu.TABLE_SCHEMA
                WHERE tc.TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                GROUP BY tc.TABLE_NAME, tc.CONSTRAINT_NAME, tc.CONSTRAINT_TYPE
                ORDER BY tc.TABLE_NAME, tc.CONSTRAINT_TYPE
                """

                self.cursor.execute(constraint_query)
                constraints = self.cursor.fetchall()

                # Analizar resultados
                constraint_summary = {
                    'PRIMARY KEY': [],
                    'FOREIGN KEY': [],
                    'UNIQUE': [],
                    'NOT NULL': []
                }

                for constraint in constraints:
                    table_name, const_name, const_type, columns = constraint
                    if const_type in constraint_summary:
                        constraint_summary[const_type].append({
                            'table': table_name,
                            'constraint': const_name,
                            'columns': columns
                        })

                # Contar tables sin PK
                tables_query = """
                SELECT COUNT(DISTINCT TABLE_NAME)
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                AND TABLE_TYPE = 'BASE TABLE'
                """
                self.cursor.execute(tables_query)
                total_tables = self.cursor.fetchone()[0]

                # Guardar resultados
                self.analysis_results['constraints_summary'][db] = {
                    'total_tables': total_tables,
                    'tables_with_pk': len(set(c['table'] for c in constraint_summary['PRIMARY KEY'])),
                    'tables_without_pk': total_tables - len(set(c['table'] for c in constraint_summary['PRIMARY KEY'])),
                    'foreign_keys': len(constraint_summary['FOREIGN KEY']),
                    'unique_constraints': len(constraint_summary['UNIQUE']),
                    'constraints': constraint_summary
                }

                # Imprimir resumen
                print(f"  [STATS] Total tables: {total_tables}")
                print(f"  [STATS] Tablas con PK: {len(set(c['table'] for c in constraint_summary['PRIMARY KEY']))}")
                print(f"  [WARNING] Tablas SIN PK: {total_tables - len(set(c['table'] for c in constraint_summary['PRIMARY KEY']))}")
                print(f"  [STATS] Foreign Keys: {len(constraint_summary['FOREIGN KEY'])}")
                print(f"  [STATS] Unique Constraints: {len(constraint_summary['UNIQUE'])}")

            except Exception as e:
                print(f"  [ERROR] {str(e)}")

    def analyze_dimensional_model(self):
        """Analiza el modelo dimensional (DIM/FACT tables)"""
        print("\n" + "="*60)
        print("ANÁLISIS DEL MODELO DIMENSIONAL")
        print("="*60)

        try:
            # Analizar en TRANSFORMATION layer donde debería estar el modelo estrella
            self.cursor.execute("USE DATABASE DEV_TRANSFORMATION")
            self.cursor.execute("USE SCHEMA SECURITY_ANALYTICS")

            # Identificar tables DIM y FACT
            dim_fact_query = """
            SELECT
                TABLE_NAME,
                CASE
                    WHEN UPPER(TABLE_NAME) LIKE 'DIM_%' THEN 'DIMENSION'
                    WHEN UPPER(TABLE_NAME) LIKE 'FACT_%' THEN 'FACT'
                    WHEN UPPER(TABLE_NAME) LIKE 'FCT_%' THEN 'FACT'
                    ELSE 'OTHER'
                END as TABLE_TYPE,
                ROW_COUNT,
                BYTES
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
            AND TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_TYPE, TABLE_NAME
            """

            self.cursor.execute(dim_fact_query)
            dim_fact_tables = self.cursor.fetchall()

            dimensions = []
            facts = []
            others = []

            for table in dim_fact_tables:
                table_name, table_type, row_count, bytes = table
                table_info = {
                    'name': table_name,
                    'rows': row_count or 0,
                    'size_mb': round((bytes or 0) / 1024 / 1024, 2)
                }

                if table_type == 'DIMENSION':
                    dimensions.append(table_info)
                elif table_type == 'FACT':
                    facts.append(table_info)
                else:
                    others.append(table_info)

            print(f"\n[FOUND] Tablas Dimensión: {len(dimensions)}")
            for dim in dimensions[:10]:
                print(f"  - {dim['name']} ({dim['rows']:,} filas)")

            print(f"\n[FOUND] Tablas Fact: {len(facts)}")
            for fact in facts[:10]:
                print(f"  - {fact['name']} ({fact['rows']:,} filas)")

            if len(others) > 0:
                print(f"\n[WARNING] Tablas sin nomenclatura DIM/FACT: {len(others)}")
                print("  Esto puede indicar un modelo dimensional incompleto")

            # Analizar relaciones entre DIM y FACT
            self.analyze_dim_fact_relationships(dimensions, facts)

            # Guardar resultados
            self.analysis_results['dimensional_model_issues'] = {
                'dimensions': dimensions,
                'facts': facts,
                'others': others,
                'issues': []
            }

            # Detectar issues
            if len(facts) == 0:
                self.analysis_results['dimensional_model_issues']['issues'].append(
                    "NO se encontraron tables FACT - El modelo dimensional podría estar incompleto"
                )
            if len(dimensions) < 3:
                self.analysis_results['dimensional_model_issues']['issues'].append(
                    f"Solo {len(dimensions)} dimensiones encontradas - Un modelo dimensional típico tiene más"
                )

        except Exception as e:
            print(f"[ERROR] {str(e)}")

    def analyze_dim_fact_relationships(self, dimensions, facts):
        """Analiza las relaciones entre dimensiones y hechos"""
        print("\n[ANALYZING] Relaciones DIM-FACT...")

        if not facts:
            print("  [WARNING] No hay tables FACT for analizar relaciones")
            return

        try:
            for fact in facts[:5]:  # Analizar primeras 5 fact tables
                fact_name = fact['name']
                print(f"\n  Analizando FACT: {fact_name}")

                # Obtener columns de la fact table
                columns_query = f"""
                SELECT COLUMN_NAME, DATA_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                AND TABLE_NAME = '{fact_name}'
                AND (
                    COLUMN_NAME LIKE '%_ID' OR
                    COLUMN_NAME LIKE '%_KEY' OR
                    COLUMN_NAME LIKE '%_SK'
                )
                ORDER BY ORDINAL_POSITION
                """

                self.cursor.execute(columns_query)
                fact_columns = self.cursor.fetchall()

                potential_fks = []
                for col_name, col_type in fact_columns:
                    # Buscar dimensión correspondiente
                    dim_name = self.find_matching_dimension(col_name, dimensions)
                    if dim_name:
                        potential_fks.append({
                            'column': col_name,
                            'probable_dim': dim_name,
                            'type': col_type
                        })
                        print(f"    - {col_name} -> Probable relationship con {dim_name}")
                    else:
                        print(f"    - {col_name} -> [WARNING] No se encontró dimensión correspondiente")

                if not potential_fks:
                    print(f"    [WARNING] No se detectaron Foreign Keys potenciales en {fact_name}")

        except Exception as e:
            print(f"  [ERROR] {str(e)}")

    def find_matching_dimension(self, column_name, dimensions):
        """Encuentra la dimensión que corresponde a una column FK"""
        column_upper = column_name.upper()

        # Remover sufijos comunes
        base_name = column_upper.replace('_ID', '').replace('_KEY', '').replace('_SK', '')

        for dim in dimensions:
            dim_upper = dim['name'].upper()
            # Verificar si el nombre base está en el nombre de la dimensión
            if base_name in dim_upper or dim_upper.replace('DIM_', '') in base_name:
                return dim['name']

        return None

    def analyze_missing_keys(self):
        """Detecta columns que deberían ser keys pero no están definidas como tal"""
        print("\n" + "="*60)
        print("DETECCIÓN DE KEYS FALTANTES")
        print("="*60)

        databases = ['DEV_LANDING', 'DEV_TRANSFORMATION', 'DEV_REPORTING']

        for db in databases:
            print(f"\n[ANALYZING] {db}...")

            try:
                self.cursor.execute(f"USE DATABASE {db}")
                self.cursor.execute("USE SCHEMA SECURITY_ANALYTICS")

                # Buscar columns con patrones de keys
                potential_keys_query = """
                SELECT
                    c.TABLE_NAME,
                    c.COLUMN_NAME,
                    c.DATA_TYPE,
                    c.IS_NULLABLE,
                    t.ROW_COUNT
                FROM INFORMATION_SCHEMA.COLUMNS c
                JOIN INFORMATION_SCHEMA.TABLES t
                    ON c.TABLE_NAME = t.TABLE_NAME
                    AND c.TABLE_SCHEMA = t.TABLE_SCHEMA
                WHERE c.TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                AND t.TABLE_TYPE = 'BASE TABLE'
                AND (
                    c.COLUMN_NAME LIKE '%_ID' OR
                    c.COLUMN_NAME LIKE '%_KEY' OR
                    c.COLUMN_NAME LIKE '%_CODE' OR
                    c.COLUMN_NAME = 'ID' OR
                    c.COLUMN_NAME LIKE '%_SK' OR
                    c.COLUMN_NAME LIKE '%_PK'
                )
                ORDER BY c.TABLE_NAME, c.COLUMN_NAME
                """

                self.cursor.execute(potential_keys_query)
                potential_keys = self.cursor.fetchall()

                # Verificar cuáles NO tienen constraints
                missing_keys = []
                for table_name, column_name, data_type, is_nullable, row_count in potential_keys:
                    # Verificar si tiene algún constraint
                    check_constraint_query = f"""
                    SELECT COUNT(*)
                    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                    WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                    AND TABLE_NAME = '{table_name}'
                    AND COLUMN_NAME = '{column_name}'
                    """

                    self.cursor.execute(check_constraint_query)
                    has_constraint = self.cursor.fetchone()[0] > 0

                    if not has_constraint:
                        missing_keys.append({
                            'table': table_name,
                            'column': column_name,
                            'data_type': data_type,
                            'nullable': is_nullable,
                            'table_rows': row_count
                        })

                self.analysis_results['missing_keys'][db] = missing_keys

                print(f"  [FOUND] {len(missing_keys)} columns que podrían ser keys sin constraints")

                # Mostrar las más críticas (tables con más filas)
                critical_missing = sorted(missing_keys,
                                        key=lambda x: x['table_rows'] or 0,
                                        reverse=True)[:10]

                if critical_missing:
                    print("\n  [CRITICAL] Top columns sin constraints (por volumen de data):")
                    for item in critical_missing:
                        print(f"    - {item['table']}.{item['column']} ({item['table_rows']:,} filas)")

            except Exception as e:
                print(f"  [ERROR] {str(e)}")

    def analyze_referential_integrity(self):
        """Analiza la integridad referencial entre tables"""
        print("\n" + "="*60)
        print("ANÁLISIS DE INTEGRIDAD REFERENCIAL")
        print("="*60)

        # Verificar relaciones entre capas
        layer_relationships = {
            'landing_to_transform': [],
            'transform_to_reporting': []
        }

        print("\n[CHECKING] Integridad Landing -> Transformation...")

        try:
            # Analizar tables que deberían tener correspondencia entre capas
            self.cursor.execute("USE DATABASE DEV_LANDING")
            self.cursor.execute("USE SCHEMA SECURITY_ANALYTICS")

            landing_tables_query = """
            SELECT TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
            AND TABLE_TYPE = 'BASE TABLE'
            """
            self.cursor.execute(landing_tables_query)
            landing_tables = [row[0] for row in self.cursor.fetchall()]

            # Verificar correspondencia en Transformation
            self.cursor.execute("USE DATABASE DEV_TRANSFORMATION")

            for landing_table in landing_tables[:20]:  # Analizar primeras 20
                # Buscar table relacionada en transformation
                base_name = landing_table.replace('RAW_', '').replace('STG_', '')

                check_transform_query = f"""
                SELECT TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'
                AND (
                    TABLE_NAME LIKE '%{base_name}%' OR
                    TABLE_NAME LIKE 'DIM_%{base_name}%' OR
                    TABLE_NAME LIKE 'FACT_%{base_name}%'
                )
                """

                self.cursor.execute(check_transform_query)
                transform_matches = self.cursor.fetchall()

                if transform_matches:
                    for match in transform_matches:
                        layer_relationships['landing_to_transform'].append({
                            'source': f"DEV_LANDING.SECURITY_ANALYTICS.{landing_table}",
                            'target': f"DEV_TRANSFORMATION.SECURITY_ANALYTICS.{match[0]}",
                            'confidence': 'detected'
                        })
                else:
                    print(f"  [WARNING] {landing_table} no tiene correspondencia en Transformation")

            print(f"  [FOUND] {len(layer_relationships['landing_to_transform'])} relaciones detectadas")

            self.analysis_results['relationship_analysis'] = layer_relationships

        except Exception as e:
            print(f"  [ERROR] {str(e)}")

    def generate_recommendations(self):
        """Genera recomendaciones basadas en el análisis"""
        print("\n" + "="*60)
        print("GENERANDO RECOMENDACIONES")
        print("="*60)

        recommendations = []

        # Analizar resultados de constraints
        for db, summary in self.analysis_results['constraints_summary'].items():
            if summary['tables_without_pk'] > 0:
                recommendations.append({
                    'severity': 'HIGH',
                    'database': db,
                    'issue': f"{summary['tables_without_pk']} tables sin Primary Key",
                    'recommendation': f"Agregar Primary Keys a las tables en {db}",
                    'impact': "Sin PKs, no se puede garantizar unicidad ni optimizar joins"
                })

            if summary['foreign_keys'] == 0 and db == 'DEV_TRANSFORMATION':
                recommendations.append({
                    'severity': 'CRITICAL',
                    'database': db,
                    'issue': "No hay Foreign Keys definidas en la capa de Transformation",
                    'recommendation': "Definir FKs entre tables DIM y FACT for mantener integridad",
                    'impact': "Sin FKs, no hay integridad referencial garantizada"
                })

        # Analizar modelo dimensional
        dim_issues = self.analysis_results.get('dimensional_model_issues', {})
        if dim_issues.get('issues'):
            for issue in dim_issues['issues']:
                recommendations.append({
                    'severity': 'HIGH',
                    'database': 'DEV_TRANSFORMATION',
                    'issue': issue,
                    'recommendation': "Implementar modelo estrella completo con DIM y FACT tables",
                    'impact': "Modelo dimensional incompleto afecta performance de queries"
                })

        # Analizar keys faltantes
        for db, missing in self.analysis_results['missing_keys'].items():
            critical_count = len([m for m in missing if (m.get('table_rows') or 0) > 1000])
            if critical_count > 0:
                recommendations.append({
                    'severity': 'MEDIUM',
                    'database': db,
                    'issue': f"{critical_count} columns críticas sin constraints que parecen ser keys",
                    'recommendation': "Revisar y agregar constraints apropiados a estas columns",
                    'impact': "Puede afectar performance y no hay garantía de integridad"
                })

        self.analysis_results['recommendations'] = recommendations

        # Imprimir recomendaciones
        print("\n[RECOMMENDATIONS]")
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. [{rec['severity']}] {rec['database']}")
            print(f"   Issue: {rec['issue']}")
            print(f"   Recomendación: {rec['recommendation']}")
            print(f"   Impacto: {rec['impact']}")

    def generate_detailed_report(self):
        """Genera reporte detallado en Excel y Markdown"""
        print("\n" + "="*60)
        print("GENERANDO REPORTE DETALLADO")
        print("="*60)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = Path("data_model_analysis")
        output_dir.mkdir(exist_ok=True)

        # Generate Excel
        excel_file = output_dir / f"data_model_analysis_{timestamp}.xlsx"

        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # 1. Resumen de Constraints
            constraints_data = []
            for db, summary in self.analysis_results['constraints_summary'].items():
                constraints_data.append({
                    'Database': db,
                    'Total Tables': summary['total_tables'],
                    'Tables with PK': summary['tables_with_pk'],
                    'Tables without PK': summary['tables_without_pk'],
                    'Foreign Keys': summary['foreign_keys'],
                    'Unique Constraints': summary['unique_constraints']
                })
            pd.DataFrame(constraints_data).to_excel(writer, sheet_name='Constraints Summary', index=False)

            # 2. Missing Keys
            all_missing_keys = []
            for db, missing in self.analysis_results['missing_keys'].items():
                for item in missing:
                    all_missing_keys.append({
                        'Database': db,
                        'Table': item['table'],
                        'Column': item['column'],
                        'Data Type': item['data_type'],
                        'Nullable': item['nullable'],
                        'Table Rows': item['table_rows']
                    })
            if all_missing_keys:
                pd.DataFrame(all_missing_keys).to_excel(writer, sheet_name='Missing Keys', index=False)

            # 3. Dimensional Model
            dim_model = self.analysis_results.get('dimensional_model_issues', {})
            if dim_model:
                # Dimensions
                if dim_model.get('dimensions'):
                    pd.DataFrame(dim_model['dimensions']).to_excel(writer, sheet_name='Dimensions', index=False)
                # Facts
                if dim_model.get('facts'):
                    pd.DataFrame(dim_model['facts']).to_excel(writer, sheet_name='Facts', index=False)

            # 4. Recommendations
            if self.analysis_results['recommendations']:
                pd.DataFrame(self.analysis_results['recommendations']).to_excel(
                    writer, sheet_name='Recommendations', index=False
                )

        print(f"  [SAVED] Excel: {excel_file}")

        # Generate Markdown
        md_file = output_dir / f"data_model_analysis_{timestamp}.md"

        md_content = []
        md_content.append("# Análisis del Modelo de Datos SECURITY_ANALYTICS")
        md_content.append(f"\nGenerado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Resumen Ejecutivo
        md_content.append("## Resumen Ejecutivo\n")

        total_issues = sum(s['tables_without_pk'] for s in self.analysis_results['constraints_summary'].values())
        critical_recs = len([r for r in self.analysis_results['recommendations'] if r['severity'] == 'CRITICAL'])

        md_content.append(f"- **Tablas sin Primary Key**: {total_issues}")
        md_content.append(f"- **Recomendaciones Críticas**: {critical_recs}")
        md_content.append(f"- **Total Recomendaciones**: {len(self.analysis_results['recommendations'])}\n")

        # Detalle por capa
        md_content.append("## Análisis por Capa\n")

        for db, summary in self.analysis_results['constraints_summary'].items():
            md_content.append(f"### {db}\n")
            md_content.append(f"- Total tables: {summary['total_tables']}")
            md_content.append(f"- Tablas con PK: {summary['tables_with_pk']}")
            md_content.append(f"- Tablas sin PK: **{summary['tables_without_pk']}**")
            md_content.append(f"- Foreign Keys: {summary['foreign_keys']}")
            md_content.append(f"- Unique Constraints: {summary['unique_constraints']}\n")

        # Modelo Dimensional
        dim_model = self.analysis_results.get('dimensional_model_issues', {})
        if dim_model:
            md_content.append("## Análisis del Modelo Dimensional\n")
            md_content.append(f"- **Dimensiones encontradas**: {len(dim_model.get('dimensions', []))}")
            md_content.append(f"- **Tablas Fact encontradas**: {len(dim_model.get('facts', []))}")
            md_content.append(f"- **Otras tables**: {len(dim_model.get('others', []))}\n")

            if dim_model.get('issues'):
                md_content.append("### Issues Detectados:\n")
                for issue in dim_model['issues']:
                    md_content.append(f"- {issue}")
                md_content.append("")

        # Recomendaciones
        md_content.append("## Recomendaciones Prioritarias\n")

        for severity in ['CRITICAL', 'HIGH', 'MEDIUM']:
            recs = [r for r in self.analysis_results['recommendations'] if r['severity'] == severity]
            if recs:
                md_content.append(f"### {severity}\n")
                for rec in recs:
                    md_content.append(f"**{rec['database']}**")
                    md_content.append(f"- Issue: {rec['issue']}")
                    md_content.append(f"- Recomendación: {rec['recommendation']}")
                    md_content.append(f"- Impacto: {rec['impact']}\n")

        # Script SQL de mejoras sugeridas
        md_content.append("## Scripts SQL Sugeridos\n")
        md_content.append("```sql")
        md_content.append("-- Ejemplo: Agregar Primary Keys")

        for db, summary in self.analysis_results['constraints_summary'].items():
            if summary['tables_without_pk'] > 0:
                md_content.append(f"\n-- En {db}")
                md_content.append(f"-- Identificar candidata a PK con:")
                md_content.append(f"SELECT TABLE_NAME, COLUMN_NAME")
                md_content.append(f"FROM {db}.INFORMATION_SCHEMA.COLUMNS")
                md_content.append(f"WHERE TABLE_SCHEMA = 'SECURITY_ANALYTICS'")
                md_content.append(f"AND (COLUMN_NAME LIKE '%_ID' OR COLUMN_NAME = 'ID');")

        md_content.append("```\n")

        # Guardar Markdown
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_content))

        print(f"  [SAVED] Markdown: {md_file}")

        # Guardar JSON con all the results
        json_file = output_dir / f"analysis_results_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, default=str)

        print(f"  [SAVED] JSON: {json_file}")

    def run_complete_analysis(self):
        """Execute el análisis completo"""
        try:
            self.connect()
            self.analyze_constraints_per_layer()
            self.analyze_dimensional_model()
            self.analyze_missing_keys()
            self.analyze_referential_integrity()
            self.generate_recommendations()
            self.generate_detailed_report()

            print("\n" + "="*60)
            print("[SUCCESS] ANÁLISIS COMPLETADO")
            print("="*60)
            print("\nRevisa la folder 'data_model_analysis' for los reportes detallados")

        except Exception as e:
            print(f"\n[ERROR] {str(e)}")
        finally:
            if self.conn:
                self.conn.close()
                print("\n[INFO] Conexión cerrada")


def main():
    print("\n" + "="*60)
    print("   ANÁLISIS DE CALIDAD DEL MODELO DE DATOS")
    print("   SECURITY_ANALYTICS - GenericCorp")
    print("="*60)

    analyzer = DataModelAnalyzer()
    analyzer.run_complete_analysis()

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())