# Trellix EDR Dashboard

## 🔰 Endpoint Detection & Response Platform

Real-time Trellix EDR monitoring dashboard for security operations.

## 📋 Quick Start

### Prerequisites
- Python 3.9+
- Snowflake access
- Network connectivity

### Installation
```bash
# Clone repository
git clone https://github.com/GenericCorp/trellix-edr-dashboard.git
cd trellix-edr-dashboard

# Create environment
conda env create -f environment.yml
conda activate trellix_edr_dashboard

# Configure credentials
cp .env.example .env
# Edit .env with your credentials

# Run dashboard
streamlit run streamlit_app.py
```

## 🎯 Features

### Core Capabilities
- **EDR Coverage**: Real-time endpoint protection metrics
- **Agent Health**: Update status and version compliance
- **Communication Status**: Active/stale endpoint monitoring
- **AMCore Compliance**: Version management and outdated detection
- **Security Alerts**: Alert tracking and system monitoring
- **OPCO Analysis**: Operating company performance comparison

### Key Metrics
- Total endpoints and coverage percentage
- Agent update rates
- Communication status (24h/7d)
- AMCore version compliance
- Alert distribution
- OPCO risk assessment

## 📊 Data Sources

### Snowflake Views
```sql
DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_TRELLIX_AGENT_HEALTH
DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_TRELLIX_AMCORE_COMPLIANCE
DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_TRELLIX_COMMUNICATION_STATUS
DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_TRELLIX_EDR_COVERAGE
DEV_REPORTING.SECURITY_ANALYTICS.VW_GOLD_TRELLIX_SECURITY_ALERTS
```

## 🔧 Configuration

### Environment Variables
```bash
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ROLE=your_role
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=DEV_REPORTING
SNOWFLAKE_SCHEMA=SECURITY_ANALYTICS
```

### Dashboard Settings
- Auto-refresh: 5 minutes
- Data cache TTL: 300 seconds
- Default time range: Last 30 days

## 📈 Dashboard Tabs

### 1. EDR Coverage
- Active vs inactive endpoints
- Coverage percentage by OPCO
- Target compliance tracking

### 2. Agent Health
- Update rate monitoring
- Days outdated tracking
- Agent distribution analysis

### 3. Communication Status
- 24h/7d activity monitoring
- Stale endpoint detection
- OS type breakdown

### 4. AMCore Compliance
- Version distribution
- Outdated endpoint tracking
- Compliance percentage

### 5. Security Alerts
- Alert type distribution
- System impact analysis
- Critical alert tracking

### 6. OPCO Analysis
- Performance scorecard
- Risk assessment heatmap
- Comparative metrics

## 🚀 Deployment

### Local Development
```bash
streamlit run streamlit_app.py --server.port 8501
```

### Production
```bash
streamlit run streamlit_app.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  --server.headless true
```

## 🔍 Troubleshooting

### Common Issues

**Connection Error**
```python
# Verify Snowflake connection
from snowflake.snowpark import Session
session = Session.builder.configs(connection_params).create()
```

**Data Not Loading**
- Check Snowflake permissions
- Verify view access
- Review network connectivity

**Performance Issues**
- Increase warehouse size
- Optimize query filters
- Check cache settings

## 📞 Support

- **Email**: trellix-support@GenericCorp.com
- **Teams**: GenericCorp Security Support
- **Wiki**: Internal documentation

## 📜 License

© 2025 GenericCorp Corporation. All rights reserved.
Internal use only - Proprietary and confidential.