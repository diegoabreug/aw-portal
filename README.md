# AW Client Report Portal

A robust, automated reporting portal designed for Windbrook Solutions to streamline the generation of SACS (Simple Automated Cashflow System) and TCC (Total Client Chart) financial reports.

## Features
- **Client Management:** Full CRUD operations for client profiles with dynamic partner/spouse tracking.
- **Automated Calculations:** Dynamic SACS logic for cash flow analysis and net worth segregation.
- **PDF Generation:** Automated, high-fidelity PDF reports (SACS & TCC) using ReportLab with dynamic layout algorithms to prevent data overlap.
- **Historical Data:** Persistent storage of quarterly reports for compliance and longitudinal analysis.

## Live Demo
Check out the live application hosted on Railway:
[https://aw-portal-production-076f.up.railway.app](https://aw-portal-production-076f.up.railway.app)
*(Note: You can explore the pre-loaded client profiles to test the report generation flow.)*

## Technical Stack
- **Backend:** Python / Flask
- **Database:** SQLite
- **PDF Generation:** ReportLab
- **Deployment:** Railway (with persistent volume storage)

## Quick Start
1. Clone the repository:
   ```bash
   git clone [https://github.com/diegoabreug/aw-portal.git](https://github.com/diegoabreug/aw-portal.git)
Install dependencies:

Bash
pip install -r requirements.txt
Run the application:

Bash
python app.py
Key Business Logic
Liability Segregation: Per PRD requirements, liabilities are tracked but strictly isolated from Net Worth calculations.

Dynamic Layout: The TCC generator uses a dynamic bounding-box algorithm to manage variable account counts without compromising visual integrity.
