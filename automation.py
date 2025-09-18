"""Automation and background task system for GOFAP."""

import schedule
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, Any
from main import app, db
from models import Account, Transaction, PayrollRecord, Budget, UtilityPayment, TransactionStatus, TransactionType
    User, Account, Transaction, PayrollRecord, Budget, UtilityPayment,
    TransactionStatus, TransactionType
)

logger = logging.getLogger(__name__)


class AutomationEngine:
    """Core automation engine for GOFAP."""
    
    def __init__(self):
        self.running = False
        self.scheduler_thread = None
    
    def start(self):
        """Start the automation engine."""
        if self.running:
            logger.warning("Automation engine already running")
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("Automation engine started")
    
    def stop(self):
        """Stop the automation engine."""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        logger.info("Automation engine stopped")
    
    def _run_scheduler(self):
        """Run the scheduler in a background thread."""
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute


class PayrollAutomation:
    """Automated payroll processing system."""
    
    @staticmethod
    def process_scheduled_payroll():
        """Process scheduled payroll payments."""
        with app.app_context():
            try:
                # Get unprocessed payroll records that are due
                due_payroll = PayrollRecord.query.filter(
                    PayrollRecord.processed == False,
                    PayrollRecord.pay_period_end <= datetime.utcnow()
                ).all()
                
                processed_count = 0
                for payroll in due_payroll:
                    try:
                        # Create transaction for payroll
                        transaction = Transaction(
                            transaction_id=f"PAYROLL_{payroll.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                            transaction_type=TransactionType.PAYROLL,
                            status=TransactionStatus.PROCESSING,
                            amount=payroll.net_pay,
                            description=f"Payroll payment for {payroll.pay_period_start} to {payroll.pay_period_end}",
                            user_id=payroll.employee_id
                        )
                        
                        db.session.add(transaction)
                        
                        # Mark payroll as processed
                        payroll.processed = True
                        payroll.processed_at = datetime.utcnow()
                        
                        processed_count += 1
                        
                    except Exception as e:
                        logger.error(f"Failed to process payroll {payroll.id}: {e}")
                
                db.session.commit()
                logger.info(f"Processed {processed_count} payroll payments")
                
            except Exception as e:
                logger.error(f"Payroll automation failed: {e}")
                db.session.rollback()
    
    @staticmethod
    def generate_payroll_reports():
        """Generate automated payroll reports."""
        with app.app_context():
            try:
                # Generate monthly payroll summary
                current_date = datetime.utcnow()
                first_of_month = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                
                monthly_payroll = PayrollRecord.query.filter(
                    PayrollRecord.pay_period_start >= first_of_month,
                    PayrollRecord.processed == True
                ).all()
                
                total_gross = sum(p.gross_pay for p in monthly_payroll)
                total_net = sum(p.net_pay for p in monthly_payroll)
                total_tax = sum(p.tax_withheld for p in monthly_payroll)
                
                report_data = {
                    'period': f"{first_of_month.strftime('%Y-%m')}",
                    'total_employees': len(set(p.employee_id for p in monthly_payroll)),
                    'total_gross_pay': total_gross,
                    'total_net_pay': total_net,
                    'total_tax_withheld': total_tax,
                    'generated_at': current_date.isoformat()
                }
                
                logger.info(f"Generated payroll report: {report_data}")
                return report_data
                
            except Exception as e:
                logger.error(f"Failed to generate payroll report: {e}")


class BudgetMonitoring:
    """Automated budget monitoring and alerts."""
    
    @staticmethod
    def check_budget_utilization():
        """Check budget utilization and send alerts."""
        with app.app_context():
            try:
                budgets = Budget.query.filter_by(is_active=True).all()
                alerts = []
                
                for budget in budgets:
                    utilization = (budget.spent_amount / budget.allocated_amount) * 100 if budget.allocated_amount > 0 else 0
                    
                    # Alert thresholds
                    if utilization >= 90:
                        alert_level = "CRITICAL"
                    elif utilization >= 75:
                        alert_level = "WARNING"
                    elif utilization >= 50:
                        alert_level = "INFO"
                    else:
                        continue  # No alert needed
                    
                    alert = {
                        'budget_id': budget.id,
                        'budget_name': budget.name,
                        'department': budget.department,
                        'utilization_percentage': round(utilization, 2),
                        'allocated_amount': budget.allocated_amount,
                        'spent_amount': budget.spent_amount,
                        'remaining_amount': budget.allocated_amount - budget.spent_amount,
                        'alert_level': alert_level,
                        'generated_at': datetime.utcnow().isoformat()
                    }
                    
                    alerts.append(alert)
                    logger.warning(f"Budget alert: {budget.name} at {utilization:.1f}% utilization")
                
                return alerts
                
            except Exception as e:
                logger.error(f"Budget monitoring failed: {e}")
                return []
    
    @staticmethod
    def update_budget_spending():
        """Update budget spending based on recent transactions."""
        with app.app_context():
            try:
                # Update budget spending based on completed transactions
                # This is a simplified example - in reality, you'd have more sophisticated mapping
                budgets = Budget.query.filter_by(is_active=True).all()
                
                for budget in budgets:
                    # Get transactions for this department (simplified logic)
                    department_transactions = Transaction.query.filter(
                        Transaction.status == TransactionStatus.COMPLETED,
                        Transaction.description.contains(budget.department)
                    ).all()
                    
                    total_spending = sum(t.amount for t in department_transactions)
                    budget.spent_amount = total_spending
                
                db.session.commit()
                logger.info("Updated budget spending from transactions")
                
            except Exception as e:
                logger.error(f"Failed to update budget spending: {e}")
                db.session.rollback()


class UtilityPaymentAutomation:
    """Automated utility payment processing."""
    
    @staticmethod
    def process_overdue_notices():
        """Process overdue utility payment notices."""
        with app.app_context():
            try:
                overdue_payments = UtilityPayment.query.filter(
                    UtilityPayment.is_paid == False,
                    UtilityPayment.due_date < datetime.utcnow()
                ).all()
                
                notices = []
                for payment in overdue_payments:
                    days_overdue = (datetime.utcnow() - payment.due_date).days
                    
                    notice = {
                        'payment_id': payment.id,
                        'citizen_id': payment.citizen_id,
                        'utility_type': payment.utility_type,
                        'account_number': payment.account_number,
                        'amount_due': payment.amount_due,
                        'due_date': payment.due_date.isoformat(),
                        'days_overdue': days_overdue,
                        'notice_generated_at': datetime.utcnow().isoformat()
                    }
                    
                    notices.append(notice)
                
                logger.info(f"Generated {len(notices)} overdue payment notices")
                return notices
                
            except Exception as e:
                logger.error(f"Failed to process overdue notices: {e}")
                return []
    
    @staticmethod
    def auto_pay_recurring_utilities():
        """Process automatic recurring utility payments."""
        with app.app_context():
            try:
                # Find utility payments due for auto-pay (simplified logic)
                due_payments = UtilityPayment.query.filter(
                    UtilityPayment.is_paid == False,
                    UtilityPayment.due_date <= datetime.utcnow() + timedelta(days=1)
                ).all()
                
                processed_count = 0
                for payment in due_payments:
                    # Create transaction for auto-payment
                    transaction = Transaction(
                        transaction_id=f"UTILITY_AUTO_{payment.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                        transaction_type=TransactionType.UTILITY_PAYMENT,
                        status=TransactionStatus.PROCESSING,
                        amount=payment.amount_due,
                        description=f"Auto-pay {payment.utility_type} bill - {payment.account_number}",
                        user_id=payment.citizen_id
                    )
                    
                    db.session.add(transaction)
                    
                    # Mark payment as paid
                    payment.is_paid = True
                    payment.amount_paid = payment.amount_due
                    payment.paid_date = datetime.utcnow()
                    
                    processed_count += 1
                
                db.session.commit()
                logger.info(f"Processed {processed_count} automatic utility payments")
                
            except Exception as e:
                logger.error(f"Auto-pay processing failed: {e}")
                db.session.rollback()


class ReportingAutomation:
    """Automated reporting system."""
    
    @staticmethod
    def generate_daily_financial_report():
        """Generate daily financial summary report."""
        with app.app_context():
            try:
                today = datetime.utcnow().date()
                
                # Get today's transactions
                today_transactions = Transaction.query.filter(
                    Transaction.created_at >= datetime.combine(today, datetime.min.time()),
                    Transaction.created_at < datetime.combine(today + timedelta(days=1), datetime.min.time())
                ).all()
                
                # Calculate totals by type
                totals_by_type = {}
                for transaction in today_transactions:
                    tx_type = transaction.transaction_type.value
                    if tx_type not in totals_by_type:
                        totals_by_type[tx_type] = {'count': 0, 'amount': 0}
                    totals_by_type[tx_type]['count'] += 1
                    totals_by_type[tx_type]['amount'] += transaction.amount
                
                report = {
                    'date': today.isoformat(),
                    'total_transactions': len(today_transactions),
                    'total_amount': sum(t.amount for t in today_transactions),
                    'transactions_by_type': totals_by_type,
                    'generated_at': datetime.utcnow().isoformat()
                }
                
                logger.info(f"Generated daily financial report: {report['total_transactions']} transactions, ${report['total_amount']:.2f}")
                return report
                
            except Exception as e:
                logger.error(f"Failed to generate daily financial report: {e}")
                return None


# Schedule automation tasks
def setup_automation_schedules():
    """Set up all automation schedules."""
    # Payroll automation
    schedule.every().monday.at("08:00").do(PayrollAutomation.process_scheduled_payroll)
    schedule.every().day.at("23:00").do(PayrollAutomation.generate_payroll_reports)
    
    # Budget monitoring
    schedule.every().day.at("06:00").do(BudgetMonitoring.check_budget_utilization)
    schedule.every().hour.do(BudgetMonitoring.update_budget_spending)
    
    # Utility payment automation
    schedule.every().day.at("07:00").do(UtilityPaymentAutomation.process_overdue_notices)
    schedule.every().day.at("09:00").do(UtilityPaymentAutomation.auto_pay_recurring_utilities)
    
    # Reporting automation
    schedule.every().day.at("23:30").do(ReportingAutomation.generate_daily_financial_report)
    
    logger.info("Automation schedules configured")


# Global automation engine instance
automation_engine = AutomationEngine()


def start_automation():
    """Start all automation systems."""
    setup_automation_schedules()
    automation_engine.start()


def stop_automation():
    """Stop all automation systems."""
    automation_engine.stop()