from rest_framework import serializers
from wallet.models import Wallet
from decimal import Decimal

class DepositSerializer(serializers.Serializer):
    username = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))
    description = serializers.CharField(required=False, allow_blank=True, default="")



class TransferSerializer(serializers.Serializer):
    reciever_username = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))
    description = serializers.CharField(required=False, allow_blank=True, default="")


class DonateSerializer(serializers.Serializer):
    expiration_minutes = serializers.IntegerField(min_value=1)
    description = serializers.CharField(required=False, allow_blank=True, default="")