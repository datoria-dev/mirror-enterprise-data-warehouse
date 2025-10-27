# Repository Folder Structure

This document describes the organization of the Snowflake IT Security KPI Data Warehouse repository.

## Directory Structure

```
snowflake-SECURITY_ANALYTICS-datawarehouse-dev/
│
├── 01_SQL_SCRIPTS/                    # SQL scripts for Snowflake
│   ├── 01_Prerequisites/              # Initial setup and prerequisites
│   ├── 02_Base_Implementation/        # Core table and schema creation
│   ├── 03_Enhancements/               # Feature additions and improvements
│   ├── 04_Pipelines/                  # Data pipeline definitions
│   ├── 05_Fixes/                      # Bug fixes and corrections
│   └── 06_Monitoring/                 # Monitoring and analysis queries
│
├── 02_PYTHON_SCRIPTS/                 # Python automation scripts
│   ├── run_daily_analysis.py          # Daily data model analysis
│   ├── run_multi_database_analysis.py # Multi-database analysis
│   ├── analyze_historical_results.py  # Historical trend analysis
│   └── test_connection.py             # Connection testing utility
│
├── 03_CONFIG/                         # Configuration files
│   ├── .env                           # Environment variables (not in repo)
│   └── .env.example                   # Environment template
│
├── 04_DOCUMENTATION/                  # Project documentation
│   ├── 01_Reports/                    # Analysis reports
│   ├── 02_ERD/                        # Entity Relationship Diagrams
│   │   └── ITSECKPI_ERD_Documentation_*.xlsx
│   ├── 03_Guides/                     # User guides
│   ├── 04_Setup_Guides/               # Setup and configuration guides
│   │   ├── AZURE_DEVOPS_QUICK_START.md
│   │   ├── AZURE_DEVOPS_SETUP_GUIDE.md
│   │   ├── QUICK_START_GITHUB.md
│   │   ├── QUICK_START_MONITORING.md
│   │   ├── MANUAL_UPLOAD_INSTRUCTIONS.md
│   │   └── UPDATE_GITHUB_INSTRUCTIONS.md
│   ├── ARCHITECTURE_DIAGRAMS.md       # Architecture documentation
│   ├── DELIVERABLES_SUMMARY.md        # Project deliverables summary
│   ├── PROJECT_ANALYSIS_AND_SERVICENOW_INTEGRATION_SUMMARY.md
│   └── SERVICENOW_INTEGRATION_ANALYSIS.md
│
├── 05_ANALYSIS_RESULTS/               # Output from daily analysis scripts
│   ├── *.json                         # JSON analysis results
│   ├── *.csv                          # CSV analysis results
│   └── README.md                      # Analysis results documentation
│
├── 06_SOURCE_DATA/                    # Source data files
│   └── (Raw data files for ingestion)
│
├── 07_EXCEL_OUTPUTS/                  # Excel reports and exports
│   └── (Generated Excel reports)
│
├── 08_QUERY_RESULTS/                  # Ad-hoc query results
│   └── (Query output files)
│
├── 09_STREAMLIT_APPS/                 # Streamlit dashboard applications
│   ├── Ancon/                         # Ancon security platform app
│   ├── BitSight/                      # BitSight security ratings app
│   ├── Cisco_AMP/                     # Cisco AMP for Endpoints app
│   ├── Crowdstrike/                   # Crowdstrike Falcon app
│   ├── Intel_Threats/                 # Threat intelligence app
│   ├── Qualys/                        # Qualys vulnerability mgmt app
│   ├── Sophos/                        # Sophos endpoint security app
│   ├── Splunk/                        # Splunk SIEM app
│   ├── Symantec/                      # Symantec endpoint security app
│   ├── Trellix/                       # Trellix security app
│   ├── Zerofox/                       # ZeroFox threat intelligence app
│   ├── Zscaler/                       # Zscaler cloud security app
│   ├── common/                        # Shared utilities
│   └── templates/                     # App templates
│
├── 10_POWERBI_DASHBOARDS/             # Power BI dashboard files
│   ├── 01_Executive_Dashboards/       # Executive-level dashboards
│   ├── 02_Security_Operations/        # SecOps dashboards
│   ├── 03_Compliance/                 # Compliance reporting dashboards
│   ├── 04_Vulnerability_Mgmt/         # Vulnerability management dashboards
│   ├── 05_Endpoint_Security/          # Endpoint security dashboards
│   ├── 06_Identity_Access/            # Identity and access dashboards
│   ├── 07_SIEM_Analytics/             # SIEM analytics dashboards
│   └── 08_Archived/                   # Archived dashboards
│
├── 11_SERVICENOW_INTEGRATION/         # ServiceNow integration components
│   ├── 01_SQL_Scripts/                # ServiceNow-related SQL
│   ├── 02_Documentation/              # Integration documentation
│   ├── 03_Configuration/              # Configuration files
│   └── 04_Testing/                    # Test scripts and data
│
├── 12_GITHUB_ASSETS/                  # GitHub repository assets
│   ├── GITHUB_CONTRIBUTING.md         # Contribution guidelines
│   ├── GITHUB_GITIGNORE.txt           # Gitignore template
│   ├── GITHUB_LICENSE.txt             # License information
│   ├── GITHUB_PUBLICATION_SUMMARY.md  # Publication summary
│   ├── GITHUB_README.md               # GitHub README
│   └── GITHUB_REPOSITORY_SETUP_GUIDE.md
│
├── 99_ARCHIVE/                        # Archived and obsolete files
│   ├── _2025_10_07/                   # Date-stamped archive
│   ├── GITHUB_REPO_OLD/               # Old GitHub repo copy
│   ├── README_OLD.md                  # Previous README version
│   └── (Other archived content)
│
├── FINAL_DELIVERABLES/                # Final project deliverables
│   ├── 01_Reports/                    # Final reports
│   ├── 02_ERD_Diagrams/               # Final ERD diagrams
│   ├── 03_Excel_DataModel/            # Final Excel data models
│   ├── 04_SQL_Scripts/                # Final SQL scripts
│   └── 05_Implementation_Scripts/     # Final implementation scripts
│
├── .gitignore                         # Git ignore rules
├── .env.example                       # Environment variable template
├── README.md                          # Main project README
├── requirements.txt                   # Python dependencies
└── FOLDER_STRUCTURE.md                # This file

```

## Folder Numbering Convention

The repository uses a numeric prefix system for logical organization:

- **01-03**: Core technical assets (SQL, Python, Config)
- **04-08**: Documentation and outputs (Docs, Analysis, Data, Excel, Query results)
- **09-11**: Applications and integrations (Streamlit, Power BI, ServiceNow)
- **12**: GitHub/Repository assets
- **99**: Archive for obsolete content

## Key Files

### Root Level
- **README.md**: Main project documentation and overview
- **requirements.txt**: Python package dependencies
- **FOLDER_STRUCTURE.md**: Repository organization guide (this file)
- **.gitignore**: Git exclusion rules
- **.env.example**: Template for environment configuration

### Configuration
- **03_CONFIG/.env**: Environment variables for Snowflake connection (not in repo)

### Monitoring Scripts
- **02_PYTHON_SCRIPTS/run_daily_analysis.py**: Daily data warehouse analysis
- **02_PYTHON_SCRIPTS/run_multi_database_analysis.py**: Multi-database comparison
- **02_PYTHON_SCRIPTS/analyze_historical_results.py**: Trend analysis with alerts

### SQL Scripts
- **01_SQL_SCRIPTS/06_Monitoring/DAILY_DATA_MODEL_ANALYSIS_BASIC.sql**: Core analysis queries

## Usage Notes

1. **Development**: Work in `01_SQL_SCRIPTS` and `02_PYTHON_SCRIPTS`
2. **Configuration**: Update `.env` file in `03_CONFIG` (never commit)
3. **Documentation**: Add guides to `04_DOCUMENTATION/03_Guides`
4. **Analysis Results**: Auto-generated in `05_ANALYSIS_RESULTS` (excluded from git)
5. **Archive**: Move obsolete files to `99_ARCHIVE` with date stamp

## Maintenance

- Keep folder numbering consistent when adding new directories
- Document any structural changes in this file
- Archive old versions before major restructuring
- Use descriptive names for new subdirectories

## Recent Changes

### 2025-10-22: Major Restructuring
- Fixed duplicate folder numbering (03_, 06_)
- Renumbered folders for logical sequence:
  - `03_DOCUMENTATION` → `04_DOCUMENTATION`
  - `06_ANALYSIS_RESULTS` → `05_ANALYSIS_RESULTS`
  - `04_EXCEL_OUTPUTS` → `07_EXCEL_OUTPUTS`
  - `05_QUERY_RESULTS` → `08_QUERY_RESULTS`
  - `07_STREAMLIT_APPS` → `09_STREAMLIT_APPS`
  - `08_POWERBI_DASHBOARDS` → `10_POWERBI_DASHBOARDS`
  - `09_SERVICENOW_INTEGRATION` → `11_SERVICENOW_INTEGRATION`
- Created `12_GITHUB_ASSETS` for GitHub-related files
- Moved loose documentation files to `04_DOCUMENTATION`
- Created `04_DOCUMENTATION/04_Setup_Guides` for setup documentation
- Archived `README_OLD.md` and old `GITHUB_REPO` folder
- Updated all Python scripts with new folder paths
- Updated `.gitignore` with new structure

---

**Last Updated**: 2025-10-22
**Maintained By**: IT Security KPI Development Team
