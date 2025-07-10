from wallet.models import Wallet, Transaction, DonateLink
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
        wallet.balance += amount
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
    """return user instance by its username
    """
    try:
        return User.objects.filter(username=username).first()
    except Exception as e:
        logger.error(f"an error occured while getting user by username -> {e}")
        raise


def get_wallet_by_user(user):
    """return a wallet instance by user's username.
    """
    try:
        return Wallet.objects.filter(user=user).first()
    except Exception as e:
        logger.error(f"an error occured while getting wallet by its user -> {e}")
        raise


def create_donate_link(receiver, expiration_minutes, description=""):
    """create a donate link
    """
    try:
        donate_link = DonateLink.objects.create(receiver=receiver, expiration_minutes=expiration_minutes, description=description)
    except Exception as e:
        logger.error(f"an error occured while creating donate link: {e}")
        raise
    return donate_link.id