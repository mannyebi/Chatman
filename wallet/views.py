from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from wallet import services
import logging
from decimal import Decimal
from wallet import serializers
# Create your views here.

logger = logging.getLogger(__name__)


class DepositView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = serializers.DepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        username = data["username"]
        amount = data["amount"]
        description = data["description"]

        #get user by its username
        user = services.get_user_by_username(username=username)
        if not user:
            return Response({"error":"No user found with this username"}, status=404)


        #get wallet
        wallet = services.get_wallet_by_user(user=user)
        if not wallet:
                logger.critical(f"A user doens't have any wallet. user:{user}")
                return Response({"error":"No wallet found for this user"}, status=404)

        #deposit
        try:
            deposit = services.deposit(wallet=wallet, amount=amount, description=description)
        except Exception as e:
            logger.error(f"an error occured while deposit money to {wallet} -> {e}")
            return Response({"error":"an error occured while depositing money."}, status=500)
        
        return Response({"message":f"Succesfull deposit for {wallet.user.username}. wallet balance : {deposit}"}, status=200)
    

class TransferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = serializers.TransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        sender = request.user
        reciever_username = data['reciever_username']
        amount = data["amount"]
        description = data["description"]

        #get sender's wallet
        from_wallet = services.get_wallet_by_user(user=sender)
        if not from_wallet:
            logger.error(f"No wallet found for user {sender}")
            return Response({"error":"no wallet found for sender."}, status=404)

        #get reciever user by userna
        reciever_user = services.get_user_by_username(username=reciever_username)
        if not reciever_user:
            return Response({"error":"Receiver not found."}, status=404)


        #get receievers wallet
        to_wallet = services.get_wallet_by_user(reciever_user)
        if not to_wallet:
            logger.error(f"No wallet found for user {sender}")
            return Response({"error":"reciever wallet didn't found."}, status=404)

        try:
            services.transfer(wallet=from_wallet, to_wallet=to_wallet, amount=Decimal(amount), description=description)
        except ValueError as ve:
            return Response({"error":"Insufficient funds."}, status=400)
        except Exception as e:
            logger.error(f"an error occured while transfering money -> {e}")
            return Response({"error":"couldn't transfer money due to a server error."}, status=500)
        
        return Response({"message":"Money transferd successfuly "})
        