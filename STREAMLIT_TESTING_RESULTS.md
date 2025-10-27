# Streamlit Apps Testing Results

**Date**: 2025-10-27
**Tester**: Fuad Onate
**Environment**: DEV_REPORTING.SECURITY_ANALYTICS
**Total Apps**: 18

---

## Testing Status Overview

| Priority | Apps | Tested | Issues | Status |
|----------|------|--------|--------|--------|
| **High Priority** | 4 | 0 | 0 | ⏳ Pending |
| **Medium Priority** | 4 | 0 | 0 | ⏳ Pending |
| **Lower Priority** | 10 | 0 | 0 | ⏳ Pending |
| **TOTAL** | 18 | 0 | 0 | ⏳ Testing in Progress |

---

## How to Access Apps

### Via Snowflake UI:
1. Go to: https://app.snowflake.com
2. Authenticate with Okta SSO (fuad.onate@CompanyX.com)
3. Navigate to: **Data** → **Databases** → **DEV_REPORTING** → **SECURITY_ANALYTICS** → **Streamlit**
4. Click on app name to launch

### Direct URLs (from Snowflake):
Apps have unique URL IDs. Format: `https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/[URL_ID]`

---

## Priority 1: High-Priority Apps (Test First)

### 1. STREAMLIT_SYMANTEC
**App**: Symantec Endpoint Security Dashboard
**URL ID**: j26cqmbpm3w42zj5njj3
**Deployed**: 2025-10-25 22:27:53

#### Basic Functionality
- [ ] App loads without errors
- [ ] All tabs render correctly
- [ ] Data displays in tables
- [ ] Charts render properly

#### Filters
- [ ] Date range filter works
- [ ] Severity filters work
- [ ] Category filters work
- [ ] Filters update results correctly

#### Features
- [ ] Download CSV buttons work (has 3 buttons)
- [ ] Refresh button works
- [ ] Alert thresholds display (has 2 alerts)
- [ ] No `np.random` errors

#### Data Quality
- [ ] Data is current (not stale)
- [ ] Data matches source tables
- [ ] No null/missing data issues
- [ ] KPIs calculate correctly

#### Performance
- [ ] Loads in <5 seconds
- [ ] Filters respond quickly (<2 sec)
- [ ] No lag or freezing
- [ ] Charts render smoothly

#### Design & UX
- [ ] Visual appeal: ⭐⭐⭐⭐⭐
- [ ] Usability: ⭐⭐⭐⭐⭐
- [ ] Professional appearance: ⭐⭐⭐⭐⭐
- [ ] Clear navigation

**Issues Found**:
- [Document any issues here]

**Improvement Ideas**:
- [Document potential improvements]

**Overall Rating**: __/10

---

### 2. STREAMLIT_CROWDSTRIKE
**App**: CrowdStrike Falcon Dashboard
**URL ID**: pezbdllntnq4ae4pdy3s
**Deployed**: 2025-10-25 22:27:51

#### Basic Functionality
- [ ] App loads without errors
- [ ] All tabs render correctly
- [ ] Data displays in tables
- [ ] Charts render properly

#### Filters
- [ ] Date range filter works
- [ ] Severity filters work
- [ ] Detection type filters work
- [ ] Filters update results correctly

#### Features
- [ ] Download CSV buttons work (has 7 buttons)
- [ ] Refresh button works
- [ ] Alert thresholds display (has 4 alerts)
- [ ] No `np.random` errors

#### Data Quality
- [ ] Data is current (not stale)
- [ ] Data matches source tables
- [ ] No null/missing data issues
- [ ] KPIs calculate correctly

#### Performance
- [ ] Loads in <5 seconds
- [ ] Filters respond quickly (<2 sec)
- [ ] No lag or freezing
- [ ] Charts render smoothly

#### Design & UX
- [ ] Visual appeal: ⭐⭐⭐⭐⭐
- [ ] Usability: ⭐⭐⭐⭐⭐
- [ ] Professional appearance: ⭐⭐⭐⭐⭐
- [ ] Clear navigation

**Issues Found**:
- [Document any issues here]

**Improvement Ideas**:
- [Document potential improvements]

**Overall Rating**: __/10

---

### 3. STREAMLIT_SENTINELONE
**App**: SentinelOne Security Platform
**URL ID**: ab6eno3icam5zbwlhhx4
**Deployed**: 2025-10-25 22:28:00

#### Basic Functionality
- [ ] App loads without errors
- [ ] All tabs render correctly (including Metadata tab)
- [ ] Data displays in tables
- [ ] Charts render properly

#### Filters
- [ ] Date range filter works
- [ ] Threat level filters work
- [ ] Agent status filters work
- [ ] Filters update results correctly

#### Features
- [ ] Download CSV buttons work (if present)
- [ ] Refresh button works
- [ ] Metadata tab loads (has 76 columns)
- [ ] Metadata search works
- [ ] No `np.random` errors

#### Data Quality
- [ ] Data is current (not stale)
- [ ] Data matches source tables
- [ ] No null/missing data issues
- [ ] KPIs calculate correctly

#### Performance
- [ ] Loads in <5 seconds
- [ ] Filters respond quickly (<2 sec)
- [ ] No lag or freezing
- [ ] Charts render smoothly

#### Design & UX
- [ ] Visual appeal: ⭐⭐⭐⭐⭐
- [ ] Usability: ⭐⭐⭐⭐⭐
- [ ] Professional appearance: ⭐⭐⭐⭐⭐
- [ ] Clear navigation

**Issues Found**:
- [Document any issues here]

**Improvement Ideas**:
- [Document potential improvements]

**Overall Rating**: __/10

---

### 4. STREAMLIT_QUALYS
**App**: Qualys Vulnerability Management
**URL ID**: bv6rqf25654g2zjlkx2w
**Deployed**: 2025-10-25 22:27:58

#### Basic Functionality
- [ ] App loads without errors
- [ ] All tabs render correctly
- [ ] Data displays in tables
- [ ] Charts render properly

#### Filters
- [ ] Date range filter works
- [ ] Severity filters work (Critical/High/Medium/Low)
- [ ] Asset filters work
- [ ] Filters update results correctly

#### Features
- [ ] Download CSV buttons work (if present)
- [ ] Refresh button works
- [ ] Vulnerability aging analysis works
- [ ] No `np.random` errors

#### Data Quality
- [ ] Data is current (not stale)
- [ ] Data matches source tables
- [ ] No null/missing data issues
- [ ] KPIs calculate correctly

#### Performance
- [ ] Loads in <5 seconds
- [ ] Filters respond quickly (<2 sec)
- [ ] No lag or freezing
- [ ] Charts render smoothly

#### Design & UX
- [ ] Visual appeal: ⭐⭐⭐⭐⭐
- [ ] Usability: ⭐⭐⭐⭐⭐
- [ ] Professional appearance: ⭐⭐⭐⭐⭐
- [ ] Clear navigation

**Issues Found**:
- [Document any issues here]

**Improvement Ideas**:
- [Document potential improvements]

**Overall Rating**: __/10

---

## Priority 2: Medium-Priority Apps

### 5. STREAMLIT_SOPHOS
**App**: Sophos Security Dashboard
**URL ID**: ivusmm45shxz5u6l6jao
**Deployed**: 2025-10-25 23:23:14 (Recently fixed and redeployed)

#### Basic Functionality
- [ ] App loads without errors
- [ ] All tabs render correctly
- [ ] Data displays in tables
- [ ] Charts render properly

#### Filters
- [ ] Date range filter works
- [ ] Severity filters work
- [ ] Endpoint filters work
- [ ] Filters update results correctly

#### Features
- [ ] Download CSV buttons work (recently fixed)
- [ ] Refresh button works (recently fixed - no `np.random` errors)
- [ ] All 6 `np.random` fixes verified
- [ ] Download button keys working

#### Data Quality
- [ ] Data is current (not stale)
- [ ] Data matches source tables
- [ ] No null/missing data issues
- [ ] KPIs calculate correctly

#### Performance
- [ ] Loads in <5 seconds
- [ ] Filters respond quickly (<2 sec)
- [ ] No lag or freezing
- [ ] Charts render smoothly

#### Design & UX
- [ ] Visual appeal: ⭐⭐⭐⭐⭐
- [ ] Usability: ⭐⭐⭐⭐⭐
- [ ] Professional appearance: ⭐⭐⭐⭐⭐
- [ ] Clear navigation

**Issues Found**:
- [Document any issues here]

**Improvement Ideas**:
- [Document potential improvements]

**Overall Rating**: __/10

---

### 6. STREAMLIT_SPLUNK
**App**: Splunk Security Analytics
**URL ID**: 3f5pbwn2vpzizdtqjiuj
**Deployed**: 2025-10-25 22:28:04

#### Basic Functionality
- [ ] App loads without errors
- [ ] All tabs render correctly
- [ ] Data displays in tables
- [ ] Charts render properly

#### Filters
- [ ] Date range filter works
- [ ] Event type filters work
- [ ] Source filters work
- [ ] Filters update results correctly

#### Features
- [ ] Download CSV buttons work (if present)
- [ ] Refresh button works
- [ ] No `np.random` errors

#### Data Quality
- [ ] Data is current (not stale)
- [ ] Data matches source tables
- [ ] No null/missing data issues
- [ ] KPIs calculate correctly

#### Performance
- [ ] Loads in <5 seconds
- [ ] Filters respond quickly (<2 sec)
- [ ] No lag or freezing
- [ ] Charts render smoothly

#### Design & UX
- [ ] Visual appeal: ⭐⭐⭐⭐⭐
- [ ] Usability: ⭐⭐⭐⭐⭐
- [ ] Professional appearance: ⭐⭐⭐⭐⭐
- [ ] Clear navigation

**Issues Found**:
- [Document any issues here]

**Improvement Ideas**:
- [Document potential improvements]

**Overall Rating**: __/10

---

### 7. STREAMLIT_CYBELANGEL
**App**: CybelAngel Digital Risk Protection
**URL ID**: wakynkevgf73ymcmy7lz
**Deployed**: 2025-10-25 22:28:09

#### Basic Functionality
- [ ] App loads without errors
- [ ] All tabs render correctly (including Metadata tab)
- [ ] Data displays in tables
- [ ] Charts render properly

#### Filters
- [ ] Date range filter works
- [ ] Risk level filters work
- [ ] Category filters work
- [ ] Filters update results correctly

#### Features
- [ ] Download CSV buttons work (if present)
- [ ] Refresh button works
- [ ] Metadata tab loads (has 112 columns)
- [ ] Metadata search works
- [ ] No `np.random` errors

#### Data Quality
- [ ] Data is current (not stale)
- [ ] Data matches source tables
- [ ] No null/missing data issues
- [ ] KPIs calculate correctly

#### Performance
- [ ] Loads in <5 seconds
- [ ] Filters respond quickly (<2 sec)
- [ ] No lag or freezing
- [ ] Charts render smoothly

#### Design & UX
- [ ] Visual appeal: ⭐⭐⭐⭐⭐
- [ ] Usability: ⭐⭐⭐⭐⭐
- [ ] Professional appearance: ⭐⭐⭐⭐⭐
- [ ] Clear navigation

**Issues Found**:
- [Document any issues here]

**Improvement Ideas**:
- [Document potential improvements]

**Overall Rating**: __/10

---

### 8. STREAMLIT_ZEROFOX
**App**: ZeroFox Digital Risk Protection
**URL ID**: gxlmxtd2qphzainafl7k
**Deployed**: 2025-10-25 22:28:13

#### Basic Functionality
- [ ] App loads without errors
- [ ] All tabs render correctly
- [ ] Data displays in tables
- [ ] Charts render properly

#### Filters
- [ ] Date range filter works
- [ ] Threat type filters work
- [ ] Severity filters work
- [ ] Filters update results correctly

#### Features
- [ ] Download CSV buttons work (if present)
- [ ] Refresh button works
- [ ] No `np.random` errors

#### Data Quality
- [ ] Data is current (not stale)
- [ ] Data matches source tables
- [ ] No null/missing data issues
- [ ] KPIs calculate correctly

#### Performance
- [ ] Loads in <5 seconds
- [ ] Filters respond quickly (<2 sec)
- [ ] No lag or freezing
- [ ] Charts render smoothly

#### Design & UX
- [ ] Visual appeal: ⭐⭐⭐⭐⭐
- [ ] Usability: ⭐⭐⭐⭐⭐
- [ ] Professional appearance: ⭐⭐⭐⭐⭐
- [ ] Clear navigation

**Issues Found**:
- [Document any issues here]

**Improvement Ideas**:
- [Document potential improvements]

**Overall Rating**: __/10

---

## Priority 3: Lower-Priority Apps

### 9. STREAMLIT_ZSCALER
**App**: Zscaler Cloud Security
**URL ID**: xnnfrjrms5hh74tu26t5
**Deployed**: 2025-10-25 22:28:15

#### Testing Checklist
- [ ] Basic functionality (load, tabs, data, charts)
- [ ] Filters work correctly
- [ ] Download buttons work (if present)
- [ ] Refresh button works
- [ ] No errors
- [ ] Good performance (<5 sec load)
- [ ] Professional design

**Issues**: [None documented yet]
**Rating**: __/10

---

### 10. STREAMLIT_CISCO_AMP
**App**: Cisco Advanced Malware Protection
**URL ID**: neazn6tegg3whessq2qp
**Deployed**: 2025-10-25 22:28:06

#### Testing Checklist
- [ ] Basic functionality (load, tabs, data, charts)
- [ ] Filters work correctly
- [ ] Download buttons work (if present)
- [ ] Refresh button works
- [ ] No errors
- [ ] Good performance (<5 sec load)
- [ ] Professional design

**Issues**: [None documented yet]
**Rating**: __/10

---

### 11. STREAMLIT_PROOFPOINT
**App**: Proofpoint Email Security
**URL ID**: 7gjf7suceieycvpd5huy
**Deployed**: 2025-10-25 22:28:11

#### Testing Checklist
- [ ] Basic functionality (load, tabs, data, charts)
- [ ] Filters work correctly
- [ ] Download buttons work (if present)
- [ ] Refresh button works
- [ ] Metadata tab works (has 23 columns)
- [ ] No errors
- [ ] Good performance (<5 sec load)
- [ ] Professional design

**Issues**: [None documented yet]
**Rating**: __/10

---

### 12. STREAMLIT_INTEL_THREATS
**App**: Threat Intelligence Dashboard
**URL ID**: 75jkkznw75ogsfrgzjhk
**Deployed**: 2025-10-25 22:28:22

#### Testing Checklist
- [ ] Basic functionality (load, tabs, data, charts)
- [ ] Filters work correctly
- [ ] Download buttons work (if present)
- [ ] Refresh button works
- [ ] No errors
- [ ] Good performance (<5 sec load)
- [ ] Professional design

**Issues**: [None documented yet]
**Rating**: __/10

---

### 13. STREAMLIT_BITSIGHT
**App**: BitSight Security Ratings
**URL ID**: ebeyj2mwi2vvcvvzxqt4
**Deployed**: 2025-10-25 22:28:19

#### Testing Checklist
- [ ] Basic functionality (load, tabs, data, charts)
- [ ] Filters work correctly
- [ ] Download buttons work (if present)
- [ ] Refresh button works
- [ ] No errors
- [ ] Good performance (<5 sec load)
- [ ] Professional design

**Issues**: [None documented yet]
**Rating**: __/10

---

### 14. STREAMLIT_LEVIAT
**App**: Leviat Security Analytics
**URL ID**: ft6lmkagcxv2lszahsda
**Deployed**: 2025-10-25 22:28:24

#### Testing Checklist
- [ ] Basic functionality (load, tabs, data, charts)
- [ ] Filters work correctly
- [ ] Download buttons work (has 7 buttons)
- [ ] Refresh button works
- [ ] Alert thresholds display (has 4 alerts)
- [ ] Metadata tab works (has 146 columns)
- [ ] No errors
- [ ] Good performance (<5 sec load)
- [ ] Professional design

**Issues**: [None documented yet]
**Rating**: __/10

---

### 15. STREAMLIT_SERVICENOW
**App**: ServiceNow Security Operations
**URL ID**: kscpsgajtow5g5rzzsnp
**Deployed**: 2025-10-25 22:28:26

#### Testing Checklist
- [ ] Basic functionality (load, tabs, data, charts)
- [ ] Filters work correctly
- [ ] Download buttons work (has 4 buttons)
- [ ] Refresh button works
- [ ] Alert thresholds display (has 4 alerts)
- [ ] Metadata tab works (has 36 columns)
- [ ] No errors
- [ ] Good performance (<5 sec load)
- [ ] Professional design

**Issues**: [None documented yet]
**Rating**: __/10

---

### 16. STREAMLIT_ANCON
**App**: Ancon Security Monitoring
**URL ID**: zbapkxmoz3zx5vvd3cbj
**Deployed**: 2025-10-25 22:28:17

#### Testing Checklist
- [ ] Basic functionality (load, tabs, data, charts)
- [ ] Filters work correctly
- [ ] Download buttons work (if present)
- [ ] Refresh button works
- [ ] No errors
- [ ] Good performance (<5 sec load)
- [ ] Professional design

**Issues**: [None documented yet]
**Rating**: __/10

---

### 17. STREAMLIT_TENABLE
**App**: Tenable Vulnerability Management
**URL ID**: sfzrqgljlaon6xmifik5
**Deployed**: 2025-10-25 22:28:28

#### Testing Checklist
- [ ] Basic functionality (load, tabs, data, charts)
- [ ] Filters work correctly
- [ ] Download buttons work (if present)
- [ ] Refresh button works
- [ ] Metadata tab works (WARNING: Has 0 columns - no data)
- [ ] No errors
- [ ] Good performance (<5 sec load)
- [ ] Professional design

**Known Issue**: Metadata shows 0 columns - likely no data in tables
**Issues**: [Document after testing]
**Rating**: __/10

---

### 18. STREAMLIT_TRELLIX
**App**: Trellix Security Analytics
**URL ID**: 55ey7pn5jcs27a73ibam
**Deployed**: 2025-10-25 22:27:55

#### Testing Checklist
- [ ] Basic functionality (load, tabs, data, charts)
- [ ] Filters work correctly
- [ ] Download buttons work (if present)
- [ ] Refresh button works
- [ ] No errors
- [ ] Good performance (<5 sec load)
- [ ] Professional design

**Issues**: [None documented yet]
**Rating**: __/10

---

## Summary of Findings

### Critical Issues
- [To be populated during testing]

### High Priority Issues
- [To be populated during testing]

### Medium Priority Issues
- [To be populated during testing]

### Low Priority Issues
- [To be populated during testing]

### Design Improvements
- [To be populated during testing]

### Feature Enhancements
- [To be populated during testing]

---

## Testing Notes

### Apps with Metadata Tab (6 total)
1. **SentinelOne** - 76 columns
2. **CybelAngel** - 112 columns
3. **Proofpoint** - 23 columns
4. **ServiceNow** - 36 columns
5. **Leviat** - 146 columns
6. **Tenable** - 0 columns (⚠️ No data)

### Apps with Download Buttons (11 total)
- **Symantec** - 3 buttons
- **CrowdStrike** - 7 buttons
- **Leviat** - 7 buttons
- **ServiceNow** - 4 buttons
- Others - 1-2 buttons each

### Apps with Alert Thresholds (8 total)
- **CrowdStrike** - 4 alerts
- **Leviat** - 4 alerts
- **ServiceNow** - 4 alerts
- **Symantec** - 2 alerts
- Others - 2 alerts each

### Recently Fixed Apps
- **Sophos** - Fixed and redeployed on 2025-10-25 23:23 (all `np.random` and download button fixes applied)

---

## Next Steps

### After Testing Phase 1 (High Priority):
1. Document all issues found
2. Categorize by severity (Critical/High/Medium/Low)
3. Create fix priority list
4. Update improvement roadmap

### After Testing Phase 2 (Medium Priority):
1. Compare design consistency across apps
2. Identify common improvement opportunities
3. Test performance patterns

### After Complete Testing:
1. Create comprehensive issues document
2. Estimate effort for fixes
3. Create implementation timeline
4. Update project documentation

---

**Document Created**: 2025-10-27
**Status**: Ready for Testing
**Next Action**: Begin manual testing in Snowflake UI
