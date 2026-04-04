> [!IMPORTANT]
> ## ⚠️ This Repository is an Archived Prototype
>
> **This Python/Flask prototype has been superseded by the full TypeScript production platform.**
>
> ### ➡️ Active Repository: [UniversalStandards/GOFAP](https://github.com/UniversalStandards/GOFAP)
>
> All active development, issues, contributions, and deployments have moved to the main GOFAP repo.  
> This repository is preserved for historical reference only. No further updates will be made here.

---

# 🏛️ GOFAP — Government Operations and Financial Accounting Platform
### Python/Flask Prototype (Legacy · Archived)

![Status](https://img.shields.io/badge/Status-Archived%20%E2%80%94%20Superseded-lightgrey?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.12+-blue?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-3.1.2-green?style=flat-square)

This repository contains the **original Python/Flask prototype** of GOFAP, developed in mid-2024 as a proof-of-concept for:

- Digital banking account creation via Stripe and Modern Treasury APIs
- Government-level treasury operations and ACH payment flows
- SolidFi and Unit.co Banking-as-a-Service integration prototyping
- Early constituent services portal concept
- Initial financial management UI built with Bootstrap 5

---

## 🔄 Migration to Production Platform

The full production system — **GOFAPS (Government Operations, Financial, Accounting & Personnel System)** — is a complete TypeScript rewrite with a significantly expanded feature set:

| Feature Area | This Prototype | [Production Platform](https://github.com/UniversalStandards/GOFAP) |
|---|---|---|
| **Language / Stack** | Python 3.12 + Flask | TypeScript + React 18 + Node.js/Express |
| **Database** | SQLite / PostgreSQL (SQLAlchemy) | PostgreSQL / Neon (Drizzle ORM) |
| **UI** | Bootstrap 5 + Jinja2 templates | React + Shadcn/ui + Tailwind CSS |
| **Authentication** | Flask-Login | OIDC / Replit Auth + PostgreSQL sessions |
| **Financial** | Basic GL, accounts, payments | Full multi-fund GL, AP/AR, treasury, budget |
| **HR Module** | ❌ Not included | ✅ Full HR lifecycle + payroll |
| **Procurement** | ❌ Not included | ✅ Solicitation through contract closeout |
| **Fleet & Assets** | ❌ Not included | ✅ Full fleet lifecycle + capital assets |
| **Constituent Services** | ❌ Not included | ✅ Configurable public portals (9 agency types) |
| **Analytics / AI** | Basic dashboards | Predictive analytics + ATLANTIS.AI integration |
| **Deployment** | Gunicorn / Docker | AWS EC2, Azure, UpCloud, Vercel, Render, Free Tier |
| **Compliance** | Basic security | FISMA, NIST 800-53, FedRAMP-aligned, Section 508 |

---

## 🗂️ Prototype Features (Historical Reference)

### Banking & Treasury
- Digital bank account creation via Modern Treasury and Stripe
- Multi-currency support (USD, EUR, GBP, CAD)
- Treasury cash flow management and inter-fund transfers
- PayPal integration scaffolding

### Financial Operations
- Payment processing (vendor, payroll, tax collection)
- Department-level budget tracking and allocations
- Real-time transaction processing with audit trails
- Basic financial analytics dashboards

### Security
- Role-based access control (Flask-Login)
- Session management with configurable timeout
- Comprehensive audit logging
- Parameterized queries (SQLAlchemy ORM)
- CSRF protection

### CI/CD Workflows (12 GitHub Actions)
- Comprehensive CI pipeline with security scanning
- CodeQL analysis for vulnerability detection
- Multi-version Python testing (3.9, 3.10, 3.11)
- Dependency review and Frogbot Xray scanning
- Automated PR labeling and issue summarization

---

## 📦 Historical Quick Start (For Reference Only)

```bash
git clone https://github.com/UniversalStandards/New-Government-agency-banking-Program.git
cd New-Government-agency-banking-Program
pip install -r requirements.txt
cp .env.example .env
# Configure .env with Stripe / Modern Treasury keys
python main.py
# Access at http://127.0.0.1:5000
```

---

## 📄 License

This project is licensed under [The Unlicense](LICENSE) — released into the public domain.

---

## 📞 Support & Contact

All support requests should be directed to the **active production platform**:

➡️ **[UniversalStandards/GOFAP](https://github.com/UniversalStandards/GOFAP)**

| Channel | Details |
|---|---|
| **Office (OFAPS)** | gofap@ofaps.spurs.gov |
| **Phone** | (844) 697-7877 ext. 6327 |
| **Live Platform** | [replit.com/@rootgov/GovFlowPro](https://replit.com/@rootgov/GovFlowPro) |

---

<div align="center">

**"We Account for Everything"**

*Office of Finance, Accounting & Personnel Services (OFAPS)*  
*US Department of Special Projects and Unified Response Services · spurs.gov*

</div>
