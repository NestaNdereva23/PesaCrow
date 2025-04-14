from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from payment.mpesa_client import MpesaClient
from projects.models import ProjectRequest, Milestone
import logging
from .models import MilestonePayment
import json
logger = logging.getLogger(__name__)


def milestone_payment(request):
    user = request.user
    if user.userprofile.role_type != 'Client':
        return redirect(reverse("home:dashboard"))

    #verify mpesa number exists
    if not user.userprofile.mpesa_number:
        messages.error(request, "Please add your Mpesa number in your profile before making payments.")
        return redirect(reverse("profiles:profile"))

    project_requests = ProjectRequest.objects.filter(sender_email=request.user.email, verified=True)
    context = {}
    # get the pending milestone id from session
    pending_milestone_id = request.session.get('pending_milestone_id')
    if not pending_milestone_id:
        # if no pending milestone id in session find one
        projects = ProjectRequest.objects.filter(sender_email=request.user.email, verified=True)
        for project in projects:
            # check for pending miestone
            pending_milestone = Milestone.objects.filter(
                project=project,
                status='Pending',
                payment_status='Unpaid'
            ).order_by('order_number').first()

            if pending_milestone:
                # store the milestone id session for use in payment view
                pending_milestone_id = pending_milestone.id
                break

    if pending_milestone_id:
        # get specific milestone to pay
        try:
            milestone_to_pay = Milestone.objects.get(id=pending_milestone_id)
            project = milestone_to_pay.project

            if request.method == 'POST':
                '''
                    Process payment
                '''
                
                mpesa_client = MpesaClient()
                #get specific milestone to pay
                try:
                    #clean and get mpesa number
                    
                    mpesa_number = clean_mpesa_no(request)
                    print(mpesa_number)
                    if not mpesa_number:
                        messages.error(request, "Invalid Mpesa Number format")
                        context = {"project": project, "milestone": milestone_to_pay}
                        return render(request, "payment/milestone_payment.html", context)

                    mpesa_response = mpesa_client.initiate_stk_push(
                    clean_mpesa_no(request),
                    int(milestone_to_pay.payment_amount),
                    )
                    logger.info(f"Mpesa Response: {mpesa_response}")
                    
                    if mpesa_response and mpesa_response.get('ResponseCode') == '0':
                        #create payment record
                        logger.info(f"Mpesa Response full content: {mpesa_response}")
                        print(mpesa_response)

                        
 
                        transaction = MilestonePayment.objects.create(
                            milestone=milestone_to_pay,
                            amount=int(milestone_to_pay.payment_amount),
                            checkout_request_id=mpesa_response.get('CheckoutRequestID'),
                            status= 'Pending',
                            mpesa_number=mpesa_number,
                            description=f"Payment for milestone: {milestone_to_pay.title}"
                        )
                        # transaction.save()
                        milestone_to_pay.payment_status = 'Processing'
                        milestone_to_pay.save()
                        
                        # clear the session variable
                        if 'pending_milestone_id' in request.session:
                            del request.session['pending_milestone_id']

                        messages.success(request, f"Payment for milestone '{milestone_to_pay.title} was successfull!'")
                        # return redirect('home:dashboard')
                        return JsonResponse({
                            'status': 'Success',
                            'message': 'Check your phone to complete the payment',
                            'milestone': milestone_to_pay.id,
                            'checkout_request_id': mpesa_response.get('CheckoutRequestID'),
                        })
                    else:
                        milestone_to_pay.payment_status = 'Unpaid'
                        milestone_to_pay.status = 'Pending'
                        milestone_to_pay.save()
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Mpesa payment failed',
                        })
                except Exception as e:
                    logger.error(f"Error initating Mpesa STKS Push: {str(e)}")
                    milestone_to_pay.payment_status = 'Unpaid'
                    milestone_to_pay.status = 'Pending'
                    milestone_to_pay.save()
                    return JsonResponse({
                        'status': 'error',
                        'message': 'An error has occurred. Please try again.',
                    })

            context = {
                "project": project,
                "milestone": milestone_to_pay
            }

        except Milestone.DoesNotExist:
            messages.error(request, "The milestone youre trying to pay for does not exist")
            return redirect('home:dashboard')
    else:
        #no pending milestones to pay
        messages.info(request, "No pending milestones require payment at this time")
        return redirect('home:dashboard')

    return render(request, 'payment/milestone_payment.html', context)

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

def mpesa_callback(request):
    '''
    Handle Mpesa payment callback
    '''
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
            transaction = MilestonePayment.objects.filter(checkout_request_id=checkout_request_id).order_by('order_number').first()
            if not transaction:
                logger.error(f"Transaction with Checkout Request ID '{checkout_request_id}' not found.")
                return JsonResponse({"ResultCode": result_code, "ResultDesc": "Transaction not found"})

            #update transaction and milestone
            if result_code == 0:
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

