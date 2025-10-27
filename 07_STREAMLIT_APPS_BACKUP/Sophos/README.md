# Sophos Security Dashboard

## 🛡️ Endpoint Protection Platform

Real-time Sophos endpoint security monitoring dashboard for enterprise security operations.

## 📋 Quick Start

### Prerequisites
- Python 3.9+
- Snowflake access
- Network connectivity

### Installation
```bash
# Clone repository
git clone https://github.com/GenericCorp/sophos-security-dashboard.git
cd sophos-security-dashboard

# Create environment
conda env create -f environment.yml
conda activate sophos_security_dashboard

# Configure credentials
cp .env.example .env
# Edit .env with your credentials

# Run dashboard
streamlit run streamlit_app.py
```

## 🎯 Features

### Core Capabilities
- **Endpoint Health**: Real-time health compliance monitoring
- **Protection Coverage**: Comprehensive protection rate tracking
- **Security Alerts**: Alert management and severity analysis
- **OS Protection**: Operating system-specific security metrics
- **User Activity**: User behavior and endpoint association tracking
- **Executive Dashboard**: High-level security posture overview

### Key Metrics
- Total endpoints and health compliance percentage
- Protection coverage rates
- Active endpoints (7-day window)
- Security alert distribution
- OS-specific protection rates
- User activity patterns

## 📊 Data Sources

### Snowflake Views
```sql
DEV_REPORTING.SECURITY_ANALYTICS.VW_SOPHOS_ENDPOINT_HEALTH
DEV_REPORTING.SECURITY_ANALYTICS.VW_SOPHOS_EXECUTIVE_SUMMARY
DEV_REPORTING.SECURITY_ANALYTICS.VW_SOPHOS_OS_PROTECTION
DEV_REPORTING.SECURITY_ANALYTICS.VW_SOPHOS_SECURITY_ALERTS
DEV_REPORTING.SECURITY_ANALYTICS.VW_SOPHOS_USER_ACTIVITY
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

### 1. Endpoint Health
- Health compliance gauge
- Protection coverage metrics
- Endpoint status distribution

### 2. OS Protection
- Operating system distribution
- Protection rates by OS
- Health and activity status

### 3. Security Alerts
- Alert type distribution
- Severity analysis
- Impact assessment

### 4. User Activity
- User endpoint associations
- Activity timeline analysis
- Protection status by user

### 5. Trends Analysis
- 30-day protection trends
- Alert severity trends
- Compliance gap analysis

### 6. Executive Dashboard
- Overall security score
- Risk assessment matrix
- Priority action items
- Compliance summary

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

- **Email**: sophos-support@GenericCorp.com
- **Teams**: GenericCorp Security Support
- **Wiki**: Internal documentation

## 🔐 Security Notes

- All data transmissions are encrypted
- Authentication required for all access
- Regular security audits performed
- Compliance with corporate security policies

## 📜 License

© 2025 GenericCorp Corporation. All rights reserved.
Internal use only - Proprietary and confidential.