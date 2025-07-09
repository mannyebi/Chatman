from wallet.models import Wallet, Transaction
from decimal import Decimal
from django.db import transaction
import logging
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()

@transaction.atomic
def deposit(wallet: Wallet, amount: Decimal, description: str= ""):
    """deposit money to a wallet.
    """
    try:
        wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)
        wallet.balance += Decimal(amount)
        wallet.save()
        logger.info(f"wallet: {wallet}, deposit {amount}, Saved")
        Transaction.objects.create(wallet=wallet, amount=amount, description=description, type="deposit")
    except Exception as e:
        logger.error(f"an error occured while deposit moeny for {wallet} -> {e}")
        raise
    return wallet.balance


@transaction.atomic
def transfer(wallet:Wallet, to_wallet:Wallet, amount: Decimal, description: str=""):
    """Transfer money between to wallets.
    """
    try:
        from_wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)
        to_wallet = Wallet.objects.select_for_update().get(pk=to_wallet.pk)

        if from_wallet.balance < amount:
            raise ValueError("Insufficient funds.")

        from_wallet.balance -= amount
        to_wallet.balance += amount

        from_wallet.save()
        to_wallet.save()

        Transaction.objects.create(wallet=from_wallet, to_wallet=to_wallet, type="transfer", amount=amount, description=description)
    except Exception as e:
        logger.error(f"an error occured while transfering from {wallet} to {to_wallet} -> {e}")
        raise


def get_user_by_username(username):
    return User.objects.filter(username=username).first()


def get_wallet_by_user(user):
    """return a wallet instance by username
    """
    try:
        wallet = Wallet.objects.filter(user=user).first()
        return wallet if wallet else None
    except Exception as e:
        logger.error(f"an error occured while getting wallet by its user -> {e}")
        raise