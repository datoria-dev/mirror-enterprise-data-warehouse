#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de ejecución for Snowflake ERD Complete Extractor
Permite executer con credenciales interactivas o from .env
"""

import sys
import os
from pathlib import Path
from getpass import getpass

# Agregar el directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

from snowflake_erd_complete_extractor import SnowflakeERDExtractor

def get_connection_forms():
    """Obtiene los parámetros de connection de forma interactiva o from .env"""

    print("=" * 60)
    print("🚀 Snowflake ERD Complete Extractor - Configuración")
    print("=" * 60)

    env_file = Path(".env")

    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv()

        # Verificar si las variables están configuradas
        account = os.getenv('SNOWFLAKE_ACCOUNT')
        user = os.getenv('SNOWFLAKE_USER')
        password = os.getenv('SNOWFLAKE_PASSWORD')

        if account and account != 'tu_cuenta_aqui' and user and user != 'tu_usuario_aqui':
            print("\n✅ Archivo .env detectado con credenciales")
            use_env = input("¿Deseas usar las credenciales del file .env? (S/n): ").strip().lower()

            if use_env != 'n':
                return {
                    'account': account,
                    'user': user,
                    'password': password,
                    'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
                    'database': os.getenv('SNOWFLAKE_DATABASE', 'DEV_ITSECKPI'),
                    'schema': os.getenv('SNOWFLAKE_SCHEMA', 'SECURITY_ANALYTICS')
                }

    # Solicitar credenciales interactivamente
    print("\n📝 Por favor ingresa tus credenciales de Snowflake:")
    print("(Nota: Si ya estás conectado from VS Code, usa las mismas credenciales)\n")

    connection_forms = {
        'account': input("🔹 Snowflake Account (ej: abc12345.us-east-1): ").strip(),
        'user': input("🔹 Username: ").strip(),
        'password': getpass("🔹 Password: "),
        'warehouse': input("🔹 Warehouse [ENTER for COMPUTE_WH]: ").strip() or 'COMPUTE_WH',
        'database': input("🔹 Database [ENTER for DEV_ITSECKPI]: ").strip() or 'DEV_ITSECKPI',
        'schema': input("🔹 Schema [ENTER for SECURITY_ANALYTICS]: ").strip() or 'SECURITY_ANALYTICS'
    }

    # Opción de guardar credenciales
    save = input("\n¿Deseas guardar estas credenciales en .env for futuro uso? (s/N): ").strip().lower()
    if save == 's':
        save_credentials_to_env(connection_forms)

    return connection_forms

def save_credentials_to_env(forms):
    """Guarda las credenciales en file .env"""
    try:
        env_content = f"""# Configuración de Snowflake - Generado automáticamente
SNOWFLAKE_ACCOUNT={forms['account']}
SNOWFLAKE_USER={forms['user']}
SNOWFLAKE_PASSWORD={forms['password']}
SNOWFLAKE_WAREHOUSE={forms['warehouse']}
SNOWFLAKE_DATABASE={forms['database']}
SNOWFLAKE_SCHEMA={forms['schema']}
"""
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Credenciales guardadas en .env")
    except Exception as e:
        print(f"⚠️ No se pudieron guardar las credenciales: {e}")

def display_menu():
    """Muestra menú de opciones de ejecución"""
    print("\n" + "=" * 60)
    print("📊 Opciones de Extracción")
    print("=" * 60)
    print("\n1. Extracción Completa (Metadata + Diagramas + Documentación)")
    print("2. Solo Extracción de Metadata")
    print("3. Solo Generación de Diagramas (requiere metadata previa)")
    print("4. Solo Documentación (requiere metadata previa)")
    print("5. Análisis de Calidad del Esquema")
    print("0. Salir")

    return input("\n🎯 Selecciona una opción: ").strip()

def main():
    """Function main del ejecutor"""

    print("\n" + "🌟" * 30)
    print(" " * 10 + "SNOWFLAKE ERD COMPLETE EXTRACTOR")
    print("🌟" * 30)

    # Obtener parámetros de connection
    connection_forms = get_connection_forms()

    # Createte extractor
    extractor = SnowflakeERDExtractor(connection_forms)

    while True:
        option = display_menu()

        if option == '0':
            print("\n👋 ¡Hasta luego!")
            break

        try:
            if option == '1':
                # Extracción completa
                print("\n" + "🔄" * 20)
                print("\n🚀 Iniciando extracción completa...")
                print("\n🔌 Conectando a Snowflake...")
                extractor.connect()

                print("📊 Extrayendo metadata...")
                print("  ├─ Tablas...")
                extractor.extract_tables_metadata()
                print("  ├─ Columnas...")
                extractor.extract_columns_metadata()
                print("  ├─ Constraints y relaciones...")
                extractor.extract_constraints_and_relationships()
                print("  ├─ Vistas...")
                extractor.extract_views_metadata()
                print("  ├─ Linaje de data...")
                extractor.analyze_data_lineage()
                print("  └─ Validaciones de calidad...")
                extractor.perform_quality_checks()

                print("\n📝 Generando outputs...")
                print("  ├─ Diagramas ERD...")
                extractor.save_all_diagrams()
                print("  ├─ Documentación Excel...")
                extractor.createte_excel_documentation()
                print("  ├─ Documentación Markdown...")
                extractor.createte_markdown_documentation()
                print("  └─ Metadata JSON...")
                extractor.save_metadata_json()

                print("\n" + "✅" * 20)
                print("\n🎉 ¡Extracción completada exitosamente!")
                print("\n📁 Resultados en: snowflake_erd_output/")
                print("  ├─ 📊 diagrams/     - Diagramas ERD")
                print("  ├─ 📚 documentation/ - Excel, Markdown, JSON")
                print("  ├─ 📝 scripts/      - Mermaid, PlantUML, DBML")
                print("  └─ 📋 logs/         - Logs de ejecución")

            elif option == '2':
                # Solo metadata
                print("\n📊 Extrayendo solo metadata...")
                extractor.connect()
                extractor.extract_all_metadata()
                extractor.save_metadata_json()
                print("✅ Metadata extraída y guardada")

            elif option == '3':
                # Solo diagramas
                print("\n🎨 Generando solo diagramas...")
                if not extractor.metadata['tables']:
                    print("⚠️ Primero debes extract la metadata (opción 2)")
                else:
                    extractor.save_all_diagrams()
                    print("✅ Diagramas generados")

            elif option == '4':
                # Solo documentación
                print("\n📚 Generando solo documentación...")
                if not extractor.metadata['tables']:
                    print("⚠️ Primero debes extract la metadata (opción 2)")
                else:
                    extractor.createte_excel_documentation()
                    extractor.createte_markdown_documentation()
                    print("✅ Documentación generada")

            elif option == '5':
                # Análisis de calidad
                print("\n🔍 Realizando análisis de calidad...")
                if not extractor.metadata['tables']:
                    extractor.connect()
                    extractor.extract_all_metadata()

                extractor.perform_quality_checks()

                issues = extractor.metadata.get('quality_issues', {})
                print("\n📊 Resultados del Análisis de Calidad:")
                print("  ├─ Tablas huérfanas: {}".format(len(issues.get('orphaned_tables', []))))
                print("  ├─ Sin Primary Key: {}".format(len(issues.get('missing_primary_keys', []))))
                print("  └─ Inconsistencias: {}".format(len(issues.get('naming_inconsistencies', []))))

                if issues.get('orphaned_tables'):
                    print("\n⚠️ Tablas huérfanas detectadas:")
                    for table in issues['orphaned_tables'][:5]:
                        print(f"    - {table}")

            else:
                print("\n❌ Opción no válida")

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Revisa los logs for más detalles")

        finally:
            if extractor.conn:
                extractor.close()

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error fatal: {str(e)}")
        sys.exit(1)