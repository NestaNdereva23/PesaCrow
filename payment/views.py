from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from payment.mpesa_client import MpesaClient
from projects.models import ProjectRequest, Milestone
import logging
from .models import MilestonePayment
import json
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
logger = logging.getLogger(__name__)


''' Handles the payment view when a client clicks on the payment button from the projects view'''
@login_required
def pay_milestone(request, milestone_id):
    milestone = get_object_or_404(Milestone, id=milestone_id)

    # Ensure only the project client can pay
    if request.user.email != milestone.project.sender_email:
        messages.error(request, "You don't have permission to pay for this milestone.")
        return redirect('projects:dashboard')

    # Ensure milestone is in pending status
    if milestone.status != 'Pending':
        messages.error(request, "This milestone is not available for payment.")
        return redirect('projects:project_detail', milestone.project.id)

    context = {
        'milestone': milestone,
    }
    return render(request, 'payment/milestone_payment.html', context)


#TODO Refactor and remove the session implementation
def milestone_payment(request):
    user = request.user
    if user.userprofile.role_type != 'Client':
        return redirect(reverse("home:dashboard"))

    #verify mpesa number exists
    if not user.userprofile.mpesa_number:
        messages.error(request, "Please add your Mpesa number in your profile before making payments.")
        return redirect(reverse("profiles:profile"))

    if request.method == 'POST':
        #GET milestone id from form data
        milestone_id = request.POST.get('milestone_id')
        if not milestone_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Milestone ID is required'
            })
        # get specific milestone to pay
        try:
            # milestone_to_pay = Milestone.objects.get(id=milestone_id)
            milestone_to_pay = get_object_or_404(Milestone, id=milestone_id)
            
            #verify user permissions
            if request.user.email != milestone_to_pay.project.sender_email:
                return JsonResponse({
                    'status': 'error',
                    'message': "you do not have permission to pay for this milestone"
                })
            
            #Ensure the milstone has the correct status payment i.e Pending
            if milestone_to_pay.payment_status not in ['Unpaid', 'Failed', 'Processing']:
                return JsonResponse({
                    'status': 'error',
                    'message': "This milestone is not available for payment"
                })
            
            #check if there already a pending payment
            existing_payment  = MilestonePayment.objects.filter(
                milestone=milestone_to_pay,
                status__in='Pending'
            ).first()

            if existing_payment:
                return JsonResponse({
                    'status': 'success',
                    'message': 'Payment already in progress. Check your phone to complete the payment.',
                    'milestone': milestone_to_pay.id,
                    'checkout_request_id': existing_payment.checkout_request_id,
                })
                
            mpesa_client = MpesaClient()
            
                #clean and get mpesa number
            mpesa_number = clean_mpesa_no(request)
            if not mpesa_number:
                return JsonResponse({
                    'status': 'error',
                    'message': "Invalid Mpesa Number format"
                })
                    
            ''' Initiate the STK Push'''
            mpesa_response = mpesa_client.initiate_stk_push(
            mpesa_number,
            int(milestone_to_pay.payment_amount),
            )
            logger.info(f"Mpesa Response: {mpesa_response}")
                
            if mpesa_response and mpesa_response.get('ResponseCode') == '0':
                #create payment record
                logger.info(f"Mpesa Response full content: {mpesa_response}")
                print(mpesa_response) 

                try:
                    transaction = MilestonePayment.objects.create(
                        milestone=milestone_to_pay,
                        amount=int(milestone_to_pay.payment_amount),
                        checkout_request_id=mpesa_response.get('CheckoutRequestID'),
                        status= 'Pending',
                        mpesa_number=mpesa_number,
                        description=f"Payment for milestone: {milestone_to_pay.title}"
                    )
                        # Update the milestone status
                    milestone_to_pay.payment_status = 'Processing'
                    milestone_to_pay.save()
                        
                    messages.success(request, 
                        f"Payment for milestone '{milestone_to_pay.title} was initiated successfully!'")
                        # return redirect('home:dashboard')
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Check your phone to complete the payment',
                        'milestone': milestone_to_pay.id,
                        'checkout_request_id': mpesa_response.get('CheckoutRequestID'),
                    })
                except IntegrityError as e:
                    # Handle duplicate payment record
                    logger.error(f"Duplicate payment record attempt: {str(e)}")
                    
                    # Check if payment record was created by another request
                    existing_payment = MilestonePayment.objects.filter(
                        milestone=milestone_to_pay,
                        checkout_request_id=mpesa_response.get('CheckoutRequestID')
                    ).first()
                    
                    if existing_payment:
                        return JsonResponse({
                            'status': 'success',
                            'message': 'Payment already initiated. Check your phone to complete the payment.',
                            'milestone': milestone_to_pay.id,
                            'checkout_request_id': existing_payment.checkout_request_id,
                        })
                    else:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Payment record creation failed. Please try again.',
                        })

            else:
                # milestone_to_pay.payment_status = 'Unpaid'
                # milestone_to_pay.status = 'Pending'
                # milestone_to_pay.save()

                return JsonResponse({
                    'status': 'error',
                    'message': 'Mpesa payment failed. Please try again',
                })
        except Milestone.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'The milestone youre trying to pay for does not exist.',
            })

        except Exception as e:
            logger.error(f"Error initating Mpesa STK Push: {str(e)}")
            return JsonResponse({
                    'status': 'error',
                    'message': "An error has occurred. Please try again"
                })
    else:
        #no pending milestones to pay
        messages.info(request, "No pending milestones require payment at this time")
        return redirect('home:dashboard')

def clean_mpesa_no(request):
    user = request.user
    mpesa_number = user.userprofile.mpesa_number
    if not mpesa_number:
        return None
    mpesa_number = ''.join(filter(str.isdigit, mpesa_number))

    if mpesa_number.startswith('0'):
        return '254' + mpesa_number[1:] #conv 07xxxxxxxx to 2547xxxxx
    elif mpesa_number.startswith('254'):
        return  mpesa_number
    elif len(mpesa_number) == 9:
        return '254' + mpesa_number
    else:
        messages.error(request, "The mpesa number you entered is not valid")
        return None


def check_transaction_status(request):
    #Check status of Mpesa transaction
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            checkout_request_id = data.get('checkout_request_id')

            if not checkout_request_id:
                return JsonResponse({'status': 'error', 'message': 'No checkout request_id provided'}, status=400)

            #find payment record
            try:
                payment = MilestonePayment.objects.get(checkout_request_id=checkout_request_id)
                return JsonResponse({
                    'status': 'success',
                    'payment_status': payment.status,
                    'milestone_status': payment.milestone.status,
                    'milestone_payment_status': payment.milestone.payment_status,
                })
            except MilestonePayment.DoesNotExist:
                return JsonResponse({ 'status': 'error', 'message': 'Transaction not found' }, status=404)
        except json.JSONDecodeError:
            return JsonResponse({ 'status': 'error', 'message': 'Invalid JSON data' }, status=400)
        except Exception as e:
            logger.error(f"Error checking transaction status: {str(e)}")
            return JsonResponse({ 'status': 'error', 'message': str(e) }, status=500)

    #handle polling requests
    elif request.method == 'GET':
        checkout_request_id = request.GET.get('checkout_request_id')
        if not checkout_request_id:
            return JsonResponse({'status': 'error', 'message': 'Checkout request is is required'}, status=400)
        try:
            payment = MilestonePayment.objects.get(checkout_request_id=checkout_request_id)
            return JsonResponse({
                'status': 'success',
                'payment_status': payment.status,
                'milestone_status': payment.milestone.status,
                'milestone_payment_status': payment.milestone.payment_status,
            })
        except MilestonePayment.DoesNotExist:
            return JsonResponse({ 'status': 'error', 'message': 'Transaction not found' }, status=404)

    return JsonResponse({'status': 'error', 'message': 'Method not allowed' }, status=405)

@csrf_exempt
def mpesa_callback(request):
    ''' Handle Mpesa payment callback '''
    if request.method == 'POST':
        try:
            callback_data = json.loads(request.body)
            logger.info(f"Received Mpesa callback: {callback_data}")

            result_code = callback_data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
            checkout_request_id = callback_data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')
            metadata_items = callback_data.get('Body', {}).get('stkCallback', {}).get('CallbackMetadata', {}).get('Item', [])

            #extract receipt number and other metadata info
            receipt_number = None
            for item in metadata_items:
                if item.get('Name') == 'MpesaReceiptNumber':
                    receipt_number = item.get('Value')

            #retrieve transaction
            transaction = MilestonePayment.objects.filter(checkout_request_id=checkout_request_id).first()
            print(transaction)
            if not transaction:
                logger.error(f"Transaction with Checkout Request ID '{checkout_request_id}' not found.")
                return JsonResponse({"ResultCode": result_code, "ResultDesc": "Transaction not found"})

            #update transaction and milestone
            if result_code == 0:
                print(result_code)
                transaction.status = 'Complete'
                transaction.receipt_no = receipt_number
                transaction.save()

                if transaction.milestone:
                    milestone = transaction.milestone
                    milestone.payment_status = 'Paid'
                    milestone.status = 'Active'
                    milestone.save()
            else:
                transaction.status = 'Failed'
                transaction.save()

                if transaction.milestone:
                    milestone = transaction.milestone
                    milestone.payment_status = 'Failed'
                    milestone.status = 'Pending'
                    milestone.save()

            return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
        except json.JSONDecodeError:
            logger.error("Invalid JSON in callback data.")
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Invalid JSON"}, status=400)
        except Exception as e:
            logger.error(f"Error processing callback: {str(e)}")
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Internal Server Error"}, status=500)

    return JsonResponse({"ResultCode":1, "ResultDesc":"Invalid Request"}, status=400)





def payment_success(request, milestone_id):
    milestone = get_object_or_404(Milestone, id=milestone_id)
    return render(request, 'projects/payment_success.html', {'milestone': milestone})



