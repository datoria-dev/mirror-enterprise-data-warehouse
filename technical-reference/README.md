# Technical Reference Documentation

**Folder Name**: `technical-reference/` - Standard naming for engineering data projects
**Purpose**: Official external documentation for all platforms, services, APIs, libraries, and tools
**Audience**: Development team, data engineers, stakeholders
**Status**: ✅ TO BE UPLOADED to Azure DevOps as folder AND Wiki pages

---

## 📁 Directory Structure

```
technical-reference/
├── README.md                    # This index
├── Snowflake/                   # Snowflake platform docs
│   └── STREAMLIT_LIMITATIONS.md # ⚡ Critical limitations
├── Python/                      # Python language docs
│   └── RANDOM_MODULE.md         # ✅ Complete reference
├── Streamlit/                   # Streamlit framework docs
├── Power_BI/                    # Power BI platform docs
├── APIs/                        # API documentation (18 services)
│   ├── ServiceNow/
│   ├── Symantec/
│   ├── Trellix/
│   └── ... (15 more services)
├── Libraries/                   # Python libraries docs
└── Security_Tools/              # Security tools docs
```

---

## ✅ Current Documentation Status

| Platform | Document | Status | Date |
|----------|----------|--------|------|
| **Snowflake** | STREAMLIT_LIMITATIONS.md | ✅ Complete | 2025-10-25 |
| **Python** | RANDOM_MODULE.md | ✅ Complete | 2025-10-25 |

---

## 🚀 Quick Start

**For Developers - Check Limitations First**:
```bash
# Before using any platform/service:
cat technical-reference/[Platform]/03_LIMITATIONS.md
```

**For New Team Members - Start Here**:
1. Read this README
2. Review Snowflake/STREAMLIT_LIMITATIONS.md
3. Review Python/RANDOM_MODULE.md

---

## 📚 Official Source Links

**Core Platforms**:
- **Snowflake**: https://docs.snowflake.com/
- **Python**: https://docs.python.org/3/
- **Streamlit**: https://docs.streamlit.io/
- **Power BI**: https://docs.microsoft.com/en-us/power-bi/

**Security Tools**: (APIs to be documented)

---

## 🎯 Why This Exists

1. **Centralized Knowledge** - Single source for external docs
2. **Version Control** - Track which versions we use
3. **Offline Access** - Critical docs available locally
4. **Knowledge Preservation** - Docs at time of implementation
5. **Team Resource** - Share knowledge across team

---

## 📋 To Do (Priority)

**High Priority**:
- [ ] Snowflake SQL Reference
- [ ] Streamlit API Reference
- [ ] ServiceNow API & Native Connector
- [ ] pandas DataFrame Operations

**Medium Priority**:
- [ ] Power BI DAX Reference
- [ ] plotly Charts Reference
- [ ] Python requests Library

**Low Priority**:
- [ ] 18 Security Tool APIs (one by one)

---

## 🔄 Maintenance

**Monthly**: Check for doc updates, verify versions
**Quarterly**: Full documentation audit
**When Issues Found**: Document immediately in 03_LIMITATIONS.md

---

## 📞 Contact

**Owner**: Fuad Onate (fuad.onate@CompanyX.com)
**Last Updated**: 2025-10-25
**Next Review**: 2025-11-25

---

See full details in individual platform folders.
