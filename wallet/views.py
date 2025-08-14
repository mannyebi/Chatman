from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from wallet import services
import logging
from decimal import Decimal
from wallet import serializers
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import status


# Create your views here.

logger = logging.getLogger(__name__)
User_obj = get_user_model()

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
            return Response({"error":"No user found with this username"}, status=status.HTTP_400_BAD_REQUEST)


        #get wallet
        wallet = services.get_wallet_by_user(user=user)
        if not wallet:
                logger.critical(f"A user doens't have any wallet. user:{user}")
                return Response({"error":"No wallet found for this user"}, status=status.HTTP_400_BAD_REQUEST)

        #deposit
        try:
            deposit = services.deposit(wallet=wallet, amount=amount, description=description)
        except Exception as e:
            logger.error(f"an error occured while deposit money to {wallet} -> {e}")
            return Response({"error":"an error occured while depositing money."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({"message":f"Succesfull deposit for {wallet.user.username}. wallet balance : {deposit}"}, status=status.HTTP_200_OK)
    

class TransferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = serializers.TransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        receiver = get_object_or_404(User_obj, username=serializer.validated_data["reciever_username"])
        amount :Decimal = serializer.validated_data['amount']
        description :str = serializer.validated_data['description']

        sender = request.user

        #sender and receiver should not be the same.
        if sender == receiver:
            return Response({"error":"You can not transfer to your self."}, status=status.HTTP_400_BAD_REQUEST)

        #get sender's wallet
        from_wallet = services.get_wallet_by_user(user=sender)
        if not from_wallet:
            logger.error(f"No wallet found for user {sender}")
            return Response({"error":"no wallet found for sender."}, status=status.HTTP_400_BAD_REQUEST)

        #get receievers wallet
        to_wallet = services.get_wallet_by_user(receiver)
        if not to_wallet:
            logger.error(f"No wallet found for user {sender}")
            return Response({"error":"receiver wallet didn't found."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            transfer = services.transfer(wallet=from_wallet, to_wallet=to_wallet, amount=Decimal(amount), description=description)
        #handeling amount validation
        except ValueError as ve:
            return Response({"error":"Insufficient funds."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"an error occured while transfering money -> {e}")
        

        try:
            services.notifiy_transaction_in_ws(receiver=receiver, sender=sender, transfer=transfer)
            print("hi")
        except Exception as e:
            logger.warning(f"WS notify failed: {e}")


        return Response({"message":"Money transferd successfuly."}, status=status.HTTP_200_OK)
        


class CreateDonateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = serializers.DonateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        reciever = request.user
        expiration_minutes = data["expiration_minutes"]
        description = data["description"]

        try:
            donate_link = services.create_donate_link(receiver=reciever, expiration_minutes=expiration_minutes, description=description)
        except Exception as e :
            logger.error(f"an error occured while creating donate link: {e}")
            return Response({"error":"an error occured while creating donate link"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({"message":f"Donate link with id: `{donate_link}` created successfuly"}, status=status.HTTP_201_CREATED)