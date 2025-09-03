from django.urls import path
from wallet import views

urlpatterns = [
    path("deposit/", views.DepositView.as_view(), name="depoist"),
    path("transfer/", views.TransferView.as_view(), name="transfer"),
    path("create-donate-link/", views.CreateDonateView.as_view(), name="create-donate-link"),
    path("fetch-balance/", views.FetchUserBalance.as_view(), name="fetch-balance"),

]