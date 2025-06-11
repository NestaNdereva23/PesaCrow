let isPaymentInProgress = false;

function initiatePayment() {
    // Prevent form submission
    event.preventDefault();
    
    // Prevent double submission
    if (isPaymentInProgress) {
        return false;
    }
    
    isPaymentInProgress = true;
    
    // Show loading indicator
    document.getElementById('payment-button').disabled = true;
    document.getElementById('payment-button').textContent = 'Processing...';
    document.getElementById('payment-status').textContent = 'Processing payment...';
    
    // Submit the form via AJAX
    const form = document.getElementById('payment-form');
    const formData = new FormData(form);
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Start polling for status updates
            document.getElementById('payment-status').textContent = 'Payment initiated. Check your phone to complete.';
            pollTransactionStatus(data.checkout_request_id);
        } else {
            document.getElementById('payment-status').textContent = 'Error: ' + data.message;
            resetButton();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('payment-status').textContent = 'An error occurred. Please try again.';
        resetButton();
    });
    
    return false; // Prevent form submission
}

function pollTransactionStatus(checkoutRequestId) {
    let pollCount = 0;
    const maxPolls = 24; // Poll for up to 2 minutes (24 * 5 seconds)
    
    // Poll every 5 seconds
    const statusInterval = setInterval(() => {
        fetch(`/payment/check-transaction-status/?checkout_request_id=${checkoutRequestId}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                if (data.payment_status === 'Complete') {
                    clearInterval(statusInterval);
                    document.getElementById('payment-status').textContent = 'Payment successful! Redirecting...';
                    // Redirect to dashboard after 2 seconds
                    setTimeout(() => {
                        window.location.href = '/dashboard/'; // Use absolute URL instead of template tag
                    }, 2000);
                } else if (data.payment_status === 'Failed') {
                    clearInterval(statusInterval);
                    document.getElementById('payment-status').textContent = 'Payment failed. Please try again.';
                    resetButton();
                } else {
                    // Continue polling if status is still 'Pending'
                    document.getElementById('payment-status').textContent = 'Waiting for payment confirmation...';
                }
            } else {
                document.getElementById('payment-status').textContent = data.message;
            }
            
            pollCount++;
            if (pollCount >= maxPolls) {
                clearInterval(statusInterval);
                document.getElementById('payment-status').textContent = 'Payment status check timed out. Please check your dashboard.';
                resetButton();
            }
        })
        .catch(error => {
            console.error('Error checking status:', error);
            pollCount++;
            if (pollCount >= maxPolls) {
                clearInterval(statusInterval);
                document.getElementById('payment-status').textContent = 'Payment status unknown. Please check your dashboard.';
                resetButton();
            }
        });
    }, 5000);
}

function resetButton() {
    const button = document.getElementById('payment-button');
    button.disabled = false;
    button.textContent = 'Pay with M-Pesa';
    isPaymentInProgress = false; // Reset the flag
}