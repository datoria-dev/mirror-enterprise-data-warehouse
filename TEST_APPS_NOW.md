# Testing All Updated Streamlit Apps - Quick Guide

**Date**: 2025-10-27
**Status**: ✅ All 18 files uploaded successfully
**Updates**: CPR prefix + Syntax fixes (Trellix, Crowdstrike)

---

## 🎯 Priority Testing (Test these FIRST)

### 1. STREAMLIT_TRELLIX (Fixed syntax error at line 987)
**URL**: https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/55ey7pn5jcs27a73ibam
**What to check**:
- ✅ App loads without syntax errors
- ✅ Title shows "CPR - Trellix Security Analytics" (in browser tab)
- ✅ OPCO Scorecard displays correctly (line 987 fix)
- ✅ Coverage metrics display without errors
- ✅ Alert thresholds work (if coverage < 90%)

**Expected**: Should load completely without "SyntaxError: invalid syntax" message

---

### 2. STREAMLIT_CROWDSTRIKE (Fixed syntax error at line 139)
**URL**: https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/pezbdllntnq4ae4pdy3s
**What to check**:
- ✅ App loads without syntax errors
- ✅ Title shows "CPR - CrowdStrike Falcon Dashboard" (in browser tab)
- ✅ safe_query function works (line 139 fix)
- ✅ Database context set correctly
- ✅ All tabs load (Overview, Data Tables, Trends)
- ✅ Download CSV buttons work (has 7 buttons)

**Expected**: Should load completely without "SyntaxError" or function errors

---

### 3. STREAMLIT_SOPHOS (Recently fixed - np.random issues)
**URL**: https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/ivusmm45shxz5u6l6jao
**What to check**:
- ✅ App loads without errors
- ✅ Title shows "CPR - Sophos Security Dashboard"
- ✅ No "np.random" AttributeError messages
- ✅ Download CSV buttons work (all 6 fixed)
- ✅ Refresh button doesn't cause errors

**Expected**: All fixes from previous deployment should be present

---

## 📋 Sample Testing (Test a few from each category)

### Endpoint Security Apps

#### STREAMLIT_SYMANTEC
**URL**: https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/j26cqmbpm3w42zj5njj3
**Check**: CPR prefix, loads correctly, has 3 download buttons, 2 alerts

#### STREAMLIT_SENTINELONE
**URL**: https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/ab6eno3icam5zbwlhhx4
**Check**: CPR prefix, Metadata tab (76 columns), search works

---

### Threat Intelligence Apps

#### STREAMLIT_ZEROFOX
**URL**: https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/gxlmxtd2qphzainafl7k
**Check**: CPR prefix, professional design (this is the template app)

#### STREAMLIT_CYBELANGEL
**URL**: https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/wakynkevgf73ymcmy7lz
**Check**: CPR prefix, Metadata tab (112 columns)

---

### Vulnerability Management Apps

#### STREAMLIT_QUALYS
**URL**: https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/bv6rqf25654g2zjlkx2w
**Check**: CPR prefix, vulnerability aging analysis

#### STREAMLIT_TENABLE
**URL**: https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/sfzrqgljlaon6xmifik5
**Check**: CPR prefix, NOTE: has 0 columns in metadata (known issue)

---

### Operations & SIEM Apps

#### STREAMLIT_SPLUNK
**URL**: https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/3f5pbwn2vpzizdtqjiuj
**Check**: CPR prefix, event analysis works

#### STREAMLIT_SERVICENOW
**URL**: https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/kscpsgajtow5g5rzzsnp
**Check**: CPR prefix, 4 download buttons, 4 alerts, Metadata tab (36 columns)

---

## 🔍 Complete App List with URLs

| # | App Name | URL | Priority | Notes |
|---|----------|-----|----------|-------|
| 1 | STREAMLIT_ANCON | [Link](https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/zbapkxmoz3zx5vvd3cbj) | Medium | |
| 2 | STREAMLIT_BITSIGHT | [Link](https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/ebeyj2mwi2vvcvvzxqt4) | Medium | |
| 3 | STREAMLIT_CISCO_AMP | [Link](https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/neazn6tegg3whessq2qp) | Medium | |
| 4 | STREAMLIT_CROWDSTRIKE | [Link](https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/pezbdllntnq4ae4pdy3s) | **HIGH** | **Syntax fix line 139** |
| 5 | STREAMLIT_CYBELANGEL | [Link](https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/wakynkevgf73ymcmy7lz) | Medium | Metadata: 112 cols |
| 6 | STREAMLIT_INTEL_THREATS | [Link](https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/75jkkznw75ogsfrgzjhk) | Medium | |
| 7 | STREAMLIT_LEVIAT | [Link](https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/ft6lmkagcxv2lszahsda) | Medium | 7 downloads, 4 alerts |
| 8 | STREAMLIT_PROOFPOINT | [Link](https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/7gjf7suceieycvpd5huy) | Medium | Metadata: 23 cols |
| 9 | STREAMLIT_QUALYS | [Link](https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/bv6rqf25654g2zjlkx2w) | High | Vuln management |
| 10 | STREAMLIT_SENTINELONE | [Link](https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/ab6eno3icam5zbwlhhx4) | High | Metadata: 76 cols |
| 11 | STREAMLIT_SERVICENOW | [Link](https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/kscpsgajtow5g5rzzsnp) | Medium | 4 downloads, 4 alerts |
| 12 | STREAMLIT_SOPHOS | [Link](https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/ivusmm45shxz5u6l6jao) | **HIGH** | **np.random fixes** |
| 13 | STREAMLIT_SPLUNK | [Link](https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/3f5pbwn2vpzizdtqjiuj) | Medium | |
| 14 | STREAMLIT_SYMANTEC | [Link](https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/j26cqmbpm3w42zj5njj3) | High | 3 downloads, 2 alerts |
| 15 | STREAMLIT_TENABLE | [Link](https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/sfzrqgljlaon6xmifik5) | Medium | ⚠️ 0 columns metadata |
| 16 | STREAMLIT_TRELLIX | [Link](https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/55ey7pn5jcs27a73ibam) | **HIGH** | **Syntax fix line 987** |
| 17 | STREAMLIT_ZEROFOX | [Link](https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/gxlmxtd2qphzainafl7k) | High | Template app |
| 18 | STREAMLIT_ZSCALER | [Link](https://app.snowflake.com/GenericCorp-CRH_EDW/#/streamlit-apps/xnnfrjrms5hh74tu26t5) | Medium | |

---

## ✅ Quick Testing Checklist (For Each App)

### Basic Functionality
- [ ] App loads without errors
- [ ] Page title shows "CPR - [Service Name]" in browser tab
- [ ] Main header displays correctly
- [ ] Data loads in tables

### Features
- [ ] Date filters work (if present)
- [ ] Category filters work (if present)
- [ ] Download CSV buttons work (if present)
- [ ] Refresh button doesn't cause errors
- [ ] Metadata tab loads (if present)
- [ ] Charts display correctly

### Visual/UX
- [ ] Professional design (gradient header, styled cards)
- [ ] No layout issues
- [ ] Hover effects work on metrics
- [ ] Tabs are styled correctly

---

## 🐛 Known Issues to Verify Are Fixed

### 1. Trellix - Line 987 Syntax Error
**Before**:
```python
st.metric("Coverage", f"{coverage:.1f}%",
# Comment in wrong place
if coverage < 90:
         delta=f"{coverage-95:.1f}%")  # Parameter misplaced
```

**After (Fixed)**:
```python
st.metric("Coverage", f"{coverage:.1f}%",
         delta=f"{coverage-95:.1f}%")
if coverage < 90:  # Comment after
```

**Test**: Coverage metric should display correctly with delta value

---

### 2. Crowdstrike - Line 139 Syntax Error
**Before**:
```python
def safe_query(...):
    try:
        session = get_active_session()
# Wrong indentation - outside function
try:
    session.sql("USE DATABASE...").collect()
```

**After (Fixed)**:
```python
def safe_query(...):
    try:
        session = get_active_session()
        # Correct indentation - inside function
        try:
            session.sql("USE DATABASE...").collect()
```

**Test**: App should load data correctly without database context errors

---

### 3. Sophos - np.random Errors
**Before**: Used `np.random.random()` which caused AttributeError

**After (Fixed)**: All 6 instances replaced with unique keys:
- `key=f"download_alerts_{datetime.now().timestamp()}"`
- `key=f"download_endpoints_{datetime.now().timestamp()}"`
- etc.

**Test**: All download buttons should work without "np.random" errors

---

## 📊 Testing Results Template

Use this to track your testing:

```
App Tested: _________________
Date: 2025-10-27
Tester: Fuad Onate

[ ] Loads without errors
[ ] CPR prefix visible
[ ] All features work
[ ] No syntax errors
[ ] Professional design

Issues Found:
-

Overall Rating: __/10

Notes:
```

---

## 🚀 Quick Start Testing Instructions

1. **Open Snowflake** (you're already authenticated from file upload)
2. **Test Priority Apps First** (Trellix, Crowdstrike, Sophos)
3. **Click the URL links above** to access each app directly
4. **Check for**:
   - "CPR - " prefix in browser tab title
   - No syntax errors or crashes
   - Download buttons work (if present)
   - Professional design renders correctly
5. **Document any issues** in [STREAMLIT_TESTING_RESULTS.md](STREAMLIT_TESTING_RESULTS.md)

---

## ✨ Expected Results

### All Apps Should Have:
1. ✅ "CPR - " prefix in page title
2. ✅ No syntax errors
3. ✅ Professional gradient design
4. ✅ Functional filters and buttons
5. ✅ Data displays correctly
6. ✅ Same quality as ZeroFox template

### Apps Fixed Today:
- **Trellix**: Line 987 syntax error FIXED
- **Crowdstrike**: Line 139 syntax error FIXED
- **All 18 apps**: CPR prefix ADDED

---

## 📝 After Testing

Once you've tested the priority apps, update:
1. [STREAMLIT_TESTING_RESULTS.md](STREAMLIT_TESTING_RESULTS.md) - Mark checkboxes, add ratings
2. [ALL_APPS_FIXED_SUMMARY.md](ALL_APPS_FIXED_SUMMARY.md) - Update status
3. Let me know if any issues found so we can fix them

---

**Ready to test!** Start with the 3 priority apps (Trellix, Crowdstrike, Sophos) using the URLs above.
