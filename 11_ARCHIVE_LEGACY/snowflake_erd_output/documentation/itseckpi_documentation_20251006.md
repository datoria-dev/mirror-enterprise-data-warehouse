# Documentación del Esquema SECURITY_ANALYTICS - GenericCorp

Generado: 2025-10-06 10:43:00

## [DATA] Resumen Ejecutivo

- **Account**: GenericCorp-CRH_EDW
- **Role**: DEV_DEVELOPER
- **Warehouse**: DEV_WH
- **Schema**: SECURITY_ANALYTICS

### Estadísticas Generales

- **Total de tablas**: 243
- **Total de vistas**: 238
- **Total de columnas**: 5232
- **Volumen total**: 1.07 GB


## [BUILD] Landing Layer

**Database**: `DEV_LANDING`

**Tablas**: 145

| Tabla | Filas | Tamaño (MB) | Tipo |
|-------|-------|-------------|------|
| AD_COMPUTERS_ALUNGRIFFITHS | 640 | 0.01 | TABLE |
| AD_COMPUTERS_AMAT | 16,939 | 0.47 | TABLE |
| AD_COMPUTERS_ANCON | 842 | 0.02 | TABLE |
| AD_COMPUTERS_APG | 6,656 | 0.21 | TABLE |
| AD_COMPUTERS_ASHGROVE | 1,282 | 0.04 | TABLE |
| AD_COMPUTERS_BELGIUM | 767 | 0.02 | TABLE |
| AD_COMPUTERS_CRHPP_NET | 6 | 0.00 | TABLE |
| AD_COMPUTERS_CRH_CORP | 20 | 0.00 | TABLE |
| AD_COMPUTERS_CRH_NET | 10 | 0.00 | TABLE |
| AD_COMPUTERS_CRH_UNI_COM | 915 | 0.03 | TABLE |

*... y 135 más*

## [BUILD] Transformation Layer

**Database**: `DEV_TRANSFORMATION`

**Tablas**: 183

| Tabla | Filas | Tamaño (MB) | Tipo |
|-------|-------|-------------|------|
| CISCO_AMP_DATA | 4,948 | 0.10 | TABLE |
| CLOSE_CODE_MAPPING | 6 | 0.00 | TABLE |
| CROWDSTRIKE_ENDPOINTS | 3,609 | 0.14 | TABLE |
| CROWDSTRIKE_VERSIONS | 13 | 0.00 | TABLE |
| DATA_QUALITY_RESULTS | 0 | 0.00 | TABLE |
| DIM_ANCON_USERS | 995 | 0.09 | TABLE |
| DIM_AV_OPCO | 108 | 0.00 | TABLE |
| DIM_BITSIGHT_RISK_VECTORS | 7 | 0.00 | TABLE |
| DIM_CYBELANGEL_ALERTS | 196 | 0.02 | TABLE |
| DIM_DATES | 10,000 | 0.10 | TABLE |

*... y 173 más*

## [BUILD] Reporting Layer

**Database**: `DEV_REPORTING`

**Tablas**: 153

| Tabla | Filas | Tamaño (MB) | Tipo |
|-------|-------|-------------|------|
| BOL_CROWDSTRIKE | 1,203 | 0.22 | TABLE |
| FIXEDVULNERABILITIES | 46,349 | 12.65 | TABLE |
| HOSTS | 84,745 | 7.10 | TABLE |
| KB | 131,106 | 40.01 | TABLE |
| PROJECTS_OVERVIEW | 3,840 | 0.13 | TABLE |
| S1_VERSIONS | 103 | 0.01 | TABLE |
| VULNERABILITIES | 980,867 | 26.07 | TABLE |
| VW_ANCON_COMPLIANCE_SETTINGS | 0 | 0.00 | VIEW |
| VW_AV_REGIONAL_TREND | 0 | 0.00 | VIEW |
| VW_BITSIGHT_CRITICAL_FINDINGS | 0 | 0.00 | VIEW |

*... y 143 más*

## [SYNC] Linaje de Datos

### Landing → Transformation

| Origen | Destino | Confianza |
|--------|---------|-----------|
| AD_COMPUTERS_ANCON | DIM_ANCON_USERS | medium |
| AD_COMPUTERS_ANCON | HIST_ANCON_USERS | medium |
| AD_COMPUTERS_ANCON | VW_ANCON_USER_STATUS | medium |
| AD_COMPUTERS_ANCON | VW_ANCON_DATA_QUALITY | medium |
| AD_COMPUTERS_ANCON | VW_ANCON_SECURITY_ALERTS | medium |
| AD_COMPUTERS_ANCON | VW_ANCON_KEY_QUALITY | medium |
| AD_COMPUTERS_ASHGROVE | V_PROTECTION_STATUS | medium |
| AD_COMPUTERS_ASHGROVE | V_DEVICES_WITH_THREATS | medium |
| AD_COMPUTERS_ASHGROVE | V_GROUP_SUMMARY | medium |
| AD_COMPUTERS_CRH_UNI_COM | VW_AV_COMPLIANCE_STATUS | medium |

### Transformation → Reporting

| Origen | Destino | Confianza |
|--------|---------|-----------|
| CISCO_AMP_DATA | VW_CISCO_AMP_COVERAGE | medium |
| CISCO_AMP_DATA | VW_CISCO_AMP_OS_COVERAGE | medium |
| CISCO_AMP_DATA | VW_CISCO_AMP_VERSION_COMPLIANCE | medium |
| CISCO_AMP_DATA | VW_CISCO_AMP_ENDPOINT_HEALTH | medium |
| CISCO_AMP_DATA | VW_GOLD_ZEROFOX_DATA_QUALITY | medium |
| CISCO_AMP_DATA | VW_CISCO_AMP_COMPLIANCE_SETTINGS | medium |
| CISCO_AMP_DATA | VW_GOLD_THREATINTEL_DATA_QUALITY | medium |
| CLOSE_CODE_MAPPING | VW_DEFENDER_OS_SECURITY | medium |
| CLOSE_CODE_MAPPING | VW_FIXEDVULN_OS_TRENDS | medium |
| CLOSE_CODE_MAPPING | VW_SNOW_OS_DISTRIBUTION | medium |

## [WARNING] Issues de Calidad


### Tablas Vacías (62)

- AMP_MM_DD_YYYY
- DEFENDER_THREATS_ARCHIVE
- DEFENDER_THREATS_LANDING
- DIM_HOST
- DIM_LEVIAT_LIST_USERS

### Tablas Huérfanas (134)

- AD_COMPUTERS_ALUNGRIFFITHS
- AD_COMPUTERS_AMAT
- AD_COMPUTERS_ANCON
- AD_COMPUTERS_APG
- AD_COMPUTERS_ASHGROVE