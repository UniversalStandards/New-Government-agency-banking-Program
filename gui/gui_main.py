"""Enhanced GUI interface for GOFAP using tkinter."""

import logging
import os
import tkinter as tk
from tkinter import ttk

import requests  # This line can be removed if not used

# Try to import the newer async helpers first, fall back to compatibility mode
try:
    from gui_helpers import create_accounts  # Removed create_accounts_async from import

    HAS_ASYNC_HELPERS = True
except ImportError:
    # Fallback to simple synchronous functions for main branch compatibility
    HAS_ASYNC_HELPERS = False

    def create_accounts(service, api_key=None):
        """Simple fallback account creation function for compatibility."""
        logging.info(f"Creating {service} account (compatibility mode)")
        return f"mock_{service}_account"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API keys from environment
stripe_api_key = os.environ.get("STRIPE_SECRET_KEY", "")
modern_treasury_api_key = os.environ.get("MODERN_TREASURY_API_KEY", "")
from gui_helpers import create_accounts

from configs.settings import MODERN_TREASURY_API_KEY, STRIPE_SECRET_KEY

class AccountCreationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Account Creation GUI - GOFAP Platform")

        self.tab_control = ttk.Notebook(root)

        # Modern Treasury Tab
        self.modern_treasury_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.modern_treasury_tab, text="Modern Treasury")

        # Stripe Tab
        self.stripe_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.stripe_tab, text="Stripe")

        self.tab_control.pack(expand=1, fill="both")

class GOFAPDashboard:
    """Main dashboard for GOFAP GUI interface."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(
            "GOFAP - Government Operations and Financial Accounting Platform"
        )
        self.root.geometry("1200x800")

        # API base URL (can be configured)
        self.api_base = "http://127.0.0.1:5000/api"

        self.setup_ui()

    def setup_ui(self):
        """Set up the main user interface."""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Create sidebar
        self.create_sidebar(main_frame)

        # Create main content area
        self.content_frame = ttk.Frame(main_frame, padding="10")
        self.content_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)

        # Show dashboard by default
        self.show_dashboard()

    def create_sidebar(self, parent):
        """Create the sidebar navigation."""
        sidebar = ttk.Frame(parent, width=200)
        sidebar.grid(row=0, column=0, sticky=(tk.W, tk.N, tk.S), padx=(0, 10))
        sidebar.grid_propagate(False)

        # Logo/Title
        title_label = ttk.Label(sidebar, text="GOFAP", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 20), sticky=tk.W)

        # Navigation buttons
        nav_buttons = [
            ("Dashboard", self.show_dashboard),
            ("Users", self.show_users),
            ("Accounts", self.show_accounts),
            ("Transactions", self.show_transactions),
            ("Payroll", self.show_payroll),
            ("Budget", self.show_budget),
            ("Utilities", self.show_utilities),
            ("Reports", self.show_reports),
        ]

        for i, (text, command) in enumerate(nav_buttons):
            btn = ttk.Button(sidebar, text=text, command=command, width=20)
            btn.grid(row=i + 1, column=0, pady=2, sticky=(tk.W, tk.E))

        # Status label
        self.status_label = ttk.Label(sidebar, text="Ready", foreground="green")
        self.status_label.grid(
            row=len(nav_buttons) + 2, column=0, pady=(20, 0), sticky=tk.W
        )

    def clear_content(self):
        """Clear the content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        """Show the main dashboard."""
        self.clear_content()

        # Dashboard title
        title = ttk.Label(
            self.content_frame, text="GOFAP Dashboard", font=("Arial", 20, "bold")
        )
        title.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky=tk.W)

        # Welcome message
        welcome = ttk.Label(
            self.content_frame,
            text="Welcome to the Government Operations and Financial Accounting Platform",
            font=("Arial", 12),
        )
        welcome.grid(row=1, column=0, columnspan=2, pady=(0, 30), sticky=tk.W)

        # Features overview
        features_frame = ttk.LabelFrame(
            self.content_frame, text="Key Features", padding="10"
        )
        features_frame.grid(
            row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20)
        )

        features = [
            "💳 Digital Account & Card Management",
            "💰 Payment Processing & Treasury Management",
            "👥 HR & Payroll Management",
            "👤 Constituent Services",
            "📊 Budgeting & Financial Analytics",
            "🔄 Automated Background Processing",
            "📈 Real-time Reporting & Dashboards",
        ]

        for i, feature in enumerate(features):
            ttk.Label(features_frame, text=feature, font=("Arial", 10)).grid(
                row=i // 2, column=i % 2, sticky=tk.W, padx=(0, 20), pady=2
            )

    def show_users(self):
        """Show user management interface."""
        self.clear_content()

        title = ttk.Label(
            self.content_frame, text="User Management", font=("Arial", 16, "bold")
        )
        title.grid(row=0, column=0, pady=(0, 20), sticky=tk.W)

        info = ttk.Label(
            self.content_frame, text="Manage system users, employees, and citizens"
        )
        info.grid(row=1, column=0, pady=(0, 20), sticky=tk.W)

    def show_accounts(self):
        """Show account management interface."""
        self.clear_content()

        title = ttk.Label(
            self.content_frame, text="Account Management", font=("Arial", 16, "bold")
        )
        title.grid(row=0, column=0, pady=(0, 20), sticky=tk.W)

        info = ttk.Label(
            self.content_frame,
            text="Create and manage bank accounts and digital wallets",
        )
        info.grid(row=1, column=0, pady=(0, 20), sticky=tk.W)

    def show_transactions(self):
        """Show transaction management interface."""
        self.clear_content()

        title = ttk.Label(
            self.content_frame, text="Transaction History", font=("Arial", 16, "bold")
        )
        title.grid(row=0, column=0, pady=(0, 20), sticky=tk.W)

        info = ttk.Label(
            self.content_frame, text="View and manage all financial transactions"
        )
        info.grid(row=1, column=0, pady=(0, 20), sticky=tk.W)

    def show_payroll(self):
        """Show payroll management interface."""
        self.clear_content()

        title = ttk.Label(
            self.content_frame, text="Payroll Management", font=("Arial", 16, "bold")
        )
        title.grid(row=0, column=0, pady=(0, 20), sticky=tk.W)

        info = ttk.Label(
            self.content_frame, text="Process payroll and manage employee payments"
        )
        info.grid(row=1, column=0, pady=(0, 20), sticky=tk.W)

    def show_budget(self):
        """Show budget management interface."""
        self.clear_content()

        title = ttk.Label(
            self.content_frame, text="Budget Overview", font=("Arial", 16, "bold")
        )
        title.grid(row=0, column=0, pady=(0, 20), sticky=tk.W)

        info = ttk.Label(
            self.content_frame, text="Monitor departmental budgets and spending"
        )
        info.grid(row=1, column=0, pady=(0, 20), sticky=tk.W)

    def show_utilities(self):
        """Show utility payment interface."""
        self.clear_content()

        title = ttk.Label(
            self.content_frame, text="Utility Payments", font=("Arial", 16, "bold")
        )
        title.grid(row=0, column=0, pady=(0, 20), sticky=tk.W)

        info = ttk.Label(
            self.content_frame, text="Process citizen utility payments and services"
        )
        info.grid(row=1, column=0, pady=(0, 20), sticky=tk.W)

    def show_reports(self):
        """Show reports interface."""
        self.clear_content()

        title = ttk.Label(
            self.content_frame, text="Reports & Analytics", font=("Arial", 16, "bold")
        )
        title.grid(row=0, column=0, pady=(0, 20), sticky=tk.W)

        info = ttk.Label(
            self.content_frame, text="Generate comprehensive financial reports"
        )
        info.grid(row=1, column=0, pady=(0, 20), sticky=tk.W)

    def run(self):
        """Start the GUI application."""
        self.root.mainloop()

def main():
    """Main entry point for GUI application."""
    app = GOFAPDashboard()
    app.run()

if __name__ == "__main__":
    main()

    def create_modern_treasury_widgets(self):
        # Widgets for Modern Treasury tab
        ttk.Label(
            self.modern_treasury_tab, text="Modern Treasury Account Creation"
        ).grid(column=0, row=0, pady=10)
        ttk.Button(
            self.modern_treasury_tab,
            text="Create Account",
            command=self.create_modern_treasury_account,
        ).grid(column=0, row=1, pady=5)

        # Status label for feedback
        self.mt_status = ttk.Label(self.modern_treasury_tab, text="")
        self.mt_status.grid(column=0, row=2, pady=5)

    def create_stripe_widgets(self):
        # Widgets for Stripe tab
        ttk.Label(self.stripe_tab, text="Stripe Customer Creation").grid(
            column=0, row=0, pady=10
        )

        ttk.Button(
            self.stripe_tab, text="Create Customer", command=self.create_stripe_customer
        ).grid(column=0, row=1, pady=5)

        # Status label for feedback
        self.stripe_status = ttk.Label(self.stripe_tab, text="")
        self.stripe_status.grid(column=0, row=2, pady=5)

    def create_modern_treasury_account(self):
        """Call the function to create a Modern Treasury account."""
        try:
            self.mt_status.config(text="Creating account...")
            self.root.update()

            result = create_accounts("modern_treasury", api_key=modern_treasury_api_key)
            if result:
                self.mt_status.config(text=f"Account created: {result}")
                logger.info(f"Modern Treasury account created: {result}")
            else:
                self.mt_status.config(text="Failed to create account")
                logger.error("Failed to create Modern Treasury account")
        except Exception as e:
            self.mt_status.config(text=f"Error: {str(e)}")
            logger.error(f"Error creating Modern Treasury account: {e}")

    def create_stripe_customer(self):
        """Call the function to create a Stripe customer."""
        try:
            self.stripe_status.config(text="Creating customer...")
            self.root.update()

            result = create_accounts("stripe", api_key=stripe_api_key)
            if result:
                self.stripe_status.config(text=f"Customer created: {result}")
                logger.info(f"Stripe customer created: {result}")
            else:
                self.stripe_status.config(text="Failed to create customer")
                logger.error("Failed to create Stripe customer")
        except Exception as e:
            self.stripe_status.config(text=f"Error: {str(e)}")
            logger.error(f"Error creating Stripe customer: {e}")
        create_accounts("modern_treasury", api_key=MODERN_TREASURY_API_KEY)

    def create_stripe_customer(self):
        # Call the function to create a Stripe customer
        create_accounts("stripe", api_key=STRIPE_SECRET_KEY, params={})

if __name__ == "__main__":
    root = tk.Tk()
    app = AccountCreationGUI(root)
    root.mainloop()
