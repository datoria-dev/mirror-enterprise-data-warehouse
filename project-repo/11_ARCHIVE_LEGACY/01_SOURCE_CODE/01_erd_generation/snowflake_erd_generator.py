import snowflake.connector
import pandas as pd
import graphviz
from typing import Dict, List, Tuple
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class SnowflakeERDGenerator:
    def __init__(self, account, user, password, warehouse, role=None):
        """Initialize la connection a Snowflake"""
        self.connection_forms = {
            'account': account,
            'user': user,
            'password': password,
            'warehouse': warehouse
        }
        if role:
            self.connection_forms['role'] = role

        self.tables_info = {}
        self.relationships = []

    def connect_and_explore(self, database: str, schema: str = 'SECURITY_ANALYTICS'):
        """Conecta a una base de data específica y explora el esquema"""
        try:
            # Establishr connection
            conn = snowflake.connector.connect(
                **self.connection_forms,
                database=database,
                schema=schema
            )
            cursor = conn.cursor()

            print(f"\n{'='*60}")
            print(f"Explorando {database}.{schema}")
            print(f"{'='*60}")

            # Obtener todas las tables
            tables_query = """
            SELECT TABLE_NAME, TABLE_TYPE, COMMENT
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = %s
            ORDER BY TABLE_NAME
            """
            cursor.execute(tables_query, (schema,))
            tables = cursor.fetchall()

            print(f"\nEncontradas {len(tables)} tables/views:")

            for table in tables:
                table_name = table[0]
                table_type = table[1]
                table_comment = table[2] or ''
                full_table_name = f"{database}.{schema}.{table_name}"

                print(f"  - {table_name} ({table_type})")

                # Obtener columns de each table
                columns_query = """
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE,
                       COLUMN_DEFAULT, COMMENT
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                ORDER BY ORDINAL_POSITION
                """
                cursor.execute(columns_query, (schema, table_name))
                columns = cursor.fetchall()

                self.tables_info[full_table_name] = {
                    'database': database,
                    'schema': schema,
                    'name': table_name,
                    'type': table_type,
                    'comment': table_comment,
                    'columns': [
                        {
                            'name': col[0],
                            'type': col[1],
                            'nullable': col[2],
                            'default': col[3],
                            'comment': col[4] or ''
                        }
                        for col in columns
                    ]
                }

            # Intentar obtener constraints (si existen)
            try:
                constraints_query = """
                SELECT
                    tc.TABLE_NAME,
                    tc.CONSTRAINT_NAME,
                    tc.CONSTRAINT_TYPE,
                    kcu.COLUMN_NAME,
                    rc.UNIQUE_CONSTRAINT_NAME,
                    rc.REFERENCED_TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                LEFT JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
                    ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
                    AND tc.TABLE_SCHEMA = kcu.TABLE_SCHEMA
                LEFT JOIN INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc
                    ON tc.CONSTRAINT_NAME = rc.CONSTRAINT_NAME
                    AND tc.TABLE_SCHEMA = rc.CONSTRAINT_SCHEMA
                WHERE tc.TABLE_SCHEMA = %s
                """
                cursor.execute(constraints_query, (schema,))
                constraints = cursor.fetchall()

                if constraints:
                    print(f"\nConstraints encontradas: {len(constraints)}")
                    for const in constraints:
                        if const[2] == 'FOREIGN KEY' and const[5]:
                            self.relationships.append({
                                'from': f"{database}.{schema}.{const[0]}",
                                'to': f"{database}.{schema}.{const[5]}",
                                'column': const[3],
                                'type': 'FK'
                            })
            except:
                print("  (No se pudieron obtener constraints explícitas)")

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Error conectando a {database}: {str(e)}")

    def infer_relationships(self):
        """Infiere relaciones basándose en nombres de columns y patrones comunes"""
        print("\n" + "="*60)
        print("Analizando relaciones implícitas...")
        print("="*60)

        # Patrones comunes for identificar relaciones
        id_patterns = ['_ID', '_KEY', '_CODE', '_SK', '_PK']

        for table1_name, table1_info in self.tables_info.items():
            for col1 in table1_info['columns']:
                col_name = col1['name'].upper()

                # Buscar columns que parecen ser foreign keys
                if any(pattern in col_name for pattern in id_patterns):
                    # Extract el nombre base de la table referenciada
                    base_name = col_name.replace('_ID', '').replace('_KEY', '').replace('_CODE', '').replace('_SK', '').replace('_PK', '')

                    # Buscar tables que coincidan con el nombre base
                    for table2_name, table2_info in self.tables_info.items():
                        if table1_name != table2_name:
                            table2_base = table2_info['name'].upper()

                            # Verificar si hay coincidencia
                            if base_name in table2_base or table2_base in base_name:
                                # Verificar que la table destino tiene una column ID correspondiente
                                for col2 in table2_info['columns']:
                                    if col2['name'].upper() in [col_name, base_name + '_ID', base_name + '_KEY', 'ID', base_name]:
                                        # Evitar duplicados
                                        rel_exists = any(
                                            r['from'] == table1_name and
                                            r['to'] == table2_name and
                                            r['column'] == col1['name']
                                            for r in self.relationships
                                        )

                                        if not rel_exists:
                                            self.relationships.append({
                                                'from': table1_name,
                                                'to': table2_name,
                                                'column': col1['name'],
                                                'type': 'INFERRED'
                                            })
                                            print(f"  Relación inferida: {table1_info['name']}.{col1['name']} -> {table2_info['name']}")
                                        break

        print(f"\nTotal de relaciones encontradas: {len(self.relationships)}")

    def generate_erd(self, output_format='png', output_file='snowflake_erd'):
        """Genera el diagrama ERD using Graphviz"""
        print("\n" + "="*60)
        print("Generando diagrama ERD...")
        print("="*60)

        # Createte el grafo
        dot = graphviz.Digraph(comment='Snowflake ERD - Schema SECURITY_ANALYTICS')
        dot.attr(rankdir='LR')
        dot.attr('node', shape='none')

        # Colores por capa
        layer_colors = {
            'DEV_LANDING': '#FFE5CC',
            'DEV_TRANSFORMATION': '#CCE5FF',
            'DEV_REPORTING': '#CCFFCC'
        }

        # Agregar tables como nodos
        for table_name, table_info in self.tables_info.items():
            db = table_info['database'].upper()
            bgcolor = layer_colors.get(db, '#FFFFFF')

            # Createte HTML for la table
            label = f'''<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" BGCOLOR="{bgcolor}">
                <TR><TD COLSPAN="3" BGCOLOR="{'#FFD4A3' if db == 'DEV_LANDING' else '#A3D4FF' if db == 'DEV_TRANSFORMATION' else '#A3FFA3'}">
                <B>{table_info['name']}</B><BR/>
                <FONT POINT-SIZE="8">({table_info['type']} - {db})</FONT>
                </TD></TR>'''

            # Agregar columns maines (limitado a 10 for no saturar)
            for i, col in enumerate(table_info['columns'][:10]):
                pk_marker = ''
                # Marcar posibles PKs
                if 'ID' in col['name'].upper() or 'KEY' in col['name'].upper():
                    pk_marker = '🔑 '

                label += f'''<TR>
                    <TD ALIGN="LEFT">{pk_marker}{col['name']}</TD>
                    <TD ALIGN="LEFT"><FONT POINT-SIZE="8">{col['type']}</FONT></TD>
                    <TD ALIGN="LEFT"><FONT POINT-SIZE="8">{'NULL' if col['nullable'] == 'YES' else 'NOT NULL'}</FONT></TD>
                </TR>'''

            if len(table_info['columns']) > 10:
                label += f'''<TR><TD COLSPAN="3" ALIGN="CENTER">
                    <FONT POINT-SIZE="8">... y {len(table_info['columns']) - 10} columns más</FONT>
                </TD></TR>'''

            label += '</TABLE>>'

            dot.node(table_name, label=label)

        # Agregar relaciones
        for rel in self.relationships:
            style = 'solid' if rel['type'] == 'FK' else 'dashed'
            color = 'black' if rel['type'] == 'FK' else 'blue'
            dot.edge(rel['from'], rel['to'],
                    label=rel['column'],
                    style=style,
                    color=color,
                    fontsize='8')

        # Renderizar
        try:
            dot.render(output_file, format=output_format, cleanup=True, view=False)
            print(f"\nDiagrama generado exitosamente: {output_file}.{output_format}")

            # También generate versión DOT for edición posterior
            with open(f"{output_file}.dot", 'w') as f:
                f.write(dot.source)
            print(f"Archivo DOT también generado: {output_file}.dot")

        except Exception as e:
            print(f"Error generando el diagrama: {str(e)}")
            print("\nIntentando guardar solo el file DOT...")
            with open(f"{output_file}.dot", 'w') as f:
                f.write(dot.source)
            print(f"Archivo DOT guardado: {output_file}.dot")

    def generate_summary_report(self, output_file='erd_summary.md'):
        """Genera un reporte resumido en Markdown"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Snowflake ERD Report - Schema SECURITY_ANALYTICS\n\n")

            # Resumen por base de data
            f.write("## Resumen por Capa\n\n")

            for db in ['DEV_LANDING', 'DEV_TRANSFORMATION', 'DEV_REPORTING']:
                tables_in_db = [t for t in self.tables_info.values() if t['database'].upper() == db]
                f.write(f"### {db}\n")
                f.write(f"- Total de objetos: {len(tables_in_db)}\n")
                f.write(f"- Tablas: {len([t for t in tables_in_db if t['type'] == 'BASE TABLE'])}\n")
                f.write(f"- Views: {len([t for t in tables_in_db if t['type'] == 'VIEW'])}\n\n")

                if tables_in_db:
                    f.write("#### Objetos:\n")
                    for table in tables_in_db:
                        f.write(f"- **{table['name']}** ({table['type']}): {len(table['columns'])} columns\n")
                    f.write("\n")

            # Relaciones
            f.write("## Relaciones Identifieachs\n\n")
            f.write(f"Total de relaciones: {len(self.relationships)}\n\n")

            for rel in self.relationships:
                rel_type = "Foreign Key" if rel['type'] == 'FK' else "Inferida"
                from_table = self.tables_info[rel['from']]['name']
                to_table = self.tables_info[rel['to']]['name']
                f.write(f"- {from_table}.{rel['column']} → {to_table} ({rel_type})\n")

        print(f"\nReporte generado: {output_file}")


# Function main
def main():
    print("="*60)
    print("SNOWFLAKE ERD GENERATOR - SCHEMA SECURITY_ANALYTICS")
    print("="*60)

    # Configuración de connection
    # Necesitarás proporcionar tus credenciales
    print("\nNecesitas configure tus credenciales de Snowflake.")
    print("Puedes hacerlo de dos formas:")
    print("1. Createte un file .env con las variables")
    print("2. Modificar directamente los valores en el código\n")

    # Valores por defecto (deberás cambiarlos)
    SNOWFLAKE_ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT', 'tu_cuenta.snowflakecomputing.com')
    SNOWFLAKE_USER = os.getenv('SNOWFLAKE_USER', 'tu_usuario')
    SNOWFLAKE_PASSWORD = os.getenv('SNOWFLAKE_PASSWORD', 'tu_password')
    SNOWFLAKE_WAREHOUSE = os.getenv('SNOWFLAKE_WAREHOUSE', 'tu_warehouse')
    SNOWFLAKE_ROLE = os.getenv('SNOWFLAKE_ROLE', None)

    # Createte generador
    generator = SnowflakeERDGenerator(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        warehouse=SNOWFLAKE_WAREHOUSE,
        role=SNOWFLAKE_ROLE
    )

    # Explorar each base de data
    databases = ['DEV_LANDING', 'DEV_TRANSFORMATION', 'DEV_REPORTING']

    for db in databases:
        generator.connect_and_explore(db, 'SECURITY_ANALYTICS')

    # Inferir relaciones adicionales
    generator.infer_relationships()

    # Generate el ERD
    generator.generate_erd(output_format='png', output_file='snowflake_itseckpi_erd')

    # Generate reporte
    generator.generate_summary_report('snowflake_itseckpi_summary.md')

    print("\n" + "="*60)
    print("PROCESO COMPLETADO")
    print("="*60)
    print("\nArchivos generados:")
    print("  - snowflake_itseckpi_erd.png (Diagrama ERD)")
    print("  - snowflake_itseckpi_erd.dot (Archivo fuente for edición)")
    print("  - snowflake_itseckpi_summary.md (Reporte resumido)")


if __name__ == "__main__":
    main()