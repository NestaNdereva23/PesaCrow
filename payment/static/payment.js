
function initiatePayment() {
    // Show loading indicator
    document.getElementById('payment-button').disabled = true;
    document.getElementById('payment-status').textContent = 'Processing payment...';

    // Submit the form via AJAX
    const form = document.getElementById('payment-form');
    const formData = new FormData(form);

    fetch(form.action, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Start polling for status updates
            document.getElementById('payment-status').textContent = 'Payment initiated. Check your phone to complete.';
            pollTransactionStatus(data.checkout_request_id);
        } else {
            document.getElementById('payment-status').textContent = data.message;
            document.getElementById('payment-button').disabled = false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('payment-status').textContent = 'An error occurred. Please try again.';
        document.getElementById('payment-button').disabled = false;
    });

    return false; // Prevent form submission
}

function pollTransactionStatus(checkoutRequestId) {
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
                        window.location.href = '/dashboard/';
                    }, 2000);
                } else if (data.payment_status === 'Failed') {
                    clearInterval(statusInterval);
                    document.getElementById('payment-status').textContent = 'Payment failed. Please try again.';
                    document.getElementById('payment-button').disabled = false;
                }
                // Continue polling if status is still 'Pending'
            } else {
                document.getElementById('payment-status').textContent = data.message;
            }
        })
        .catch(error => {
            console.error('Error checking status:', error);
        });
    }, 5000);

    // Stop polling after 2 minutes (assuming transaction should complete by then)
    setTimeout(() => {
        clearInterval(statusInterval);
        document.getElementById('payment-status').textContent = 'Payment status unknown. Please check your dashboard.';
        document.getElementById('payment-button').disabled = false;
    }, 120000);
}