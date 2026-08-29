from django.contrib import admin
from .models import Student, Wallet, Transaction


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "reg_no",
        "full_name",
        "email",
        "phone",
        "department",
        "level",
        "status",
    )

    search_fields = (
        "reg_no",
        "full_name",
        "email",
    )

    list_filter = (
        "department",
        "level",
        "status",
    )


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "balance",
        "status",
    )

    search_fields = (
        "student__reg_no",
        "student__full_name",
    )

    list_filter = (
        "status",
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "wallet",
        "transaction_type",
        "amount",
        "status",
        "created_at",
    )

    search_fields = (
        "reference",
        "wallet__student__reg_no",
        "wallet__student__full_name",
    )

    list_filter = (
        "transaction_type",
        "status",
    )

    readonly_fields = (
        "reference",
        "created_at",
    )