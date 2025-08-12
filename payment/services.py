from .mpesa_client import MpesaClient

def release_funds(recipient, amount):
    
    #calling the M-Pesa B2C API.
    print(f"Releasing {amount} to {recipient}")
    return True
