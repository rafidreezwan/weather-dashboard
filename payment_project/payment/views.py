from django.shortcuts import render

# Create your views here.
# payment/views.py
import uuid
import requests
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import PaymentTransaction, ActivityLog, FileUpload
from .serializers import PaymentTransactionSerializer, ActivityLogSerializer, FileUploadSerializer
from .tasks import count_words_in_file

# --- aamarPay Sandbox Details ---
AAMARPAY_STORE_ID = "aamarpaytest"
AAMARPAY_SIGNATURE_KEY = "dbb74894e82415a2f7ff0ec3a97e4183"
AAMARPAY_API_URL = "https://sandbox.aamarpay.com/jsonpost.php"

def get_user_payment_status(user):
    """Checks if a user has at least one successful payment."""
    return PaymentTransaction.objects.filter(user=user, status='success').exists()

# --- Dashboard View ---
class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        user_has_paid = get_user_payment_status(request.user)
        files = FileUpload.objects.filter(user=request.user).order_by('-upload_time')
        activities = ActivityLog.objects.filter(user=request.user).order_by('-timestamp')
        transactions = PaymentTransaction.objects.filter(user=request.user).order_by('-timestamp')

        context = {
            'user_has_paid': user_has_paid,
            'files': files,
            'activities': activities,
            'transactions': transactions,
        }
        return render(request, 'dashboard.html', context)

# --- API Views ---
class InitiatePaymentAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        transaction_id = f"{user.id}-{uuid.uuid4()}"
        amount = "100.00"

        payload = {
            "store_id": AAMARPAY_STORE_ID,
            "signature_key": AAMARPAY_SIGNATURE_KEY,
            "cus_name": user.username,
            "cus_email": user.email or 'test@example.com',
            "cus_phone": "01234567890",
            "amount": amount,
            "currency": "BDT",
            "tran_id": transaction_id,
            "success_url": request.build_absolute_uri('/api/payment/success/'),
            "fail_url": request.build_absolute_uri('/dashboard/'), # Redirect to dashboard on fail
            "cancel_url": request.build_absolute_uri('/dashboard/'), # Redirect to dashboard on cancel
            "desc": "Payment for File Upload",
            "type": "json"
        }

        PaymentTransaction.objects.create(
            user=user,
            transaction_id=transaction_id,
            amount=float(amount),
            status='pending'
        )

        ActivityLog.objects.create(
            user=user,
            action='Payment Initiated',
            metadata={'transaction_id': transaction_id, 'amount': amount}
        )

        try:
            response = requests.post(AAMARPAY_API_URL, json=payload)
            response_data = response.json()

            if response_data.get("result") == "true" and response_data.get("payment_url"):
                return Response({"payment_url": response_data["payment_url"]}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Failed to initiate payment", "details": response_data}, status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException as e:
            return Response({"error": f"Request failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentSuccessAPI(APIView):
    def post(self, request): # aamarPay sends POST
        data = request.data
        tran_id = data.get('mer_txnid')

        try:
            transaction = PaymentTransaction.objects.get(transaction_id=tran_id)
            transaction.status = 'success'
            transaction.gateway_response = data
            transaction.save()

            ActivityLog.objects.create(
                user=transaction.user,
                action='Payment Successful',
                metadata={'transaction_id': tran_id}
            )
            # Redirect to the dashboard after success
            return redirect('dashboard')
        except PaymentTransaction.DoesNotExist:
            # Log this strange event
            return redirect('dashboard') # Redirect anyway

class FileUploadAPI(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        if not get_user_payment_status(request.user):
            return Response({'error': 'Payment required before uploading.'}, status=status.HTTP_403_FORBIDDEN)

        file_obj = request.data.get('file')
        if not file_obj:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        ext = file_obj.name.split('.')[-1].lower()
        if ext not in ['txt', 'docx']:
            return Response({'error': 'Only .txt and .docx files are allowed.'}, status=status.HTTP_400_BAD_REQUEST)

        file_upload = FileUpload.objects.create(
            user=request.user,
            file=file_obj,
            filename=file_obj.name,
        )

        ActivityLog.objects.create(
            user=request.user,
            action='File Uploaded',
            metadata={'file_id': file_upload.id, 'filename': file_upload.filename}
        )

        # Trigger Celery task
        count_words_in_file.delay(file_upload.id)

        return Response(FileUploadSerializer(file_upload).data, status=status.HTTP_201_CREATED)

# --- Listing APIs ---
class ListFilesAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        files = FileUpload.objects.filter(user=request.user)
        serializer = FileUploadSerializer(files, many=True)
        return Response(serializer.data)

class ListActivityAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        activities = ActivityLog.objects.filter(user=request.user)
        serializer = ActivityLogSerializer(activities, many=True)
        return Response(serializer.data)

class ListTransactionsAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        transactions = PaymentTransaction.objects.filter(user=request.user)
        serializer = PaymentTransactionSerializer(transactions, many=True)
        return Response(serializer.data)