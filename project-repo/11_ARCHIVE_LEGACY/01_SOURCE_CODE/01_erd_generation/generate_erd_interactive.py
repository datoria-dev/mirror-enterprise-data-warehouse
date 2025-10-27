import snowflake.connector
import pandas as pd
import graphviz
from typing import Dict, List, Tuple
import getpass

class SnowflakeERDGenerator:
    def __init__(self):
        """Initialize el generador de ERD"""
        self.tables_info = {}
        self.relationships = []
        self.connection = None

    def get_credentials(self):
        """Solicita las credenciales al usuario"""
        print("\n" + "="*60)
        print("CONFIGURACIÓN DE CONEXIÓN A SNOWFLAKE")
        print("="*60)

        print("\nIngresa tus credenciales de Snowflake:")
        account = input("Account (ej: abc123.us-east-1): ")
        user = input("Usuario: ")
        password = getpass.getpass("Contraseña: ")
        warehouse = input("Warehouse: ")
        role = input("Role (optional, presiona Enter for omitir): ").strip()

        return {
            'account': account,
            'user': user,
            'password': password,
            'warehouse': warehouse,
            'role': role if role else None
        }

    def connect_and_explore(self, credentials: dict, database: str, schema: str = 'SECURITY_ANALYTICS'):
        """Conecta a una base de data específica y explora el esquema"""
        try:
            # Establishr connection
            conn_forms = {k: v for k, v in credentials.items() if v is not None}
            conn_forms['database'] = database
            conn_forms['schema'] = schema

            print(f"\nConectando a {database}.{schema}...")
            conn = snowflake.connector.connect(**conn_forms)
            cursor = conn.cursor()

            print(f"\n{'='*60}")
            print(f"Explorando {database}.{schema}")
            print(f"{'='*60}")

            # Obtener todas las tables y views
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

            # Intentar obtener constraints
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
            except Exception as e:
                print(f"  (No se pudieron obtener constraints explícitas: {str(e)})")

            cursor.close()
            conn.close()
            return True

        except Exception as e:
            print(f"Error conectando a {database}: {str(e)}")
            return False

    def infer_relationships(self):
        """Infiere relaciones basándose en nombres de columns y patrones comunes"""
        print("\n" + "="*60)
        print("Analizando relaciones implícitas...")
        print("="*60)

        # Patrones comunes for identificar relaciones
        id_patterns = ['_ID', '_KEY', '_CODE', '_SK', '_PK']

        relationships_found = 0

        for table1_name, table1_info in self.tables_info.items():
            for col1 in table1_info['columns']:
                col_name = col1['name'].upper()

                # Buscar columns que parecen ser foreign keys
                if any(pattern in col_name for pattern in id_patterns):
                    # Extract el nombre base de la table referenciada
                    base_name = col_name
                    for pattern in id_patterns:
                        base_name = base_name.replace(pattern, '')

                    # Buscar tables que coincidan con el nombre base
                    for table2_name, table2_info in self.tables_info.items():
                        if table1_name != table2_name:
                            table2_base = table2_info['name'].upper()

                            # Verificar si hay coincidencia
                            if (base_name in table2_base or table2_base in base_name or
                                base_name == table2_base or
                                table2_base.replace('_', '') == base_name.replace('_', '')):

                                # Verificar que no sea duplicado
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
                                    relationships_found += 1
                                    print(f"  Relación inferida: {table1_info['name']}.{col1['name']} -> {table2_info['name']}")

        print(f"\nRelaciones inferidas encontradas: {relationships_found}")
        print(f"Total de relaciones: {len(self.relationships)}")

    def generate_erd(self, output_format='png', output_file='snowflake_erd'):
        """Genera el diagrama ERD using Graphviz"""
        print("\n" + "="*60)
        print("Generando diagrama ERD...")
        print("="*60)

        # Createte el grafo
        dot = graphviz.Digraph(comment='Snowflake ERD - Schema SECURITY_ANALYTICS')
        dot.attr(rankdir='TB')  # Top to Bottom
        dot.attr('node', shape='none', fontname='Arial')
        dot.attr('graph', bgcolor='white', pad='0.5')

        # Colores por capa
        layer_colors = {
            'DEV_LANDING': '#FFE5CC',
            'DEV_TRANSFORMATION': '#CCE5FF',
            'DEV_REPORTING': '#CCFFCC'
        }

        header_colors = {
            'DEV_LANDING': '#FF9933',
            'DEV_TRANSFORMATION': '#3399FF',
            'DEV_REPORTING': '#33CC33'
        }

        # Createte subgrafos por base de data
        for db_name in ['DEV_LANDING', 'DEV_TRANSFORMATION', 'DEV_REPORTING']:
            with dot.subgraph(name=f'cluster_{db_name}') as sub:
                sub.attr(label=db_name, style='filled', fillcolor='#F0F0F0', fontname='Arial Bold')

                # Agregar tables de esta base de data
                db_tables = [t for t in self.tables_info.items()
                           if t[1]['database'].upper() == db_name]

                for table_name, table_info in db_tables:
                    bgcolor = layer_colors.get(db_name, '#FFFFFF')
                    header_color = header_colors.get(db_name, '#808080')

                    # Createte HTML for la table
                    label = f'''<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" BGCOLOR="{bgcolor}">
                        <TR><TD COLSPAN="3" BGCOLOR="{header_color}" ALIGN="CENTER">
                        <FONT COLOR="WHITE"><B>{table_info['name']}</B></FONT><BR/>
                        <FONT COLOR="WHITE" POINT-SIZE="9">({table_info['type']})</FONT>
                        </TD></TR>'''

                    # Agregar encabezados de columns
                    label += '''<TR>
                        <TD BGCOLOR="#E0E0E0"><B>Column</B></TD>
                        <TD BGCOLOR="#E0E0E0"><B>Type</B></TD>
                        <TD BGCOLOR="#E0E0E0"><B>Nullable</B></TD>
                    </TR>'''

                    # Agregar columns (máximo 15 for no saturar)
                    max_cols = 15
                    for i, col in enumerate(table_info['columns'][:max_cols]):
                        # Marcar posibles PKs/FKs
                        icon = ''
                        if any(pk in col['name'].upper() for pk in ['_PK', '_ID']) and i == 0:
                            icon = '🔑 '
                        elif any(fk in col['name'].upper() for fk in ['_FK', '_KEY', '_ID']) and i > 0:
                            icon = '🔗 '

                        label += f'''<TR>
                            <TD ALIGN="LEFT">{icon}{col['name']}</TD>
                            <TD ALIGN="LEFT"><FONT POINT-SIZE="9">{col['type'][:20]}</FONT></TD>
                            <TD ALIGN="CENTER"><FONT POINT-SIZE="9">{'✓' if col['nullable'] == 'YES' else '✗'}</FONT></TD>
                        </TR>'''

                    if len(table_info['columns']) > max_cols:
                        label += f'''<TR><TD COLSPAN="3" ALIGN="CENTER" BGCOLOR="#F0F0F0">
                            <FONT POINT-SIZE="9"><I>... +{len(table_info['columns']) - max_cols} columns más</I></FONT>
                        </TD></TR>'''

                    label += '</TABLE>>'

                    sub.node(table_name, label=label)

        # Agregar relaciones
        for rel in self.relationships:
            if rel['type'] == 'FK':
                # Foreign Key explícita
                dot.edge(rel['from'], rel['to'],
                        label=f" {rel['column']} ",
                        style='solid',
                        color='darkblue',
                        fontsize='9',
                        fontcolor='darkblue',
                        arrowhead='normal')
            else:
                # Relación inferida
                dot.edge(rel['from'], rel['to'],
                        label=f" {rel['column']} ",
                        style='dashed',
                        color='gray',
                        fontsize='8',
                        fontcolor='gray',
                        arrowhead='empty')

        # Renderizar
        try:
            # Generate el diagrama
            dot.render(output_file, format=output_format, cleanup=True, view=False)
            print(f"\n✅ Diagrama generado exitosamente: {output_file}.{output_format}")

            # También generate versión DOT for edición posterior
            with open(f"{output_file}.dot", 'w', encoding='utf-8') as f:
                f.write(dot.source)
            print(f"✅ Archivo DOT también generado: {output_file}.dot")

            # Generate versión SVG for web
            dot.render(output_file, format='svg', cleanup=True, view=False)
            print(f"✅ Versión SVG generada: {output_file}.svg")

        except Exception as e:
            print(f"⚠️ Error generando el diagrama: {str(e)}")
            print("\nIntentando guardar solo el file DOT...")
            with open(f"{output_file}.dot", 'w', encoding='utf-8') as f:
                f.write(dot.source)
            print(f"✅ Archivo DOT guardado: {output_file}.dot")

    def generate_summary_report(self, output_file='erd_summary.md'):
        """Genera un reporte resumido en Markdown"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 📊 Snowflake ERD Report - Schema SECURITY_ANALYTICS\n\n")
            f.write("## 📋 Resumen Ejecutivo\n\n")

            total_tables = len([t for t in self.tables_info.values() if t['type'] == 'BASE TABLE'])
            total_views = len([t for t in self.tables_info.values() if t['type'] == 'VIEW'])
            total_columns = sum(len(t['columns']) for t in self.tables_info.values())

            f.write(f"- **Total de Objetos:** {len(self.tables_info)}\n")
            f.write(f"- **Tablas:** {total_tables}\n")
            f.write(f"- **Views:** {total_views}\n")
            f.write(f"- **Total de Columnas:** {total_columns}\n")
            f.write(f"- **Relaciones Identifieachs:** {len(self.relationships)}\n\n")

            # Resumen por base de data
            f.write("## 🗂️ Distribución por Capa\n\n")

            for db in ['DEV_LANDING', 'DEV_TRANSFORMATION', 'DEV_REPORTING']:
                tables_in_db = [t for t in self.tables_info.values() if t['database'].upper() == db]

                emoji = {'DEV_LANDING': '📥', 'DEV_TRANSFORMATION': '⚙️', 'DEV_REPORTING': '📊'}.get(db, '📁')

                f.write(f"### {emoji} {db}\n\n")
                f.write(f"**Estadísticas:**\n")
                f.write(f"- Total de objetos: {len(tables_in_db)}\n")
                f.write(f"- Tablas: {len([t for t in tables_in_db if t['type'] == 'BASE TABLE'])}\n")
                f.write(f"- Views: {len([t for t in tables_in_db if t['type'] == 'VIEW'])}\n\n")

                if tables_in_db:
                    f.write("**Objetos en esta capa:**\n\n")
                    f.write("| Nombre | Tipo | Columnas | Descripción |\n")
                    f.write("|--------|------|----------|-------------|\n")

                    for table in sorted(tables_in_db, key=lambda x: x['name']):
                        comment = table['comment'][:50] + '...' if table['comment'] and len(table['comment']) > 50 else table['comment'] or '-'
                        f.write(f"| {table['name']} | {table['type']} | {len(table['columns'])} | {comment} |\n")
                    f.write("\n")

            # Detalle de relaciones
            f.write("## 🔗 Relaciones Identifieachs\n\n")

            if self.relationships:
                f.write("### Foreign Keys Explícitas\n\n")
                fks = [r for r in self.relationships if r['type'] == 'FK']
                if fks:
                    f.write("| Tabla Origen | Columna | Tabla Destino |\n")
                    f.write("|--------------|---------|---------------|\n")
                    for rel in fks:
                        from_table = self.tables_info[rel['from']]['name']
                        to_table = self.tables_info[rel['to']]['name']
                        f.write(f"| {from_table} | {rel['column']} | {to_table} |\n")
                    f.write("\n")
                else:
                    f.write("*No se encontraron foreign keys explícitas en el esquema.*\n\n")

                f.write("### Relaciones Inferidas\n\n")
                inferred = [r for r in self.relationships if r['type'] == 'INFERRED']
                if inferred:
                    f.write("| Tabla Origen | Columna | Tabla Destino | Confianza |\n")
                    f.write("|--------------|---------|---------------|----------|\n")
                    for rel in inferred:
                        from_table = self.tables_info[rel['from']]['name']
                        to_table = self.tables_info[rel['to']]['name']
                        # Calcular confianza basada en similitud de nombres
                        confidence = "Alta" if rel['column'].upper().replace('_ID', '').replace('_KEY', '') in to_table.upper() else "Media"
                        f.write(f"| {from_table} | {rel['column']} | {to_table} | {confidence} |\n")
                    f.write("\n")
                else:
                    f.write("*No se pudieron inferir relaciones adicionales.*\n\n")
            else:
                f.write("*No se identificaron relaciones en el esquema.*\n\n")

            # Recomendaciones
            f.write("## 💡 Recomendaciones\n\n")
            f.write("1. **Documentación:** Considerar agregar comentarios a las tables y columns for mejor comprensión.\n")
            f.write("2. **Constraints:** Definir foreign keys explícitas en Snowflake for mantener integridad referencial.\n")
            f.write("3. **Naming Convention:** Mantener convenciones de nombres consistentes for facilitar el mantenimiento.\n")
            f.write("4. **Optimización:** Revisar índices y clustering keys basados en los patrones de join identificados.\n\n")

            f.write("---\n")
            f.write("*Reporte generado automáticamente por Snowflake ERD Generator*\n")

        print(f"✅ Reporte generado: {output_file}")


def main():
    """Function main"""
    print("="*60)
    print(" SNOWFLAKE ERD GENERATOR - SCHEMA SECURITY_ANALYTICS")
    print("="*60)
    print("\nEste script generateá un diagrama ERD de tu esquema SECURITY_ANALYTICS")
    print("en las bases de data DEV_LANDING, DEV_TRANSFORMATION y DEV_REPORTING")

    generator = SnowflakeERDGenerator()

    # Obtener credenciales
    credentials = generator.get_credentials()

    # Bases de data a explorar
    databases = ['DEV_LANDING', 'DEV_TRANSFORMATION', 'DEV_REPORTING']

    print("\n" + "="*60)
    print("INICIANDO EXPLORACIÓN DE ESQUEMAS")
    print("="*60)

    successful_connections = 0
    for db in databases:
        if generator.connect_and_explore(credentials, db, 'SECURITY_ANALYTICS'):
            successful_connections += 1
        else:
            print(f"⚠️ No se pudo conectar a {db}, continuando con las demás...")

    if successful_connections == 0:
        print("\n❌ No se pudo conectar a ninguna base de data.")
        print("Verifica tus credenciales y permisos.")
        return

    print(f"\n✅ Conectado exitosamente a {successful_connections}/{len(databases)} bases de data")

    # Inferir relaciones adicionales
    generator.infer_relationships()

    # Generate el ERD
    generator.generate_erd(output_format='png', output_file='snowflake_itseckpi_erd')

    # Generate reporte
    generator.generate_summary_report('snowflake_itseckpi_summary.md')

    print("\n" + "="*60)
    print(" PROCESO COMPLETADO EXITOSAMENTE")
    print("="*60)
    print("\n📁 Archivos generados:")
    print("  ├── 📊 snowflake_itseckpi_erd.png (Diagrama ERD)")
    print("  ├── 📊 snowflake_itseckpi_erd.svg (Versión web)")
    print("  ├── 📝 snowflake_itseckpi_erd.dot (Archivo fuente editable)")
    print("  └── 📄 snowflake_itseckpi_summary.md (Reporte detallado)")
    print("\n💡 Tip: Puedes editar el file .dot con cualquier editor de texto")
    print("    y regenerate el diagrama con: dot -Tpng file.dot -o file.png")


if __name__ == "__main__":
    main()