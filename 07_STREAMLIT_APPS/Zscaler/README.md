# Zscaler Security Dashboard

## 🔐 Cloud Security Platform

Real-time Zscaler security monitoring dashboard for zero trust network access and cloud security operations.

## 📋 Quick Start

### Prerequisites
- Python 3.9+
- Snowflake access
- Network connectivity

### Installation
```bash
# Clone repository
git clone https://github.com/GenericCorp/zscaler-security-dashboard.git
cd zscaler-security-dashboard

# Create environment
conda env create -f environment.yml
conda activate zscaler_security_dashboard

# Configure credentials
cp .env.example .env
# Edit .env with your credentials

# Run dashboard
streamlit run streamlit_app.py
```

## 🎯 Features

### Core Capabilities
- **Agent Health**: Real-time Zscaler agent health monitoring
- **Threat Intelligence**: Comprehensive threat analysis and detection
- **Endpoint Risk**: Risk assessment and vulnerability tracking
- **Deployment Coverage**: Zero trust coverage metrics
- **Security Alerts**: Alert management and prioritization
- **Threat Trends**: Historical analysis and trending
- **Executive Dashboard**: High-level security posture overview

### Key Metrics
- Total agents and health compliance percentage
- Deployment coverage rates
- Active threat detection and analysis
- Risk level distribution
- Security alert management
- Compliance tracking

## 📊 Data Sources

### Snowflake Views
```sql
DEV_REPORTING.SECURITY_ANALYTICS.VW_ZSCALER_AGENT_HEALTH
DEV_REPORTING.SECURITY_ANALYTICS.VW_ZSCALER_ANALYSIS
DEV_REPORTING.SECURITY_ANALYTICS.VW_ZSCALER_COMPLIANCE_SETTINGS
DEV_REPORTING.SECURITY_ANALYTICS.VW_ZSCALER_DEPLOYMENT_COVERAGE
DEV_REPORTING.SECURITY_ANALYTICS.VW_ZSCALER_ENDPOINT_RISK
DEV_REPORTING.SECURITY_ANALYTICS.VW_ZSCALER_SECURITY_ALERTS
DEV_REPORTING.SECURITY_ANALYTICS.VW_ZSCALER_THREAT_SUMMARY
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

### 1. Agent Health
- Health compliance gauge
- Agent status distribution
- Non-compliant agent tracking

### 2. Threat Analysis
- Threat severity distribution
- Top threat reasons
- Activity timeline
- Affected resources

### 3. Endpoint Risk
- Risk level assessment
- Risk factor analysis
- High-risk endpoint identification
- Risk by device type and OS

### 4. Coverage & Deployment
- Deployment coverage metrics
- Coverage by scope
- Compliance configuration
- Gap analysis

### 5. Security Alerts
- Active alert tracking
- Alert type distribution
- Days inactive analysis
- Alert prioritization

### 6. Threat Trends
- Historical threat analysis
- Trend visualization
- Category analysis
- Device type distribution

### 7. Executive Dashboard
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

## 📝 Troubleshooting

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
- Validate data freshness

**Performance Issues**
- Increase warehouse size
- Optimize query filters
- Check cache settings
- Review data volume limits

**Agent Health Issues**
- Verify agent deployment status
- Check connectivity to Zscaler cloud
- Review policy configurations

## 📞 Support

- **Email**: zscaler-support@GenericCorp.com
- **Teams**: GenericCorp Security Support
- **Wiki**: Internal documentation
- **Zscaler Portal**: admin.zscaler.com

## 🔒 Security Notes

- All data transmissions are encrypted (TLS 1.2+)
- Authentication required for all access
- Zero trust architecture enforced
- Regular security audits performed
- Compliance with corporate security policies
- Data residency requirements met

## 📊 Key Performance Indicators

### Target Metrics
- Agent Health: ≥ 95%
- Deployment Coverage: ≥ 95%
- Alert Response Time: < 4 hours
- Risk Assessment: Updated daily
- Compliance Rate: 100%

### SLA Requirements
- Dashboard Availability: 99.9%
- Data Refresh: Every 5 minutes
- Alert Detection: < 1 minute
- Report Generation: On-demand

## 🔄 Integration

### Supported Integrations
- Snowflake Data Platform
- Zscaler Cloud Security
- SIEM Integration
- ServiceNow Ticketing
- Email Notifications

## 📜 License

© 2025 GenericCorp Corporation. All rights reserved.
Internal use only - Proprietary and confidential.