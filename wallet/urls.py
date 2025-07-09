from django.urls import path
from wallet import views

urlpatterns = [
    path("deposit/", views.DepositView.as_view(), name="depoist"),
    path("transfer/", views.TransferView.as_view(), name="transfer"),
]