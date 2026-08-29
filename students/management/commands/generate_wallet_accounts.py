from django.core.management.base import BaseCommand
from students.models import Wallet
import random


class Command(BaseCommand):

    help = "Generate account numbers for wallets without account numbers"

    def handle(self, *args, **kwargs):

        wallets = Wallet.objects.filter(
            account_number__isnull=True
        )

        count = 0

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

            wallet.save(
                update_fields=["account_number"]
            )

            count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"{count} wallet account numbers generated successfully."
            )
        )