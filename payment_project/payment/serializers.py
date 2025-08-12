# payment/serializers.py
from rest_framework import serializers
from .models import FileUpload, PaymentTransaction, ActivityLog

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ['id', 'filename', 'upload_time', 'status', 'word_count']

class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = ['transaction_id', 'amount', 'status', 'timestamp']

class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ['action', 'metadata', 'timestamp']