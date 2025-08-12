# payment/urls.py
from django.urls import path
from .views import (
    DashboardView, InitiatePaymentAPI, PaymentSuccessAPI, FileUploadAPI,
    ListFilesAPI, ListActivityAPI, ListTransactionsAPI
)

urlpatterns = [
    # Frontend
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # API Endpoints
    path('api/initiate-payment/', InitiatePaymentAPI.as_view(), name='initiate-payment'),
    # Changed success URL to POST to handle aamarPay's callback
    path('api/payment/success/', PaymentSuccessAPI.as_view(), name='payment-success'),
    path('api/upload/', FileUploadAPI.as_view(), name='file-upload'),
    path('api/files/', ListFilesAPI.as_view(), name='list-files'),
    path('api/activity/', ListActivityAPI.as_view(), name='list-activity'),
    path('api/transactions/', ListTransactionsAPI.as_view(), name='list-transactions'),
]