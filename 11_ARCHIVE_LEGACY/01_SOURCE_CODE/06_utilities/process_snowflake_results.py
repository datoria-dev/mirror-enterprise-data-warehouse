import pandas as pd
import graphviz
import json
from typing import Dict, List
import re

class SnowflakeERDFromResults:
    def __init__(self):
        """Initialize el generador de ERD from resultados"""
        self.tables_info = {}
        self.relationships = []

    def process_csv_results(self, csv_file: str):
        """Procesa un file CSV con the results de las queries SQL"""
        try:
            df = pd.read_csv(csv_file)
            print(f"Procesando {len(df)} filas de resultados...")

            # Agrupar por table
            for _, row in df.iterrows():
                db_name = row['DATABASE_NAME']
                schema_name = row['SCHEMA_NAME']
                table_name = row['TABLE_NAME']
                full_name = f"{db_name}.{schema_name}.{table_name}"

                if full_name not in self.tables_info:
                    self.tables_info[full_name] = {
                        'database': db_name,
                        'schema': schema_name,
                        'name': table_name,
                        'type': row.get('TABLE_TYPE', 'TABLE'),
                        'comment': row.get('COMMENT', ''),
                        'columns': []
                    }

                # Si tiene information de columns
                if 'COLUMN_NAME' in row:
                    self.tables_info[full_name]['columns'].append({
                        'name': row['COLUMN_NAME'],
                        'type': row['DATA_TYPE'],
                        'nullable': row.get('IS_NULLABLE', 'YES'),
                        'position': row.get('ORDINAL_POSITION', 0)
                    })

            print(f"Encontradas {len(self.tables_info)} tables/views")
            return True

        except Exception as e:
            print(f"Error procesando CSV: {e}")
            return False

    def process_json_results(self, json_file: str):
        """Procesa un file JSON con the results"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for table_data in data:
                db_name = table_data['database']
                schema_name = table_data['schema']
                table_name = table_data['table_name']
                full_name = f"{db_name}.{schema_name}.{table_name}"

                self.tables_info[full_name] = {
                    'database': db_name,
                    'schema': schema_name,
                    'name': table_name,
                    'type': table_data.get('type', 'TABLE'),
                    'comment': table_data.get('comment', ''),
                    'columns': table_data.get('columns', [])
                }

            print(f"Procesadas {len(self.tables_info)} tables from JSON")
            return True

        except Exception as e:
            print(f"Error procesando JSON: {e}")
            return False

    def process_manual_input(self):
        """Permite ingresar manualmente la information de las tables"""
        print("\n" + "="*60)
        print("INGRESO MANUAL DE METADATA")
        print("="*60)
        print("\nPuedes copiar y pegar the results de tus queries SQL.")
        print("Formato esperado: DATABASE,SCHEMA,TABLE,TYPE,COLUMNS")
        print("Escribe 'FIN' cuando termines.\n")

        while True:
            line = input("Ingresa línea de data (o 'FIN'): ").strip()
            if line.upper() == 'FIN':
                break

            try:
                parts = line.split(',')
                if len(parts) >= 4:
                    db_name = parts[0].strip()
                    schema_name = parts[1].strip()
                    table_name = parts[2].strip()
                    table_type = parts[3].strip()
                    full_name = f"{db_name}.{schema_name}.{table_name}"

                    if full_name not in self.tables_info:
                        self.tables_info[full_name] = {
                            'database': db_name,
                            'schema': schema_name,
                            'name': table_name,
                            'type': table_type,
                            'comment': '',
                            'columns': []
                        }
                    print(f"✓ Agregada: {table_name}")
            except:
                print("✗ Formato incorrecto, intenta de nuevo")

        # Pedir columns for each table
        for full_name, table_info in self.tables_info.items():
            print(f"\nColumnas for {table_info['name']} (escribe 'NEXT' for following table):")
            while True:
                col = input("  Columna (nombre,tipo) o 'NEXT': ").strip()
                if col.upper() == 'NEXT':
                    break
                try:
                    col_parts = col.split(',')
                    table_info['columns'].append({
                        'name': col_parts[0].strip(),
                        'type': col_parts[1].strip() if len(col_parts) > 1 else 'VARCHAR',
                        'nullable': 'YES'
                    })
                    print(f"    ✓ {col_parts[0]}")
                except:
                    print("    ✗ Formato: nombre,tipo")

    def infer_relationships(self):
        """Infiere relaciones basándose en nombres de columns"""
        print("\nAnalizando relaciones...")

        # Patrones comunes for FKs
        fk_patterns = ['_ID', '_KEY', '_CODE', '_SK', '_FK']

        for table1_name, table1_info in self.tables_info.items():
            for col in table1_info['columns']:
                col_name = col['name'].upper()

                # Buscar posibles FKs
                if any(pattern in col_name for pattern in fk_patterns):
                    # Extract nombre base
                    base_name = col_name
                    for pattern in fk_patterns:
                        base_name = base_name.replace(pattern, '')

                    # Buscar table destino
                    for table2_name, table2_info in self.tables_info.items():
                        if table1_name != table2_name:
                            table2_base = table2_info['name'].upper()

                            # Verificar coincidencia
                            if (base_name in table2_base or
                                table2_base in base_name or
                                base_name.replace('_', '') == table2_base.replace('_', '')):

                                # Evitar duplicados
                                if not any(r['from'] == table1_name and
                                         r['to'] == table2_name and
                                         r['column'] == col['name']
                                         for r in self.relationships):

                                    self.relationships.append({
                                        'from': table1_name,
                                        'to': table2_name,
                                        'column': col['name'],
                                        'type': 'INFERRED'
                                    })
                                    print(f"  → {table1_info['name']}.{col['name']} -> {table2_info['name']}")

        print(f"\nTotal de relaciones inferidas: {len(self.relationships)}")

    def generate_erd(self, output_file='snowflake_erd'):
        """Genera el diagrama ERD"""
        print("\n" + "="*60)
        print("GENERANDO DIAGRAMA ERD")
        print("="*60)

        # Createte grafo
        dot = graphviz.Digraph(comment='Snowflake ERD - SECURITY_ANALYTICS')
        dot.attr(rankdir='TB')
        dot.attr('node', shape='none', fontname='Arial')

        # Colores por capa
        colors = {
            'DEV_LANDING': ('#FFE5CC', '#FF9933'),
            'DEV_TRANSFORMATION': ('#CCE5FF', '#3399FF'),
            'DEV_REPORTING': ('#CCFFCC', '#33CC33')
        }

        # Createte subgrafos por base de data
        databases = {}
        for table_name, table_info in self.tables_info.items():
            db = table_info['database'].upper()
            if db not in databases:
                databases[db] = []
            databases[db].append((table_name, table_info))

        for db_name, tables in databases.items():
            with dot.subgraph(name=f'cluster_{db_name}') as sub:
                sub.attr(label=db_name, style='filled', fillcolor='#F5F5F5')

                for table_name, table_info in tables:
                    bgcolor, header_color = colors.get(db_name, ('#FFFFFF', '#808080'))

                    # Createte table HTML
                    label = f'''<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" BGCOLOR="{bgcolor}">
                        <TR><TD COLSPAN="2" BGCOLOR="{header_color}" ALIGN="CENTER">
                        <FONT COLOR="WHITE"><B>{table_info['name']}</B></FONT><BR/>
                        <FONT COLOR="WHITE" POINT-SIZE="9">({table_info['type']})</FONT>
                        </TD></TR>'''

                    # Encabezados
                    label += '''<TR>
                        <TD BGCOLOR="#E0E0E0"><B>Column</B></TD>
                        <TD BGCOLOR="#E0E0E0"><B>Type</B></TD>
                    </TR>'''

                    # Columnas (máximo 12)
                    if table_info['columns']:
                        for i, col in enumerate(table_info['columns'][:12]):
                            icon = ''
                            col_upper = col['name'].upper()
                            if ('ID' in col_upper or 'PK' in col_upper) and i == 0:
                                icon = '🔑 '
                            elif any(fk in col_upper for fk in ['_FK', '_KEY', '_ID']) and i > 0:
                                icon = '🔗 '

                            label += f'''<TR>
                                <TD ALIGN="LEFT">{icon}{col['name']}</TD>
                                <TD ALIGN="LEFT"><FONT POINT-SIZE="9">{col['type'][:15]}</FONT></TD>
                            </TR>'''

                        if len(table_info['columns']) > 12:
                            label += f'''<TR><TD COLSPAN="2" ALIGN="CENTER" BGCOLOR="#F0F0F0">
                                <FONT POINT-SIZE="8"><I>+{len(table_info['columns']) - 12} más...</I></FONT>
                            </TD></TR>'''
                    else:
                        label += '''<TR><TD COLSPAN="2" ALIGN="CENTER">
                            <FONT POINT-SIZE="8"><I>Sin columns definidas</I></FONT>
                        </TD></TR>'''

                    label += '</TABLE>>'
                    sub.node(table_name, label=label)

        # Agregar relaciones
        for rel in self.relationships:
            dot.edge(rel['from'], rel['to'],
                    label=f" {rel['column']} ",
                    style='dashed',
                    color='blue',
                    fontsize='8',
                    arrowhead='normal')

        # Renderizar
        try:
            dot.render(output_file, format='png', cleanup=True, view=False)
            print(f"✅ Diagrama generado: {output_file}.png")

            dot.render(output_file, format='svg', cleanup=True, view=False)
            print(f"✅ Versión SVG: {output_file}.svg")

            with open(f"{output_file}.dot", 'w', encoding='utf-8') as f:
                f.write(dot.source)
            print(f"✅ Archivo DOT: {output_file}.dot")

        except Exception as e:
            print(f"⚠️ Error generando diagrama: {e}")
            with open(f"{output_file}.dot", 'w', encoding='utf-8') as f:
                f.write(dot.source)
            print(f"✅ Archivo DOT guardado: {output_file}.dot")

    def generate_report(self, output_file='erd_report.md'):
        """Genera reporte en Markdown"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 📊 Snowflake ERD Report - SECURITY_ANALYTICS\n\n")

            # Estadísticas
            f.write("## 📈 Estadísticas\n\n")
            total_tables = len(self.tables_info)
            total_cols = sum(len(t['columns']) for t in self.tables_info.values())
            f.write(f"- **Total de Objetos:** {total_tables}\n")
            f.write(f"- **Total de Columnas:** {total_cols}\n")
            f.write(f"- **Relaciones Identifieachs:** {len(self.relationships)}\n\n")

            # Por base de data
            f.write("## 🗂️ Objetos por Capa\n\n")
            for db in ['DEV_LANDING', 'DEV_TRANSFORMATION', 'DEV_REPORTING']:
                tables = [t for t in self.tables_info.values() if t['database'].upper() == db]
                if tables:
                    f.write(f"### {db}\n\n")
                    f.write("| Tabla | Tipo | Columnas |\n")
                    f.write("|-------|------|----------|\n")
                    for t in sorted(tables, key=lambda x: x['name']):
                        f.write(f"| {t['name']} | {t['type']} | {len(t['columns'])} |\n")
                    f.write("\n")

            # Relaciones
            if self.relationships:
                f.write("## 🔗 Relaciones\n\n")
                f.write("| Origen | Columna | Destino |\n")
                f.write("|--------|---------|----------|\n")
                for rel in self.relationships:
                    from_table = self.tables_info[rel['from']]['name']
                    to_table = self.tables_info[rel['to']]['name']
                    f.write(f"| {from_table} | {rel['column']} | {to_table} |\n")

        print(f"✅ Reporte generado: {output_file}")


def main():
    """Function main"""
    print("="*60)
    print(" SNOWFLAKE ERD GENERATOR")
    print(" Desde resultados SQL")
    print("="*60)

    generator = SnowflakeERDFromResults()

    print("\n¿Cómo quieres proporcionar los data?")
    print("1. Archivo CSV con resultados")
    print("2. Archivo JSON con estructura")
    print("3. Ingreso manual")
    print("4. Usar data de ejemplo")

    choice = input("\nOpción (1-4): ").strip()

    if choice == '1':
        csv_file = input("Ruta del file CSV: ").strip()
        generator.process_csv_results(csv_file)

    elif choice == '2':
        json_file = input("Ruta del file JSON: ").strip()
        generator.process_json_results(json_file)

    elif choice == '3':
        generator.process_manual_input()

    elif choice == '4':
        # Datos de ejemplo for demostración
        print("\nUsando data de ejemplo...")
        example_tables = {
            'DEV_LANDING.SECURITY_ANALYTICS.RAW_KPI_DATA': {
                'database': 'DEV_LANDING',
                'schema': 'SECURITY_ANALYTICS',
                'name': 'RAW_KPI_DATA',
                'type': 'TABLE',
                'comment': 'Datos crudos de KPIs',
                'columns': [
                    {'name': 'ID', 'type': 'NUMBER', 'nullable': 'NO'},
                    {'name': 'KPI_ID', 'type': 'VARCHAR', 'nullable': 'NO'},
                    {'name': 'VALUE', 'type': 'NUMBER', 'nullable': 'YES'},
                    {'name': 'TIMESTAMP', 'type': 'TIMESTAMP', 'nullable': 'NO'}
                ]
            },
            'DEV_TRANSFORMATION.SECURITY_ANALYTICS.DIM_KPI': {
                'database': 'DEV_TRANSFORMATION',
                'schema': 'SECURITY_ANALYTICS',
                'name': 'DIM_KPI',
                'type': 'TABLE',
                'comment': 'Dimensión de KPIs',
                'columns': [
                    {'name': 'KPI_ID', 'type': 'VARCHAR', 'nullable': 'NO'},
                    {'name': 'KPI_NAME', 'type': 'VARCHAR', 'nullable': 'NO'},
                    {'name': 'CATEGORY', 'type': 'VARCHAR', 'nullable': 'YES'}
                ]
            },
            'DEV_TRANSFORMATION.SECURITY_ANALYTICS.FACT_KPI_METRICS': {
                'database': 'DEV_TRANSFORMATION',
                'schema': 'SECURITY_ANALYTICS',
                'name': 'FACT_KPI_METRICS',
                'type': 'TABLE',
                'comment': 'Tabla de hechos de métricas',
                'columns': [
                    {'name': 'METRIC_ID', 'type': 'NUMBER', 'nullable': 'NO'},
                    {'name': 'KPI_ID', 'type': 'VARCHAR', 'nullable': 'NO'},
                    {'name': 'DATE_ID', 'type': 'NUMBER', 'nullable': 'NO'},
                    {'name': 'VALUE', 'type': 'NUMBER', 'nullable': 'YES'}
                ]
            },
            'DEV_REPORTING.SECURITY_ANALYTICS.VW_KPI_DASHBOARD': {
                'database': 'DEV_REPORTING',
                'schema': 'SECURITY_ANALYTICS',
                'name': 'VW_KPI_DASHBOARD',
                'type': 'VIEW',
                'comment': 'Vista for dashboard',
                'columns': [
                    {'name': 'KPI_ID', 'type': 'VARCHAR', 'nullable': 'NO'},
                    {'name': 'KPI_NAME', 'type': 'VARCHAR', 'nullable': 'NO'},
                    {'name': 'CURRENT_VALUE', 'type': 'NUMBER', 'nullable': 'YES'},
                    {'name': 'TREND', 'type': 'VARCHAR', 'nullable': 'YES'}
                ]
            }
        }
        generator.tables_info = example_tables

    else:
        print("Opción inválida")
        return

    # Inferir relaciones
    generator.infer_relationships()

    # Generate ERD
    generator.generate_erd('snowflake_itseckpi_erd')

    # Generate reporte
    generator.generate_report('snowflake_itseckpi_report.md')

    print("\n" + "="*60)
    print(" PROCESO COMPLETADO")
    print("="*60)
    print("\n📁 Archivos generados:")
    print("  ├── 📊 snowflake_itseckpi_erd.png")
    print("  ├── 📊 snowflake_itseckpi_erd.svg")
    print("  ├── 📝 snowflake_itseckpi_erd.dot")
    print("  └── 📄 snowflake_itseckpi_report.md")


if __name__ == "__main__":
    main()