#!/usr/bin/env python3
"""
Issue Bulk Processor for GOFAP Repository

This script helps process large numbers of issues systematically:
- Categorize issues by type, severity, and component
- Identify duplicates
- Bulk label and assign issues
- Generate reports and metrics
- Close stale or resolved issues in bulk

Usage:
    python scripts/issue_bulk_processor.py --action categorize
    python scripts/issue_bulk_processor.py --action find-duplicates
    python scripts/issue_bulk_processor.py --action report
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Set
import re

# Note: This script requires the GitHub CLI (gh) to be installed and authenticated


class IssueBulkProcessor:
    """Processes issues in bulk for the GOFAP repository."""

    def __init__(self, repo: str = None):
        import os
        
        self.repo = repo or os.environ.get(
            "GITHUB_REPOSITORY", 
            "UniversalStandards/New-Government-agency-banking-Program"
        )
        self.issues = []
        self.categories = defaultdict(list)

    def fetch_issues(self, state: str = "open") -> List[Dict]:
        """Fetch all issues from the repository."""
        import subprocess

        print(f"Fetching {state} issues from {self.repo}...")
        cmd = [
            "gh",
            "issue",
            "list",
            "--repo",
            self.repo,
            "--state",
            state,
            "--limit",
            "2000",
            "--json",
            "number,title,body,labels,state,createdAt,updatedAt,assignees,author",
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.issues = json.loads(result.stdout)
            print(f"Fetched {len(self.issues)} issues")
            return self.issues
        except subprocess.CalledProcessError as e:
            print(f"Error fetching issues: {e.stderr}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            sys.exit(1)

    def categorize_issues(self) -> Dict[str, List[Dict]]:
        """Categorize issues by type, priority, and component."""
        print("\nCategorizing issues...")

        categories = {
            "critical": [],
            "high_priority": [],
            "medium_priority": [],
            "low_priority": [],
            "bugs": [],
            "enhancements": [],
            "documentation": [],
            "security": [],
            "ci_cd": [],
            "frontend": [],
            "backend": [],
            "database": [],
            "api": [],
            "uncategorized": [],
            "stale": [],
            "needs_triage": [],
        }

        stale_date = datetime.now() - timedelta(days=30)

        for issue in self.issues:
            labels = [label["name"].lower() for label in issue.get("labels", [])]
            updated_at = datetime.fromisoformat(issue["updatedAt"].replace("Z", "+00:00"))

            # Priority categorization
            if "critical" in labels:
                categories["critical"].append(issue)
            elif "high-priority" in labels or "high priority" in labels:
                categories["high_priority"].append(issue)
            elif "low-priority" in labels or "low priority" in labels:
                categories["low_priority"].append(issue)
            elif "medium-priority" in labels or "medium priority" in labels:
                categories["medium_priority"].append(issue)

            # Type categorization
            if "bug" in labels:
                categories["bugs"].append(issue)
            if "enhancement" in labels or "feature" in labels:
                categories["enhancements"].append(issue)
            if "documentation" in labels:
                categories["documentation"].append(issue)
            if "security" in labels or "vulnerability" in labels:
                categories["security"].append(issue)

            # Component categorization
            if "ci-cd" in labels or "workflow" in labels:
                categories["ci_cd"].append(issue)
            if "frontend" in labels or "ui" in labels:
                categories["frontend"].append(issue)
            if "backend" in labels:
                categories["backend"].append(issue)
            if "database" in labels:
                categories["database"].append(issue)
            if "api" in labels:
                categories["api"].append(issue)

            # Status
            if "needs-triage" in labels or not labels:
                categories["needs_triage"].append(issue)
            if updated_at < stale_date:
                categories["stale"].append(issue)

            # Uncategorized (no type labels)
            type_labels = ["bug", "enhancement", "documentation", "question", "security"]
            if not any(label in labels for label in type_labels):
                categories["uncategorized"].append(issue)

        self.categories = categories
        return categories

    def find_duplicates(self) -> List[List[Dict]]:
        """Find potential duplicate issues using simple text matching."""
        print("\nFinding potential duplicates...")

        # Group issues by similar titles
        title_groups = defaultdict(list)

        for issue in self.issues:
            # Normalize title: lowercase, remove special chars, split into words
            title = issue["title"].lower()
            title = re.sub(r"[^\w\s]", " ", title)
            words = set(title.split())

            # Create a key from significant words (>3 chars)
            key_words = sorted([w for w in words if len(w) > 3])
            if key_words:
                key = " ".join(key_words[:5])  # Use first 5 significant words
                title_groups[key].append(issue)

        # Filter to groups with 2+ issues
        duplicates = [group for group in title_groups.values() if len(group) >= 2]

        print(f"Found {len(duplicates)} potential duplicate groups")
        return duplicates

    def generate_report(self) -> str:
        """Generate a comprehensive report of issues."""
        if not self.categories:
            self.categorize_issues()

        report = []
        report.append("# GOFAP Repository Issue Report")
        report.append(f"\n**Generated:** {datetime.now().isoformat()}")
        report.append(f"**Total Issues:** {len(self.issues)}\n")

        # Priority breakdown
        report.append("## Priority Breakdown\n")
        report.append(f"- 🔴 **Critical:** {len(self.categories['critical'])}")
        report.append(f"- 🟠 **High:** {len(self.categories['high_priority'])}")
        report.append(f"- 🟡 **Medium:** {len(self.categories['medium_priority'])}")
        report.append(f"- 🟢 **Low:** {len(self.categories['low_priority'])}\n")

        # Type breakdown
        report.append("## Type Breakdown\n")
        report.append(f"- 🐛 **Bugs:** {len(self.categories['bugs'])}")
        report.append(f"- ✨ **Enhancements:** {len(self.categories['enhancements'])}")
        report.append(f"- 📚 **Documentation:** {len(self.categories['documentation'])}")
        report.append(f"- 🔒 **Security:** {len(self.categories['security'])}\n")

        # Component breakdown
        report.append("## Component Breakdown\n")
        report.append(f"- ⚙️ **CI/CD:** {len(self.categories['ci_cd'])}")
        report.append(f"- 🎨 **Frontend:** {len(self.categories['frontend'])}")
        report.append(f"- ⚡ **Backend:** {len(self.categories['backend'])}")
        report.append(f"- 🗄️ **Database:** {len(self.categories['database'])}")
        report.append(f"- 🔌 **API:** {len(self.categories['api'])}\n")

        # Action items
        report.append("## Action Items\n")
        report.append(f"- 🔍 **Needs Triage:** {len(self.categories['needs_triage'])}")
        report.append(f"- ⏰ **Stale Issues:** {len(self.categories['stale'])}")
        report.append(f"- ❓ **Uncategorized:** {len(self.categories['uncategorized'])}\n")

        # Top critical issues
        if self.categories["critical"]:
            report.append("## Critical Issues (Immediate Action Required)\n")
            for issue in self.categories["critical"][:10]:
                report.append(f"- #{issue['number']}: {issue['title']}")
            report.append("")

        # Stale issues
        if self.categories["stale"]:
            report.append(f"## Stale Issues (No activity in 30+ days)\n")
            report.append(f"Total: {len(self.categories['stale'])}\n")
            for issue in self.categories["stale"][:5]:
                updated = issue["updatedAt"][:10]
                report.append(f"- #{issue['number']}: {issue['title']} (last update: {updated})")
            report.append("")

        return "\n".join(report)

    def export_categories(self, output_file: str = "issue_categories.json"):
        """Export categorized issues to JSON file."""
        if not self.categories:
            self.categorize_issues()

        # Convert to serializable format
        export_data = {}
        for category, issues in self.categories.items():
            export_data[category] = [
                {"number": issue["number"], "title": issue["title"]} for issue in issues
            ]

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2)

        print(f"\nExported categories to {output_file}")

    def bulk_label(self, issue_numbers: List[int], labels: List[str], dry_run: bool = True):
        """Add labels to multiple issues."""
        import subprocess

        print(f"\nBulk labeling {len(issue_numbers)} issues with: {', '.join(labels)}")

        if dry_run:
            print("DRY RUN - No changes will be made")
            return

        for number in issue_numbers:
            cmd = [
                "gh",
                "issue",
                "edit",
                str(number),
                "--repo",
                self.repo,
                "--add-label",
                ",".join(labels),
            ]
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                print(f"  ✓ Labeled #{number}")
            except subprocess.CalledProcessError as e:
                print(f"  ✗ Error labeling #{number}: {e.stderr.decode()}")

    def bulk_close(self, issue_numbers: List[int], reason: str, dry_run: bool = True):
        """Close multiple issues with a reason."""
        import subprocess

        print(f"\nBulk closing {len(issue_numbers)} issues")
        print(f"Reason: {reason}")

        if dry_run:
            print("DRY RUN - No changes will be made")
            return

        for number in issue_numbers:
            # Add comment with reason
            comment_cmd = [
                "gh",
                "issue",
                "comment",
                str(number),
                "--repo",
                self.repo,
                "--body",
                reason,
            ]

            # Close issue
            close_cmd = [
                "gh",
                "issue",
                "close",
                str(number),
                "--repo",
                self.repo,
                "--reason",
                "not_planned",
            ]

            try:
                subprocess.run(comment_cmd, check=True, capture_output=True)
                subprocess.run(close_cmd, check=True, capture_output=True)
                print(f"  ✓ Closed #{number}")
            except subprocess.CalledProcessError as e:
                print(f"  ✗ Error closing #{number}: {e.stderr.decode()}")


def main():
    parser = argparse.ArgumentParser(
        description="Bulk process issues in GOFAP repository"
    )
    parser.add_argument(
        "--action",
        choices=["categorize", "find-duplicates", "report", "export", "label", "close"],
        required=True,
        help="Action to perform",
    )
    parser.add_argument(
        "--state", choices=["open", "closed", "all"], default="open", help="Issue state"
    )
    parser.add_argument(
        "--output", default="issue_report.md", help="Output file for reports"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Don't make actual changes"
    )
    parser.add_argument("--labels", nargs="+", help="Labels to add (for label action)")
    parser.add_argument(
        "--issues", nargs="+", type=int, help="Issue numbers (for label/close actions)"
    )

    args = parser.parse_args()

    processor = IssueBulkProcessor()
    processor.fetch_issues(state=args.state)

    if args.action == "categorize":
        categories = processor.categorize_issues()
        print("\n=== Categorization Results ===")
        for category, issues in categories.items():
            if issues:
                print(f"{category}: {len(issues)} issues")

    elif args.action == "find-duplicates":
        duplicates = processor.find_duplicates()
        print("\n=== Potential Duplicates ===")
        for i, group in enumerate(duplicates[:20], 1):  # Show first 20 groups
            print(f"\nGroup {i}:")
            for issue in group:
                print(f"  - #{issue['number']}: {issue['title']}")

    elif args.action == "report":
        report = processor.generate_report()
        print(report)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\nReport saved to {args.output}")

    elif args.action == "export":
        processor.categorize_issues()
        processor.export_categories(args.output)

    elif args.action == "label":
        if not args.issues or not args.labels:
            print("Error: --issues and --labels required for label action")
            sys.exit(1)
        processor.bulk_label(args.issues, args.labels, dry_run=args.dry_run)

    elif args.action == "close":
        if not args.issues:
            print("Error: --issues required for close action")
            sys.exit(1)
        reason = "Closing as part of bulk issue cleanup. Please reopen if still relevant."
        processor.bulk_close(args.issues, reason, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
