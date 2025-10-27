# Ancon Security Dashboard

## 🔐 Identity & Access Management Monitoring Platform

A comprehensive Streamlit-based security dashboard for monitoring account compliance, password policies, user activity, and security alerts.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Data Sources](#data-sources)
- [Dashboard Components](#dashboard-components)
- [Security](#security)
- [Performance](#performance)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Support](#support)
- [License](#license)

## 📖 Overview

The Ancon Security Dashboard provides real-time visibility into identity and access management metrics across the organization. It integrates with Snowflake data warehouse to deliver actionable insights on:

- Account compliance status
- Password policy adherence
- User activity patterns
- Security alerts and incidents
- Risk assessment scores

## ✨ Features

### Core Functionality
- **Real-time Monitoring**: Live data updates with 5-minute auto-refresh
- **Comprehensive Analytics**: 6 specialized tabs for different security aspects
- **Risk Scoring**: Automated risk assessment algorithm
- **Alert Management**: Security alert tracking and categorization
- **Compliance Tracking**: Monitor policy compliance rates
- **Interactive Visualizations**: Plotly-based charts and graphs

### Key Metrics Tracked
- Total accounts and compliance rate
- Password age and expiration status
- Account lockouts and disabled accounts
- Failed login attempts
- User activity levels
- Security alert volumes

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│         Streamlit Frontend          │
│         (streamlit_app.py)          │
└─────────────────┬───────────────────┘
                  │
        ┌─────────▼─────────┐
        │   Data Processing │
        │     (Pandas)      │
        └─────────┬─────────┘
                  │
        ┌─────────▼─────────┐
        │  Snowflake Views  │
        │   (SECURITY_ANALYTICS)      │
        └─────────┬─────────┘
                  │
    ┌─────────────▼─────────────┐
    │     Source Systems        │
    │  (Ancon, AD, SIEM, etc.)  │
    └───────────────────────────┘
```

## 📋 Prerequisites

### System Requirements
- Python 3.9 or higher
- Modern web browser (Chrome, Firefox, Edge)
- Network and credentials access to Snowflake

### Access Requirements
- Snowflake account with appropriate permissions
- Access to DEV_REPORTING.SECURITY_ANALYTICS schema
- VPN access (if required)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/GenericCorp/ancon-security-dashboard.git
cd ancon-security-dashboard
```

### 2. Create Conda Environment
```bash
conda env create -f environment.yml
conda activate ancon_security_dashboard
```

### 3. Set Environment Variables
Create a `.env` file in the project root:
```bash
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ROLE=your_role
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=DEV_REPORTING
SNOWFLAKE_SCHEMA=SECURITY_ANALYTICS
```

### 4. Initialize Logging Directory
```bash
mkdir -p logs
```

### 5. Verify Installation
```bash
python -c "import streamlit; import snowflake.snowpark; print('Installation successful!')"
```

## ⚙️ Configuration

### Streamlit Configuration
Create `.streamlit/config.toml`:
```toml
[theme]
base = "light"
primaryColor = "#0a3d62"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
font = "sans serif"

[server]
port = 8501
headless = true
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

### Logging Configuration
Logging settings are defined in `logging_config.json`. Adjust log levels and handlers as needed:
- **Console**: INFO level for stdout
- **File**: DEBUG level with rotation
- **Security**: JSON format for security events
- **Performance**: Time-based rotation for metrics

## 🎯 Usage

### Starting the Dashboard

#### Local Development
```bash
streamlit run streamlit_app.py
```

#### Production Deployment
```bash
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

### Accessing the Dashboard
1. Open browser to `http://localhost:8501`
2. Dashboard loads automatically with latest data
3. Use sidebar filters to customize view
4. Navigate tabs for different security aspects

### Navigation Guide

#### Tab 1: Account Compliance
- Overview of account compliance status
- Password age distribution
- Non-compliant accounts table

#### Tab 2: Security Alerts
- Real-time alert monitoring
- Alert type distribution
- Top users by alert count

#### Tab 3: Password Analytics
- Password security metrics
- Policy compliance gauge
- Failed login attempt analysis

#### Tab 4: User Activity
- Activity categorization
- Inactive user identification
- Account status breakdown

#### Tab 5: Risk Assessment
- Risk scoring matrix
- Risk distribution charts
- High-risk account identification

#### Tab 6: Settings & Policies
- Current policy configuration
- Security metrics trends
- Automated recommendations

## 📊 Data Sources

### Primary Views
```sql
DEV_REPORTING.SECURITY_ANALYTICS.VW_ANCON_ACCOUNT_COMPLIANCE
DEV_REPORTING.SECURITY_ANALYTICS.VW_ANCON_SECURITY_ALERTS
DEV_REPORTING.SECURITY_ANALYTICS.VW_ANCON_SECURITY_METRICS
DEV_REPORTING.SECURITY_ANALYTICS.VW_ANCON_COMPLIANCE_SETTINGS
```

### Data Refresh Schedule
- Account compliance: Every 4 hours
- Security alerts: Real-time
- Security metrics: Daily at 2 AM
- Compliance settings: On change

## 🔒 Security

### Authentication
- Snowflake authentication via snowpark
- Session management with timeout
- Encrypted credential storage

### Data Protection
- No sensitive data stored locally
- Cache cleared on session end
- SSL/TLS for all connections

### Audit Logging
- All user actions logged
- Security events tracked
- Performance metrics captured

## ⚡ Performance

### Optimization Tips
1. **Caching**: 5-minute TTL for data queries
2. **Query Optimization**: Use materialized views where possible
3. **Resource Management**: Appropriate Snowflake warehouse sizing
4. **Browser**: Use Chrome/Edge for best performance

### Performance Metrics
- Average page load: < 3 seconds
- Query response time: < 2 seconds
- Dashboard refresh: < 5 seconds

## 🔧 Troubleshooting

### Common Issues

#### Connection Errors
```python
# Check Snowflake connectivity
from snowflake.snowpark import Session
session = Session.builder.configs(connection_parameters).create()
session.sql("SELECT CURRENT_VERSION()").show()
```

#### Data Not Loading
1. Verify Snowflake permissions
2. Check view definitions exist
3. Review logs in `logs/ancon_dashboard.log`

#### Performance Issues
1. Check Snowflake warehouse size
2. Review query execution plans
3. Verify network latency

### Debug Mode
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Code Standards
- Follow PEP 8 style guide
- Add docstrings to all functions
- Include unit tests for new features
- Update documentation

### Testing
```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=ancon_dashboard tests/

# Run linting
flake8 streamlit_app.py
pylint streamlit_app.py
```

## 📞 Support

### Resources
- **Documentation**: [Internal Wiki](https://wiki.GenericCorp.com/ancon-dashboard)
- **Issue Tracking**: [JIRA Project ANCON-DASH](https://jira.GenericCorp.com/browse/ANCON-DASH)
- **Teams Channel**: GenericCorp Security Dashboard Support
- **Email**: security-dashboard@GenericCorp.com

### SLA
- Critical issues: 4 hours
- High priority: 1 business day
- Normal priority: 3 business days
- Low priority: 1 week

## 📜 License

© 2025 GenericCorp Corporation. All rights reserved.

This software is proprietary and confidential. Unauthorized copying, distribution, or use of this software, via any medium, is strictly prohibited.

---

## 📚 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [Snowflake Documentation](https://docs.snowflake.com)
- [Plotly Documentation](https://plotly.com/python/)
- [Security Best Practices](https://wiki.GenericCorp.com/security-guidelines)

---

**Version**: 1.0.0  
**Last Updated**: January 2025  
**Maintained by**: GenericCorp Analytics Team