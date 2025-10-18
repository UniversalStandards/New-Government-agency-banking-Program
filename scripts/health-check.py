#!/usr/bin/env python3
"""
GOFAP Health Check and Monitoring Script
Performs comprehensive health checks on the GOFAP system
"""

import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

def run_command(cmd: List[str]) -> Dict[str, Any]:
    """Run a command and return the result."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Command timed out",
            "returncode": -1,
        }
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e), "returncode": -1}

def check_python_environment() -> Dict[str, Any]:
    """Check Python environment and dependencies."""
    print("🐍 Checking Python environment...")

    checks = {}

    # Python version
    checks["python_version"] = {
        "version": sys.version,
        "major_minor": f"{sys.version_info.major}.{sys.version_info.minor}",
        "compatible": sys.version_info >= (3, 10),
    }

    # Required files
    required_files = ["main.py", "requirements.txt", "models.py"]
    checks["required_files"] = {}
    for file in required_files:
        checks["required_files"][file] = Path(file).exists()

    # Dependencies check
    result = run_command(["pip", "check"])
    checks["dependencies"] = {
        "pip_check": result["success"],
        "output": result["stdout"] if result["success"] else result["stderr"],
    }

    return checks

def check_database_connectivity() -> Dict[str, Any]:
    """Check database connectivity."""
    print("🗃️ Checking database connectivity...")

    try:
        # Import here to avoid issues if modules aren't available
        from main import app, db

        with app.app_context():
            # Try to connect to database
            db.engine.connect()

            # Check if tables exist
            from sqlalchemy import inspect

            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            return {"connected": True, "tables_count": len(tables), "tables": tables}
    except Exception as e:
        return {"connected": False, "error": str(e)}

def check_application_startup() -> Dict[str, Any]:
    """Check if the Flask application starts properly."""
    print("🚀 Checking application startup...")

    try:
        from main import app

        # Test app configuration
        with app.app_context():
            config_check = {
                "debug": app.config.get("DEBUG"),
                "secret_key_set": bool(app.config.get("SECRET_KEY")),
                "database_uri_set": bool(app.config.get("SQLALCHEMY_DATABASE_URI")),
            }

        # Test route registration
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(
                {
                    "endpoint": rule.endpoint,
                    "methods": list(rule.methods),
                    "rule": str(rule),
                }
            )

        return {
            "startup_success": True,
            "config": config_check,
            "routes_count": len(routes),
            "routes": routes[:10],  # First 10 routes
        }
    except Exception as e:
        return {"startup_success": False, "error": str(e)}

def check_code_quality() -> Dict[str, Any]:
    """Check code quality with linting tools."""
    print("🔍 Checking code quality...")

    checks = {}

    # Flake8 critical errors
    result = run_command(
        [
            "flake8",
            ".",
            "--count",
            "--select=E9,F63,F7,F82",
            "--show-source",
            "--statistics",
        ]
    )
    checks["flake8_critical"] = {
        "passed": result["success"],
        "output": result["stdout"] if result["stdout"] else "No critical errors found",
    }

    # Black formatting check
    result = run_command(["black", "--check", "--diff", "."])
    checks["black_formatting"] = {
        "passed": result["success"],
        "needs_formatting": not result["success"],
        "output": (
            result["stdout"][:500] if result["stdout"] else "Code is properly formatted"
        ),
    }

    return checks

def check_security() -> Dict[str, Any]:
    """Basic security checks."""
    print("🔒 Checking security...")

    checks = {}

    # Check for common security issues with Bandit
    result = run_command(["bandit", "-r", ".", "-f", "json"])
    if result["success"]:
        try:
            import json

            bandit_data = json.loads(result["stdout"])
            checks["bandit"] = {
                "issues_count": len(bandit_data.get("results", [])),
                "high_severity": len(
                    [
                        r
                        for r in bandit_data.get("results", [])
                        if r.get("issue_severity") == "HIGH"
                    ]
                ),
                "passed": len(bandit_data.get("results", [])) == 0,
            }
        except:
            checks["bandit"] = {"error": "Could not parse Bandit output"}
    else:
        checks["bandit"] = {"error": result["stderr"]}

    # Check for hardcoded secrets (basic check)
    sensitive_patterns = ["api_key", "secret", "password", "token"]
    found_patterns = []

    for py_file in Path(".").glob("**/*.py"):
        if ".git" in str(py_file) or "__pycache__" in str(py_file):
            continue
        try:
            content = py_file.read_text().lower()
            for pattern in sensitive_patterns:
                if f"{pattern}=" in content or f"{pattern}:" in content:
                    found_patterns.append(f"{py_file}:{pattern}")
        except:
            continue

    checks["secrets_scan"] = {
        "potential_secrets": len(found_patterns),
        "details": found_patterns[:5],  # First 5 findings
        "passed": len(found_patterns) == 0,
    }

    return checks

def check_performance() -> Dict[str, Any]:
    """Basic performance checks."""
    print("⚡ Checking performance...")

    checks = {}

    # File count and sizes
    python_files = list(Path(".").glob("**/*.py"))
    total_size = sum(f.stat().st_size for f in python_files if f.is_file())

    checks["codebase_metrics"] = {
        "python_files": len(python_files),
        "total_size_kb": round(total_size / 1024, 2),
        "average_file_size_kb": (
            round(total_size / len(python_files) / 1024, 2) if python_files else 0
        ),
    }

    # Import time check
    start_time = time.time()
    try:
        pass

        import_time = time.time() - start_time
        checks["import_performance"] = {
            "import_time_seconds": round(import_time, 3),
            "acceptable": import_time < 2.0,
        }
    except Exception as e:
        checks["import_performance"] = {"error": str(e), "acceptable": False}

    return checks

def generate_health_report(results: Dict[str, Any]) -> str:
    """Generate a comprehensive health report."""
    report_lines = []
    report_lines.append(f"# 🏥 GOFAP Health Check Report")
    report_lines.append(
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
    )
    report_lines.append("")

    # Overall health score
    total_checks = 0
    passed_checks = 0

    for category, checks in results.items():
        if isinstance(checks, dict):
            for check_name, check_result in checks.items():
                total_checks += 1
                if isinstance(check_result, dict):
                    if (
                        check_result.get("passed")
                        or check_result.get("success")
                        or check_result.get("connected")
                    ):
                        passed_checks += 1
                elif check_result is True:
                    passed_checks += 1

    health_score = (
        round((passed_checks / total_checks) * 100, 1) if total_checks > 0 else 0
    )

    report_lines.append(
        f"## 🎯 Overall Health Score: {health_score}% ({passed_checks}/{total_checks} checks passed)"
    )
    report_lines.append("")

    # Status indicators
    if health_score >= 90:
        report_lines.append("### ✅ Status: HEALTHY - All systems operational")
    elif health_score >= 70:
        report_lines.append("### ⚠️ Status: ATTENTION NEEDED - Some issues detected")
    else:
        report_lines.append(
            "### 🚨 Status: CRITICAL - Multiple issues require immediate attention"
        )

    report_lines.append("")

    # Detailed results for each category
    for category, checks in results.items():
        category_name = category.replace("_", " ").title()
        report_lines.append(f"## {category_name}")

        if isinstance(checks, dict):
            for check_name, check_result in checks.items():
                status = (
                    "✅"
                    if (
                        isinstance(check_result, dict)
                        and (
                            check_result.get("passed")
                            or check_result.get("success")
                            or check_result.get("connected")
                        )
                    )
                    or check_result is True
                    else "❌"
                )
                report_lines.append(
                    f"- {status} **{check_name.replace('_', ' ').title()}**"
                )

                if isinstance(check_result, dict):
                    for key, value in check_result.items():
                        if key not in ["passed", "success", "connected"] and value:
                            if isinstance(value, (str, int, float, bool)):
                                report_lines.append(f"  - {key}: {value}")

        report_lines.append("")

    # Recommendations
    report_lines.append("## 🎯 Recommendations")
    if health_score >= 90:
        report_lines.append("- ✅ System is healthy! Continue with regular maintenance")
    else:
        report_lines.append("- 🔧 Address failing health checks")
        report_lines.append("- 📊 Run detailed diagnostics for failing components")
        report_lines.append("- 🔄 Re-run health check after fixes")

    return "\n".join(report_lines)

def main():
    """Run comprehensive health checks."""
    print("🏥 Starting GOFAP Health Check...\n")

    # Change to the directory containing this script
    os.chdir(Path(__file__).parent.parent)

    results = {}

    try:
        results["python_environment"] = check_python_environment()
        results["database_connectivity"] = check_database_connectivity()
        results["application_startup"] = check_application_startup()
        results["code_quality"] = check_code_quality()
        results["security"] = check_security()
        results["performance"] = check_performance()

        # Generate report
        report = generate_health_report(results)

        # Save report
        report_file = Path("health-check-report.md")
        report_file.write_text(report)

        print(f"\n✅ Health check completed!")
        print(f"📄 Report saved to: {report_file}")
        print("\n" + "=" * 80)
        print(report)

        # Exit with appropriate code
        health_score = 0
        total_checks = 0
        passed_checks = 0

        for category, checks in results.items():
            if isinstance(checks, dict):
                for check_name, check_result in checks.items():
                    total_checks += 1
                    if isinstance(check_result, dict):
                        if (
                            check_result.get("passed")
                            or check_result.get("success")
                            or check_result.get("connected")
                        ):
                            passed_checks += 1

        health_score = (passed_checks / total_checks) * 100 if total_checks > 0 else 0

        if health_score < 70:
            sys.exit(1)  # Critical issues
        elif health_score < 90:
            sys.exit(2)  # Warnings
        else:
            sys.exit(0)  # All good

    except Exception as e:
        print(f"❌ Health check failed with error: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()
