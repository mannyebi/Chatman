from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from wallet import services
import logging
from decimal import Decimal
# Create your views here.

logger = logging.getLogger(__name__)


class DepositView(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request):
        username = request.data.get("username")
        amount = request.data.get('amount')
        description = request.data.get("description")


        user = services.get_user_by_username(username=username)

        #get wallet
        try:
            wallet = services.get_wallet_by_user(user=user)
        except Exception as e:
            logger.error(f"an error occured while getting wallet by its user -> {e}")

        #show propper error if wallet didn't exists
        if not wallet:
            return Response({"error":"this user does not exists."}, status=404)
        

        #deposit
        try:
            deposit = services.deposit(wallet=wallet, amount=amount, description=description)
        except Exception as e:
            logger.error(f"an error occured while deposit money to {wallet} -> {e}")
            return Response({"error":"an error occured while depositing money."}, status=400)
        
        return Response({"message":f"Succesfull deposit for {wallet.user.username}. wallet balance : {deposit}"}, status=200)
    

class TransferView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        sender = request.user
        reciever_username = request.data.get('reciever_username')
        amount = request.data.get("amount")
        description = request.data.get("description")

        wallet = services.get_wallet_by_user(user=sender)

        reciever_user = services.get_user_by_username(username=reciever_username)
        to_wallet = services.get_wallet_by_user(reciever_user)

        try:
            services.transfer(wallet=wallet, to_wallet=to_wallet, amount=Decimal(amount), description=description)
        except Exception as e:
            logger.error(f"an error occured while transfering money -> {e}")
            return Response({"error":"couldn't transfer money"}, status=400)
        
        return Response({"message":"Money transferd successfuly "})
        