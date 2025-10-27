"""
Translate ALL Spanish content to English
Comprehensive translation of documentation, comments, and strings
"""

import os
import re
from pathlib import Path

# Translation dictionary for common Spanish terms
TRANSLATIONS = {
    # Documentation headers
    "RESUMEN EJECUTIVO": "EXECUTIVE SUMMARY",
    "Hallazgos Críticos": "Critical Findings",
    "Impacto en el Negocio": "Business Impact",
    "ANÁLISIS POR CAPA": "LAYER-BY-LAYER ANALYSIS",
    "Capa de Ingesta": "Ingestion Layer",
    "Capa de Modelado": "Modeling Layer",
    "Capa de Reportes": "Reporting Layer",
    "Estado": "Status",
    "Problemas Identificados": "Identified Issues",
    "ANÁLISIS DE RELACIONES": "RELATIONSHIP ANALYSIS",
    "Relaciones Faltantes Críticas": "Critical Missing Relationships",
    "RECOMENDACIONES PRIORITARIAS": "PRIORITIZED RECOMMENDATIONS",
    "CRÍTICO - Implementar Inmediatamente": "CRITICAL - Implement Immediately",
    "ALTA PRIORIDAD": "HIGH PRIORITY",
    "MEDIA PRIORIDAD": "MEDIUM PRIORITY",
    "PLAN DE IMPLEMENTACIÓN": "IMPLEMENTATION PLAN",
    "RESULTADOS ESPERADOS": "EXPECTED RESULTS",
    "CHECKLIST DE VALIDACIÓN": "VALIDATION CHECKLIST",
    "RIESGOS SI NO SE ACTÚA": "RISKS OF INACTION",
    "PRÓXIMOS PASOS": "NEXT STEPS",

    # Technical terms
    "Fecha": "Date",
    "Analista": "Analyst",
    "Esquema": "Schema",
    "Bases de Datos": "Databases",
    "Tabla": "Table",
    "Tablas": "Tables",
    "Filas": "Rows",
    "Tamaño": "Size",
    "Origen": "Source",
    "Destino": "Target",
    "Confianza": "Reliability",
    "análisis": "analysis",
    "implementar": "implement",
    "implementación": "implementation",
    "favor": "please",
    "gracias": "thank you",
    "Descripción": "Description",
    "descripción": "description",

    # Common phrases
    "Para consultas": "For inquiries",
    "Equipo de": "Team",
    "Generado automáticamente": "Automatically generated",
    "sin correspondencia": "without correspondence",
    "con datos": "with data",
    "sin documentación": "without documentation",
    "Poblada": "Populated",
    "Vacía": "Empty",
    "Mayor volumen": "Largest volume",

    # Status and priority
    "AUSENCIA TOTAL": "TOTAL ABSENCE",
    "MODELO DIMENSIONAL INCOMPLETO": "INCOMPLETE DIMENSIONAL MODEL",
    "SIN INTEGRIDAD REFERENCIAL": "NO REFERENTIAL INTEGRITY",
    "TABLAS VACÍAS": "EMPTY TABLES",
    "Queries lentas": "Slow queries",
    "Riesgo de duplicados": "Risk of duplicates",
    "Difícil entender": "Difficult to understand",
    "No hay garantías": "No guarantees",

    # Actions
    "Agregar": "Add",
    "Establecer": "Establish",
    "Renombrar": "Rename",
    "Crear": "Create",
    "Documentar": "Document",
    "Validar": "Validate",
    "Backup": "Backup",
    "Optimizar": "Optimize",
    "Monitorear": "Monitor",
    "Revisar": "Review",
    "Priorizar": "Prioritize",
    "Ejecutar": "Execute",

    # Time periods
    "Semana": "Week",
    "semana": "week",
    "esta semana": "this week",
    "en 2 semanas": "in 2 weeks",

    # Results
    "Mejora de": "Improvement of",
    "garantía": "guarantee",
    "auto-documentado": "self-documented",
    "Preparado para": "Prepared for",
    "crecimiento futuro": "future growth",

    # Risks
    "Duplicados": "Duplicates",
    "Inconsistencias": "Inconsistencies",
    "Performance degradada": "Degraded Performance",
    "Costos": "Costs",
    "Mayor uso de": "Higher usage of",
    "queries ineficientes": "inefficient queries",
}

# Files to translate with their paths
FILES_TO_TRANSLATE = [
    # Critical documentation
    "00_DOCUMENTATION/IMPLEMENTATION_REPORTS/MODELO_DATOS_ANALISIS_RECOMENDACIONES.md",
    "00_DOCUMENTATION/GUIDES/snowflake_erd_prompt.md",

    # Supporting documentation
    "04_OUTPUT/erd_diagrams/snowflake_itseckpi_report.md",
    "snowflake_erd_output/documentation/itseckpi_documentation_20251006.md",
    "data_model_analysis/data_model_analysis_20251006_104845.md",

    # Root README
    "README.md",
]

def translate_text(text):
    """
    Translate Spanish text to English using dictionary and patterns
    """
    translated = text

    # Apply dictionary translations
    for spanish, english in TRANSLATIONS.items():
        # Case-sensitive replacement
        translated = translated.replace(spanish, english)
        # Try lowercase
        translated = translated.replace(spanish.lower(), english.lower())

    # Additional pattern-based translations
    patterns = [
        (r'sin\s+(\w+)', r'without \1'),
        (r'con\s+(\w+)', r'with \1'),
        (r'todos?\s+l[ao]s\s+(\w+)', r'all \1'),
        (r'debe[ns]?\s+', 'must '),
        (r'puede[ns]?\s+', 'can '),
    ]

    for pattern, replacement in patterns:
        translated = re.sub(pattern, replacement, translated, flags=re.IGNORECASE)

    return translated

def translate_file(filepath):
    """
    Translate a file from Spanish to English
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Translate content
        translated_content = translate_text(content)

        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(translated_content)

        return True, "Success"

    except Exception as e:
        return False, str(e)

def main():
    base_path = Path("C:/Users/fonat/OneDrive/Documents/GenericCorp/Snowflake_ITSECKPI_Project")

    print("=" * 70)
    print("TRANSLATING ALL SPANISH CONTENT TO ENGLISH")
    print("=" * 70)

    translated_count = 0
    failed_count = 0

    for relative_path in FILES_TO_TRANSLATE:
        filepath = base_path / relative_path

        if not filepath.exists():
            print(f"[SKIP] {relative_path} - File not found")
            continue

        print(f"\n[TRANSLATING] {relative_path}")
        success, message = translate_file(filepath)

        if success:
            translated_count += 1
            print(f"  ✓ Translated successfully")
        else:
            failed_count += 1
            print(f"  ✗ Failed: {message}")

    print("\n" + "=" * 70)
    print("TRANSLATION SUMMARY")
    print("=" * 70)
    print(f"Translated: {translated_count}")
    print(f"Failed: {failed_count}")
    print(f"Total: {len(FILES_TO_TRANSLATE)}")

    # Now delete the original Spanish file
    spanish_original = base_path / "00_DOCUMENTATION/IMPLEMENTATION_REPORTS/MODELO_DATOS_ANALISIS_RECOMENDACIONES.md"
    if spanish_original.exists():
        os.remove(spanish_original)
        print(f"\n[DELETED] Original Spanish file: MODELO_DATOS_ANALISIS_RECOMENDACIONES.md")

if __name__ == "__main__":
    main()
