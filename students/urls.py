from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register_student, name="register_student"),
    path(
        "registration-success/",
        views.registration_success,
        name="registration_success"
    ),

    path("login/", views.student_login, name="student_login"),
    path("dashboard/", views.student_dashboard, name="student_dashboard"),
    path("logout/", views.student_logout, name="student_logout"),

    path(
        "transaction/",
        views.wallet_transaction,
        name="wallet_transaction"
    ),

    path(
        "transfer/",
        views.transfer_money,
        name="transfer_money"
    ),

    path(
        "admin-dashboard/",
        views.admin_dashboard,
        name="admin_dashboard",
    ),
    path(
    "transfer-receipt/<str:reference>/",
    views.transfer_receipt,
    name="transfer_receipt"
),
path(
    "set-pin/",
    views.set_transaction_pin,
    name="set_transaction_pin",
),
path(
    "admin-students/",
    views.admin_students,
    name="admin_students",
),
path(
    "bank-transfer/",
    views.bank_transfer,
    name="bank_transfer"
),
path(
    "resolve-bank-account/",
    views.resolve_bank_account,
    name="resolve_bank_account"
),
path(
    "get-banks/",
    views.get_banks,
    name="get_banks"
),
path(
    "school-fees/",
    views.pay_school_fees,
    name="pay_school_fees"
),
path(
    "sug-payment/",
    views.pay_sug_fee,
    name="pay_sug_fee"
),
path(
    "fund-wallet/",
    views.fund_wallet,
    name="fund_wallet"
),
]