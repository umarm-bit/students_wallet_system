from django.db import models
from django.contrib.auth.hashers import make_password


class Student(models.Model):
    reg_no = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True)
    department = models.CharField(max_length=150, blank=True)
    programme = models.CharField(max_length=150, blank=True)
    level = models.CharField(max_length=30, blank=True)
    password = models.CharField(max_length=255)
    transaction_pin = models.CharField(max_length=255,blank=True,null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reg_no} - {self.full_name}"
class Wallet(models.Model):
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name="wallet"
    )

    account_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True
    )

    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )

    status = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        if not self.account_number:

            last_wallet = (
                Wallet.objects
                .filter(account_number__startswith="DAU2026")
                .order_by("-id")
                .first()
            )

            if last_wallet and last_wallet.account_number:
                try:
                    last_number = int(
                        last_wallet.account_number[-4:]
                    )
                    next_number = last_number + 1
                except ValueError:
                    next_number = 1
            else:
                next_number = 1

            self.account_number = (
                f"DAU2026{next_number:04d}"
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.student.reg_no} - "
            f"{self.account_number} - "
            f"₦{self.balance}"
        )

class Transaction(models.Model):
    CREDIT = "credit"
    DEBIT = "debit"
    TRANSFER = "transfer"

    TRANSACTION_TYPES = [
        (CREDIT, "Credit"),
        (DEBIT, "Debit"),
        (TRANSFER, "Transfer"),
    ]

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="transactions"
    )

    receiver_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="received_transactions"
    )

    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    reference = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.CharField(
        max_length=255,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        default="successful"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reference} - ₦{self.amount}"
class BankTransfer(models.Model):
    PENDING = "pending"
    SUCCESSFUL = "successful"
    FAILED = "failed"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (SUCCESSFUL, "Successful"),
        (FAILED, "Failed"),
    ]

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="bank_transfers"
    )

    bank_name = models.CharField(
        max_length=100
    )

    account_number = models.CharField(
        max_length=20
    )

    account_name = models.CharField(
        max_length=150
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    reference = models.CharField(
        max_length=100,
        unique=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.reference} - ₦{self.amount}"
class SchoolFeePayment(models.Model):
    SUCCESSFUL = "successful"
    PENDING = "pending"
    FAILED = "failed"

    PAYMENT_STATUS = [
        (SUCCESSFUL, "Successful"),
        (PENDING, "Pending"),
        (FAILED, "Failed"),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="school_fee_payments"
    )

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="school_fee_payments"
    )

    academic_session = models.CharField(
        max_length=20
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    reference = models.CharField(
        max_length=100,
        unique=True
    )

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default=PENDING
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.reference} - ₦{self.amount}"
class SUGPayment(models.Model):
    SUCCESSFUL = "successful"
    PENDING = "pending"
    FAILED = "failed"

    PAYMENT_STATUS = [
        (SUCCESSFUL, "Successful"),
        (PENDING, "Pending"),
        (FAILED, "Failed"),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="sug_payments"
    )

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="sug_payments"
    )

    academic_session = models.CharField(
        max_length=20
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    reference = models.CharField(
        max_length=100,
        unique=True
    )

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default=PENDING
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.reference} - ₦{self.amount}"
class VirtualBankAccount(models.Model):
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name="virtual_bank_account"
    )

    wallet = models.OneToOneField(
        Wallet,
        on_delete=models.CASCADE,
        related_name="virtual_bank_account"
    )

    bank_name = models.CharField(
        max_length=100
    )

    account_number = models.CharField(
        max_length=10,
        unique=True
    )

    account_name = models.CharField(
        max_length=150
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.account_name} - "
            f"{self.account_number}"
        )