"""
Add alert thresholds for key metrics in Streamlit apps
Adds colored alerts (error/warning/success) for coverage, health scores, risk levels
"""
import os
import re
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def add_coverage_alerts(content):
    """Add alert thresholds for coverage metrics"""
    lines = content.split('\n')
    new_lines = []
    alerts_added = 0

    for i, line in enumerate(lines):
        new_lines.append(line)

        # Look for coverage percentage display patterns
        # Pattern 1: st.metric with "Coverage" or "COVERAGE"
        if 'st.metric(' in line and ('Coverage' in line or 'COVERAGE' in line):
            # Check if alert already exists after this metric
            if i + 1 < len(lines) and ('st.error' in lines[i+1] or 'st.warning' in lines[i+1] or 'st.success' in lines[i+1]):
                continue

            # Try to find the variable being displayed
            # Look backward for variable assignment
            coverage_var = None
            for j in range(i-1, max(0, i-10), -1):
                var_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=.*(?:coverage|COVERAGE).*pct', lines[j], re.IGNORECASE)
                if var_match:
                    coverage_var = var_match.group(1)
                    break

            if coverage_var:
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent

                alert_code = [
                    f"{indent_str}# Coverage alert threshold",
                    f"{indent_str}if {coverage_var} < 90:",
                    f"{indent_str}    st.error(f\"⚠️ Coverage below target: {{{coverage_var}:.1f}}% (Target: 90%)\")",
                    f"{indent_str}elif {coverage_var} < 95:",
                    f"{indent_str}    st.warning(f\"⚡ Coverage needs improvement: {{{coverage_var}:.1f}}% (Target: 95%)\")",
                    f"{indent_str}else:",
                    f"{indent_str}    st.success(f\"✅ Coverage meets target: {{{coverage_var}:.1f}}%\")"
                ]

                new_lines.extend(alert_code)
                alerts_added += 1

    return '\n'.join(new_lines), alerts_added

def add_health_score_alerts(content):
    """Add alert thresholds for health scores"""
    lines = content.split('\n')
    new_lines = []
    alerts_added = 0

    for i, line in enumerate(lines):
        new_lines.append(line)

        # Look for health score patterns
        if 'st.metric(' in line and ('Health' in line or 'HEALTH' in line or 'Score' in line):
            # Check if alert already exists
            if i + 1 < len(lines) and ('st.error' in lines[i+1] or 'st.warning' in lines[i+1] or 'st.success' in lines[i+1]):
                continue

            # Try to find the variable
            health_var = None
            for j in range(i-1, max(0, i-10), -1):
                var_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=.*(?:health|score)', lines[j], re.IGNORECASE)
                if var_match and 'coverage' not in lines[j].lower():  # Avoid coverage variables
                    health_var = var_match.group(1)
                    break

            if health_var:
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent

                alert_code = [
                    f"{indent_str}# Health score alert threshold",
                    f"{indent_str}if {health_var} < 70:",
                    f"{indent_str}    st.error(f\"⚠️ Health score critical: {{{health_var}:.1f}} (Target: >70)\")",
                    f"{indent_str}elif {health_var} < 85:",
                    f"{indent_str}    st.warning(f\"⚡ Health score needs improvement: {{{health_var}:.1f}} (Target: >85)\")",
                    f"{indent_str}else:",
                    f"{indent_str}    st.success(f\"✅ Health score good: {{{health_var}:.1f}}\")"
                ]

                new_lines.extend(alert_code)
                alerts_added += 1

    return '\n'.join(new_lines), alerts_added

def add_critical_risk_alerts(content):
    """Add alerts for critical/high risk counts"""
    lines = content.split('\n')
    new_lines = []
    alerts_added = 0

    for i, line in enumerate(lines):
        new_lines.append(line)

        # Look for critical/high risk counts
        if 'st.metric(' in line and ('Critical' in line or 'CRITICAL' in line or 'High Risk' in line):
            # Check if alert already exists
            if i + 1 < len(lines) and ('st.error' in lines[i+1] or 'st.warning' in lines[i+1] or 'st.success' in lines[i+1]):
                continue

            # Try to find the variable
            risk_var = None
            for j in range(i-1, max(0, i-10), -1):
                var_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=.*(?:critical|high.*risk|len\()', lines[j], re.IGNORECASE)
                if var_match:
                    risk_var = var_match.group(1)
                    break

            if risk_var:
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent

                alert_code = [
                    f"{indent_str}# Critical risk alert threshold",
                    f"{indent_str}if {risk_var} > 10:",
                    f"{indent_str}    st.error(f\"⚠️ High number of critical risks: {{{risk_var}}} (Action required!)\")",
                    f"{indent_str}elif {risk_var} > 0:",
                    f"{indent_str}    st.warning(f\"⚡ {{{risk_var}}} critical risk(s) found - Review needed\")",
                    f"{indent_str}else:",
                    f"{indent_str}    st.success(\"✅ No critical risks found - Good security posture!\")"
                ]

                new_lines.extend(alert_code)
                alerts_added += 1

    return '\n'.join(new_lines), alerts_added

def process_app(app_path, app_name):
    """Process a single Streamlit app"""
    try:
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()

        total_alerts = 0

        # Add coverage alerts
        content, alerts = add_coverage_alerts(content)
        total_alerts += alerts

        # Add health score alerts
        content, alerts = add_health_score_alerts(content)
        total_alerts += alerts

        # Add critical risk alerts
        content, alerts = add_critical_risk_alerts(content)
        total_alerts += alerts

        if total_alerts > 0:
            with open(app_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ {app_name}: Added {total_alerts} alert thresholds")
            return True, total_alerts
        else:
            print(f"⚠️  {app_name}: No metrics found for alerts")
            return False, 0

    except Exception as e:
        print(f"❌ {app_name}: Error - {str(e)}")
        return False, 0

def main():
    """Process all Streamlit apps"""
    base_dir = "13_STREAMLIT_COMPLETE"

    services = [
        "Ancon", "BitSight", "Cisco_AMP", "Crowdstrike", "CybelAngel",
        "Intel_Threats", "Leviat", "Proofpoint", "Qualys", "SentinelOne",
        "ServiceNow", "Sophos", "Splunk", "Symantec", "Tenable",
        "Trellix", "Zerofox", "Zscaler"
    ]

    total_apps = 0
    total_alerts = 0

    print("=" * 60)
    print("Adding Alert Thresholds to Streamlit Apps")
    print("=" * 60)

    for service in services:
        app_path = os.path.join(base_dir, service, "streamlit_app.py")
        if os.path.exists(app_path):
            success, alerts = process_app(app_path, service)
            if success:
                total_apps += 1
                total_alerts += alerts

    print("=" * 60)
    print(f"✅ Summary: Added {total_alerts} alert thresholds to {total_apps} apps")
    print("=" * 60)

if __name__ == "__main__":
    main()
