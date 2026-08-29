from django.shortcuts import render, redirect
from django.db import transaction
from decimal import Decimal
from .forms import StudentRegistrationForm
from .models import Student, Wallet, Transaction, VirtualBankAccount
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.utils.crypto import get_random_string
import random
from .models import Student, Wallet, Transaction, BankTransfer
import requests
from django.conf import settings
from django.http import JsonResponse
from .models import Student, Wallet, Transaction, SchoolFeePayment, SUGPayment
def register_student(request):
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)

        if form.is_valid():
            with transaction.atomic():

                student = form.save()

                wallet = Wallet.objects.create(
                    student=student
                )

                last_virtual = (
                    VirtualBankAccount.objects
                    .filter(
                        account_number__startswith="123456"
                    )
                    .order_by("-id")
                    .first()
                )

                if last_virtual:
                    try:
                        last_number = int(
                            last_virtual.account_number
                        )
                        next_number = last_number + 1
                    except ValueError:
                        next_number = 1234567890
                else:
                    next_number = 1234567890

                while VirtualBankAccount.objects.filter(
                    account_number=str(next_number)
                ).exists():
                    next_number += 1

                VirtualBankAccount.objects.create(
                    student=student,
                    wallet=wallet,
                    bank_name="Test Bank",
                    account_number=str(next_number),
                    account_name=student.full_name,
                )

            return redirect(
                "registration_success"
            )

    else:
        form = StudentRegistrationForm()

    return render(
        request,
        "students/register.html",
        {"form": form}
    )

def registration_success(request):
    return render(
        request,
        "students/registration_success.html"
    )
    from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password

# ... sauran code ɗinka ya kasance ...


def student_login(request):
    if request.method == "POST":
        reg_no = request.POST.get("reg_no", "").strip()
        password = request.POST.get("password", "")

        try:
            student = Student.objects.get(reg_no=reg_no)
        except Student.DoesNotExist:
            messages.error(
                request,
                "Registration Number was not found."
            )
            return redirect("student_login")

        if not student.status:
            messages.error(
                request,
                "Your student account is inactive."
            )
            return redirect("student_login")

        if not check_password(password, student.password):
            messages.error(
                request,
                "Incorrect password."
            )
            return redirect("student_login")

        request.session["student_id"] = student.id

        return redirect("student_dashboard")

    return render(
        request,
        "students/login.html"
    )

def student_dashboard(request):
    student_id = request.session.get("student_id")

    if not student_id:
        return redirect("student_login")

    student = Student.objects.get(id=student_id)
    wallet = Wallet.objects.get(student=student)

    transactions = wallet.transactions.order_by("-created_at")

    return render(
        request,
        "students/dashboard.html",
        {
            "student": student,
            "wallet": wallet,
            "transactions": transactions,
            "virtual_account": getattr(
                wallet,
                "virtual_bank_account",
                None
            ),
        }
    )

def student_logout(request):
    request.session.flush()
    return redirect("student_login")
    from decimal import Decimal
from django.db import transaction
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.crypto import get_random_string

from .models import Student, Wallet, Transaction


def wallet_transaction(request):
    student_id = request.session.get("student_id")

    if not student_id:
        return redirect("student_login")

    student = Student.objects.get(id=student_id)
    wallet = Wallet.objects.get(student=student)

    if request.method == "POST":
        transaction_type = request.POST.get("transaction_type")
        amount_text = request.POST.get("amount", "").strip()
        description = request.POST.get("description", "").strip()

        try:
            amount = Decimal(amount_text)

            if amount <= 0:
                raise ValueError

        except (ValueError, TypeError):
            messages.error(request, "Please enter a valid amount.")
            return redirect("wallet_transaction")

        if transaction_type not in ["credit", "debit"]:
            messages.error(request, "Invalid transaction type.")
            return redirect("wallet_transaction")

        if transaction_type == "debit" and amount > wallet.balance:
            messages.error(request, "Insufficient wallet balance.")
            return redirect("wallet_transaction")

        reference = "TXN-" + get_random_string(10).upper()

        with transaction.atomic():
            if transaction_type == "credit":
                wallet.balance += amount
            else:
                wallet.balance -= amount

            wallet.save()

            Transaction.objects.create(
                wallet=wallet,
                transaction_type=transaction_type,
                amount=amount,
                reference=reference,
                description=description,
                status="successful"
            )

        messages.success(
            request,
            f"Transaction successful. Reference: {reference}"
        )

        return redirect("student_dashboard")

    return render(
        request,
        "students/transaction.html",
        {
            "student": student,
            "wallet": wallet,
        }
    )
def transfer_money(request):
    student_id = request.session.get("student_id")

    if not student_id:
        return redirect("student_login")

    student = Student.objects.get(id=student_id)
    sender_wallet = Wallet.objects.get(student=student)

    if not student.transaction_pin:
        messages.error(
            request,
            "Please set your Transaction PIN before making a transfer."
        )
        return redirect("set_transaction_pin")

    if request.method == "POST":
        recipient_reg_no = request.POST.get("recipient_reg_no", "").strip()
        amount_text = request.POST.get("amount", "").strip()
        pin = request.POST.get("pin", "").strip()

        if not pin.isdigit() or len(pin) != 4:
            messages.error(
                request,
                "Please enter your 4-digit Transaction PIN."
            )
            return redirect("transfer_money")

        if not check_password(pin, student.transaction_pin):
            messages.error(
                request,
                "Incorrect Transaction PIN."
            )
            return redirect("transfer_money")

        try:
            recipient = Student.objects.get(reg_no=recipient_reg_no)
        except Student.DoesNotExist:
            messages.error(
                request,
                "Recipient student with this Registration Number was not found."
            )
            return redirect("transfer_money")

        if recipient.id == student.id:
            messages.error(
                request,
                "You cannot transfer money to yourself."
            )
            return redirect("transfer_money")

        if not recipient.status:
            messages.error(
                request,
                "Recipient student account is inactive."
            )
            return redirect("transfer_money")

        try:
            receiver_wallet = Wallet.objects.get(student=recipient)
        except Wallet.DoesNotExist:
            messages.error(
                request,
                "Recipient wallet was not found."
            )
            return redirect("transfer_money")

        if not receiver_wallet.status:
            messages.error(
                request,
                "Recipient wallet is inactive."
            )
            return redirect("transfer_money")

        try:
            amount = Decimal(amount_text)

            if amount <= 0:
                raise ValueError

        except (ValueError, TypeError):
            messages.error(
                request,
                "Please enter a valid amount."
            )
            return redirect("transfer_money")

        if amount > sender_wallet.balance:
            messages.error(
                request,
                "Insufficient wallet balance."
            )
            return redirect("transfer_money")

        transfer_reference = "TRF-" + get_random_string(10).upper()

        with transaction.atomic():

            sender_wallet.balance -= amount
            sender_wallet.save()

            receiver_wallet.balance += amount
            receiver_wallet.save()

            Transaction.objects.create(
                wallet=sender_wallet,
                receiver_wallet=receiver_wallet,
                transaction_type=Transaction.DEBIT,
                amount=amount,
                reference=transfer_reference + "-D",
                description=f"Transfer to {recipient.reg_no}",
                status="successful"
            )

            Transaction.objects.create(
                wallet=receiver_wallet,
                receiver_wallet=receiver_wallet,
                transaction_type=Transaction.CREDIT,
                amount=amount,
                reference=transfer_reference + "-C",
                description=f"Transfer from {student.reg_no}",
                status="successful"
            )

        messages.success(
            request,
            f"Transfer of ₦{amount:,.2f} to {recipient.full_name} was successful."
        )

        return redirect(
            "transfer_receipt",
            reference=transfer_reference + "-D"
        )

    return render(
        request,
        "students/transfer.html",
        {
            "student": student,
            "wallet": sender_wallet,
        }
    )
def transfer_receipt(request, reference):
    student_id = request.session.get("student_id")

    if not student_id:
        return redirect("student_login")

    student = Student.objects.get(id=student_id)

    try:
        transaction_record = Transaction.objects.select_related(
            "wallet__student",
            "receiver_wallet__student"
        ).get(reference=reference)

    except Transaction.DoesNotExist:
        messages.error(
            request,
            "Transaction receipt was not found."
        )
        return redirect("student_dashboard")

    # Get sender and receiver
    if transaction_record.transaction_type == Transaction.DEBIT:
        sender_wallet = transaction_record.wallet
        receiver_wallet = transaction_record.receiver_wallet

    else:
        sender_wallet = transaction_record.receiver_wallet
        receiver_wallet = transaction_record.wallet

    # Make sure both wallets exist
    if not sender_wallet or not receiver_wallet:
        messages.error(
            request,
            "Invalid transfer receipt."
        )
        return redirect("student_dashboard")

    # Check authorization
    if (
        student != sender_wallet.student
        and student != receiver_wallet.student
    ):
        messages.error(
            request,
            "You are not authorized to view this receipt."
        )
        return redirect("student_dashboard")

    # Find the sender's debit transaction.
    # This gives us one consistent receipt reference.
    if transaction_record.transaction_type == Transaction.CREDIT:
        debit_reference = transaction_record.reference.replace("-C", "-D")

        try:
            transaction_record = Transaction.objects.select_related(
                "wallet__student",
                "receiver_wallet__student"
            ).get(
                reference=debit_reference
            )
        except Transaction.DoesNotExist:
            pass

    return render(
        request,
        "students/transfer_receipt.html",
        {
            "transaction": transaction_record,
            "student": student,
        }
    )
@staff_member_required
def admin_dashboard(request):
    total_students = Student.objects.count()
    total_wallets = Wallet.objects.count()
    total_transactions = Transaction.objects.count()

    total_balance = Wallet.objects.aggregate(
        total=Sum("balance")
    )["total"] or Decimal("0.00")

    recent_transactions = Transaction.objects.select_related(
        "wallet__student"
    ).order_by("-created_at")[:10]

    return render(
        request,
        "students/admin_dashboard.html",
        {
            "total_students": total_students,
            "total_wallets": total_wallets,
            "total_transactions": total_transactions,
            "total_balance": total_balance,
            "recent_transactions": recent_transactions,
        },
    )
def set_transaction_pin(request):
    student_id = request.session.get("student_id")

    if not student_id:
        return redirect("student_login")

    student = Student.objects.get(id=student_id)

    if request.method == "POST":
        pin = request.POST.get("pin", "").strip()
        confirm_pin = request.POST.get("confirm_pin", "").strip()

        if not pin.isdigit() or len(pin) != 4:
            messages.error(
                request,
                "PIN must be exactly 4 digits."
            )
            return redirect("set_transaction_pin")

        if pin != confirm_pin:
            messages.error(
                request,
                "PINs do not match."
            )
            return redirect("set_transaction_pin")

        student.transaction_pin = make_password(pin)
        student.save()

        messages.success(
            request,
            "Transaction PIN has been set successfully."
        )

        return redirect("student_dashboard")

    return render(
        request,
        "students/set_pin.html",
        {
            "student": student,
        }
    )

@staff_member_required
def admin_students(request):
    students = Student.objects.select_related("wallet").order_by("-created_at")

    return render(
        request,
        "students/admin_students.html",
        {
            "students": students,
        }
    )
def generate_wallet_account_numbers():
    wallets = Wallet.objects.filter(
        account_number__isnull=True
    )

    for wallet in wallets:

        account_number = (
            "FEDDAU"
            + str(random.randint(1000000000, 9999999999))
        )

        while Wallet.objects.filter(
            account_number=account_number
        ).exists():

            account_number = (
                "FEDDAU"
                + str(random.randint(1000000000, 9999999999))
            )

        wallet.account_number = account_number
        wallet.save(update_fields=["account_number"])
def resolve_bank_account(request):
    if request.method != "GET":
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid request method."
            },
            status=400
        )

    account_number = request.GET.get(
        "account_number",
        ""
    ).strip()

    bank_code = request.GET.get(
        "bank_code",
        ""
    ).strip()

    if not account_number.isdigit() or len(account_number) != 10:
        return JsonResponse(
            {
                "success": False,
                "message": "Account number must be 10 digits."
            },
            status=400
        )

    if not bank_code:
        return JsonResponse(
            {
                "success": False,
                "message": "Bank code is required."
            },
            status=400
        )

    # Test Mode
    if (
        settings.PAYSTACK_SECRET_KEY
        and settings.PAYSTACK_SECRET_KEY.startswith("sk_test_")
        and bank_code == "001"
    ):
        return JsonResponse(
            {
                "success": True,
                "account_number": account_number,
                "account_name": "TEST ACCOUNT",
            }
        )

    url = "https://api.paystack.co/bank/resolve"

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }

    params = {
        "account_number": account_number,
        "bank_code": bank_code,
    }

    print(
        "PAYSTACK KEY PREFIX:",
        str(settings.PAYSTACK_SECRET_KEY)[:8]
    )

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=15
        )

        print(
            "PAYSTACK RESOLVE STATUS:",
            response.status_code
        )

        print(
            "PAYSTACK RESOLVE RESPONSE:",
            response.text
        )

        data = response.json()

    except requests.RequestException as e:

        print(
            "PAYSTACK RESOLVE CONNECTION ERROR:",
            str(e)
        )

        return JsonResponse(
            {
                "success": False,
                "message": "Unable to connect to Paystack."
            },
            status=503
        )

    except ValueError:

        print(
            "PAYSTACK RESOLVE INVALID JSON:",
            response.text
        )

        return JsonResponse(
            {
                "success": False,
                "message": "Paystack returned an invalid response."
            },
            status=500
        )

    if response.status_code != 200 or not data.get("status"):

        return JsonResponse(
            {
                "success": False,
                "message": data.get(
                    "message",
                    "Account could not be resolved."
                ),
                "paystack_status": response.status_code,
            },
            status=400
        )

    account_data = data.get(
        "data",
        {}
    )

    return JsonResponse(
        {
            "success": True,
            "account_number": account_data.get(
                "account_number"
            ),
            "account_name": account_data.get(
                "account_name"
            ),
        }
    )
def bank_transfer(request):
    student_id = request.session.get("student_id")

    if not student_id:
        return redirect("student_login")

    student = Student.objects.get(id=student_id)
    wallet = Wallet.objects.get(student=student)

    if request.method == "POST":

        bank_name = request.POST.get(
            "bank_name",
            ""
        ).strip()

        bank_code = request.POST.get(
            "bank_code",
            ""
        ).strip()

        account_number = request.POST.get(
            "account_number",
            ""
        ).strip()

        amount_text = request.POST.get(
            "amount",
            ""
        ).strip()

        pin = request.POST.get(
            "pin",
            ""
        ).strip()

        # -----------------------------
        # CHECK BANK
        # -----------------------------

        if not bank_name or not bank_code:
            messages.error(
                request,
                "Please select a valid bank."
            )
            return redirect("bank_transfer")

        # -----------------------------
        # CHECK ACCOUNT NUMBER
        # -----------------------------

        if not account_number.isdigit():
            messages.error(
                request,
                "Please enter a valid bank account number."
            )
            return redirect("bank_transfer")

        if len(account_number) != 10:
            messages.error(
                request,
                "Bank account number must be 10 digits."
            )
            return redirect("bank_transfer")

        # -----------------------------
        # CHECK PIN
        # -----------------------------

        if not pin.isdigit() or len(pin) != 4:
            messages.error(
                request,
                "Please enter your 4-digit Transaction PIN."
            )
            return redirect("bank_transfer")

        if not student.transaction_pin:
            messages.error(
                request,
                "Please set your Transaction PIN first."
            )
            return redirect("set_transaction_pin")

        if not check_password(
            pin,
            student.transaction_pin
        ):
            messages.error(
                request,
                "Incorrect Transaction PIN."
            )
            return redirect("bank_transfer")

        # -----------------------------
        # VERIFY BANK ACCOUNT WITH PAYSTACK
        # -----------------------------

        url = "https://api.paystack.co/bank/resolve"

        headers = {
            "Authorization": (
                f"Bearer {settings.PAYSTACK_SECRET_KEY}"
            ),
        }

        params = {
            "account_number": account_number,
            "bank_code": bank_code,
        }

        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=15
            )

            data = response.json()

        except requests.RequestException:
            messages.error(
                request,
                "Unable to connect to bank verification service."
            )
            return redirect("bank_transfer")

        if response.status_code != 200 or not data.get("status"):
            messages.error(
                request,
                data.get(
                    "message",
                    "Bank account could not be verified."
                )
            )
            return redirect("bank_transfer")

        account_data = data.get("data", {})

        verified_account_name = account_data.get(
            "account_name"
        )

        verified_account_number = account_data.get(
            "account_number"
        )

        if not verified_account_name:
            messages.error(
                request,
                "Account name could not be verified."
            )
            return redirect("bank_transfer")

        if verified_account_number != account_number:
            messages.error(
                request,
                "Bank account verification failed."
            )
            return redirect("bank_transfer")

        # -----------------------------
        # CHECK AMOUNT
        # -----------------------------

        try:
            amount = Decimal(amount_text)

            if amount <= 0:
                raise ValueError

        except (ValueError, TypeError):
            messages.error(
                request,
                "Please enter a valid amount."
            )
            return redirect("bank_transfer")

        if amount > wallet.balance:
            messages.error(
                request,
                "Insufficient wallet balance."
            )
            return redirect("bank_transfer")

        # -----------------------------
        # CREATE TRANSFER
        # -----------------------------

        transfer_reference = (
            "BTRF-"
            + get_random_string(10).upper()
        )

        with transaction.atomic():

            wallet.balance -= amount
            wallet.save()

            BankTransfer.objects.create(
                wallet=wallet,
                bank_name=bank_name,
                account_number=account_number,
                account_name=verified_account_name,
                amount=amount,
                reference=transfer_reference,
                status=BankTransfer.SUCCESSFUL,
            )

            Transaction.objects.create(
                wallet=wallet,
                transaction_type=Transaction.DEBIT,
                amount=amount,
                reference=transfer_reference,
                description=(
                    f"Bank transfer to "
                    f"{verified_account_name} "
                    f"({bank_name})"
                ),
                status="successful",
            )

        messages.success(
            request,
            f"Bank transfer of ₦{amount:,.2f} "
            f"to {verified_account_name} was successful."
        )

        return redirect(
            "student_dashboard"
        )

    return render(
        request,
        "students/bank_transfer.html",
        {
            "student": student,
            "wallet": wallet,
        }
    )
def get_banks(request):
    url = "https://api.paystack.co/bank"

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    params = {
        "country": "nigeria",
        "currency": "NGN",
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=15
        )

        print(
            "PAYSTACK BANK STATUS:",
            response.status_code
        )

        print(
            "PAYSTACK BANK RESPONSE:",
            response.text
        )

        data = response.json()

    except requests.RequestException as e:
        print(
            "PAYSTACK CONNECTION ERROR:",
            str(e)
        )

        return JsonResponse(
            {
                "success": False,
                "message": "Unable to connect to Paystack.",
            },
            status=503
        )

    except ValueError:
        print(
            "PAYSTACK BANK INVALID JSON:",
            response.text
        )

        return JsonResponse(
            {
                "success": False,
                "message": "Paystack returned an invalid response.",
            },
            status=500
        )

    if response.status_code != 200 or not data.get("status"):
        return JsonResponse(
            {
                "success": False,
                "message": data.get(
                    "message",
                    "Unable to retrieve banks."
                ),
            },
            status=400
        )

    banks = []

    for bank in data.get("data", []):
        if (
            bank.get("active")
            and bank.get("name")
            and bank.get("code")
        ):
            banks.append(
                {
                    "name": bank.get("name"),
                    "code": bank.get("code"),
                }
            )

    return JsonResponse(
        {
            "success": True,
            "banks": banks,
        }
    )
def pay_school_fees(request):
    student_id = request.session.get("student_id")

    if not student_id:
        return redirect("student_login")

    student = Student.objects.get(id=student_id)
    wallet = Wallet.objects.get(student=student)

    if request.method == "POST":

        academic_session = request.POST.get(
            "academic_session",
            ""
        ).strip()

        amount_text = request.POST.get(
            "amount",
            ""
        ).strip()

        pin = request.POST.get(
            "pin",
            ""
        ).strip()

        if not academic_session:
            messages.error(
                request,
                "Please select an academic session."
            )
            return redirect("pay_school_fees")

        if not pin.isdigit() or len(pin) != 4:
            messages.error(
                request,
                "Please enter your 4-digit Transaction PIN."
            )
            return redirect("pay_school_fees")

        if not student.transaction_pin:
            messages.error(
                request,
                "Please set your Transaction PIN first."
            )
            return redirect("set_transaction_pin")

        if not check_password(
            pin,
            student.transaction_pin
        ):
            messages.error(
                request,
                "Incorrect Transaction PIN."
            )
            return redirect("pay_school_fees")

        try:
            amount = Decimal(amount_text)

            if amount <= 0:
                raise ValueError

        except (ValueError, TypeError):
            messages.error(
                request,
                "Please enter a valid amount."
            )
            return redirect("pay_school_fees")

        if amount > wallet.balance:
            messages.error(
                request,
                "Insufficient wallet balance."
            )
            return redirect("pay_school_fees")

        payment_reference = (
            "SCH-"
            + get_random_string(10).upper()
        )

        with transaction.atomic():

            wallet.balance -= amount
            wallet.save()

            SchoolFeePayment.objects.create(
                student=student,
                wallet=wallet,
                academic_session=academic_session,
                amount=amount,
                reference=payment_reference,
                status=SchoolFeePayment.SUCCESSFUL,
            )

            Transaction.objects.create(
                wallet=wallet,
                transaction_type=Transaction.DEBIT,
                amount=amount,
                reference=payment_reference,
                description=(
                    f"School fees payment "
                    f"for {academic_session}"
                ),
                status="successful",
            )

        messages.success(
            request,
            f"School fees payment of "
            f"₦{amount:,.2f} was successful."
        )

        return redirect(
            "student_dashboard"
        )

    return render(
        request,
        "students/school_fees.html",
        {
            "student": student,
            "wallet": wallet,
        }
    )
def pay_sug_fee(request):
    student_id = request.session.get("student_id")

    if not student_id:
        return redirect("student_login")

    student = Student.objects.get(id=student_id)
    wallet = Wallet.objects.get(student=student)

    if request.method == "POST":

        academic_session = request.POST.get(
            "academic_session",
            ""
        ).strip()

        amount_text = request.POST.get(
            "amount",
            ""
        ).strip()

        pin = request.POST.get(
            "pin",
            ""
        ).strip()

        if not academic_session:
            messages.error(
                request,
                "Please select an academic session."
            )
            return redirect("pay_sug_fee")

        if not pin.isdigit() or len(pin) != 4:
            messages.error(
                request,
                "Please enter your 4-digit Transaction PIN."
            )
            return redirect("pay_sug_fee")

        if not student.transaction_pin:
            messages.error(
                request,
                "Please set your Transaction PIN first."
            )
            return redirect("set_transaction_pin")

        if not check_password(
            pin,
            student.transaction_pin
        ):
            messages.error(
                request,
                "Incorrect Transaction PIN."
            )
            return redirect("pay_sug_fee")

        try:
            amount = Decimal(amount_text)

            if amount <= 0:
                raise ValueError

        except (ValueError, TypeError):
            messages.error(
                request,
                "Please enter a valid amount."
            )
            return redirect("pay_sug_fee")

        if amount > wallet.balance:
            messages.error(
                request,
                "Insufficient wallet balance."
            )
            return redirect("pay_sug_fee")

        payment_reference = (
            "SUG-"
            + get_random_string(10).upper()
        )

        with transaction.atomic():

            wallet.balance -= amount
            wallet.save()

            SUGPayment.objects.create(
                student=student,
                wallet=wallet,
                academic_session=academic_session,
                amount=amount,
                reference=payment_reference,
                status=SUGPayment.SUCCESSFUL,
            )

            Transaction.objects.create(
                wallet=wallet,
                transaction_type=Transaction.DEBIT,
                amount=amount,
                reference=payment_reference,
                description=(
                    f"SUG fee payment "
                    f"for {academic_session}"
                ),
                status="successful",
            )

        messages.success(
            request,
            f"SUG payment of "
            f"₦{amount:,.2f} was successful."
        )

        return redirect(
            "student_dashboard"
        )

    return render(
        request,
        "students/sug_payment.html",
        {
            "student": student,
            "wallet": wallet,
        }
    )
def fund_wallet(request):
    student_id = request.session.get("student_id")

    if not student_id:
        return redirect("student_login")

    student = Student.objects.get(
        id=student_id
    )

    wallet = Wallet.objects.get(
        student=student
    )

    virtual_account = getattr(
        wallet,
        "virtual_bank_account",
        None
    )

    return render(
        request,
        "students/fund_wallet.html",
        {
            "student": student,
            "wallet": wallet,
            "virtual_account": virtual_account,
        }
    )