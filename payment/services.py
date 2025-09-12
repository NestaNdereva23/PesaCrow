from .mpesa_client import MpesaClient
from projects.models import Milestone
from django.db.models import Sum
from .models import MilestonePayment

def release_funds(milestone: Milestone):
    """
    Simulates the release of funds for a milestone.
    """
    try:
        # Get the latest milestone payment
        milestone_payment = milestone.latest_payment
        if not milestone_payment or milestone_payment.status != "Complete":
            # Handle case where payment is not complete
            return False, "Payment not complete"

        # Update milestone payment status to "Released"
        milestone_payment.status = "Released"
        milestone_payment.save()

        # Update milestone status to "Completed"
        milestone.status = "Completed"
        milestone.save()

        return True, "Funds released successfully"
    except Exception as e:
        return False, str(e)

def get_escrow_balance():
    """
    Calculates the total amount of money currently held in escrow.
    Escrow is defined as the sum of all MilestonePayments with a 'Complete' status.
    """
    total_escrow = MilestonePayment.objects.filter(status='Complete').aggregate(total=Sum('amount'))['total']
    return total_escrow or 0.00
