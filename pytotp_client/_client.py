from __future__ import annotations

import binascii
import dataclasses
import json

import pyotp
from pykeychain import AlreadyExistsException, NotFoundException, Storage


class ClientError(Exception):
    def __init__(self, message: str, return_code: int) -> None:
        self.message = message
        self.return_code = return_code

    def __str__(self) -> str:
        return self.message


@dataclasses.dataclass
class Item:
    account: str
    otp: str


class Client:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage

    def _get_otp_from_secret(self, secret: str) -> str:
        totp = pyotp.TOTP(secret)
        return totp.now()

    def search_items(self, pattern: str) -> list[Item]:
        if not pattern:
            accounts = self.storage.get_all_accounts()
        else:
            accounts = self.storage.search_accounts(pattern)
        if not accounts:
            return []

        items = []
        for account in accounts:
            secret = self.storage.get_password(account)
            otp = self._get_otp_from_secret(secret)
            item = Item(account=account, otp=otp)
            items.append(item)
        return items

    def generate_otp_auth_url(self, email: str, account: str) -> str:
        try:
            secret = self.storage.get_password(account)
        except NotFoundException:
            raise ClientError(message=f"Entry {account} not found.", return_code=1) from None
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=email, issuer_name=account)

    def get_otp(self, account: str) -> list[Item]:
        try:
            secret = self.storage.get_password(account)
        except NotFoundException:
            items = self.search_items(account)
            if not items:
                raise ClientError(message=f"Entry {account} not found.", return_code=1) from None
            return items

        otp = self._get_otp_from_secret(secret)
        return [Item(account=account, otp=otp)]

    def set_secret(self, account: str, secret: str) -> None:
        try:
            pyotp.TOTP(secret).now()
        except binascii.Error as e:
            raise ClientError(message=f"Invalid TOTP secret. {e}", return_code=3) from None

        try:
            self.storage.save_password(account, secret)
        except AlreadyExistsException:
            raise ClientError(message=f"Entry {account} already exists", return_code=2) from None

    def delete_secret(self, account: str) -> None:
        try:
            self.storage.delete(account)
        except NotFoundException:
            raise ClientError(message=f"Entry {account} not found", return_code=1) from None

    def list_all(self) -> str:
        accounts = self.storage.get_all_accounts()
        return "\n".join(accounts)

    def rename_account(self, old_account: str, new_account: str) -> None:
        try:
            secret = self.storage.get_password(old_account)
        except NotFoundException:
            raise ClientError(message=f"Entry {old_account} not found.", return_code=1) from None

        self.set_secret(new_account, secret)
        self.delete_secret(old_account)

    def export_all(self) -> str:
        result = []
        accounts = self.storage.get_all_accounts()
        for account in accounts:
            secret = self.storage.get_password(account)
            result.append({"account": account, "secret": secret})
        return json.dumps(result)

    def import_data(self, data: str) -> list[str]:
        messages: list[str] = []

        items = json.loads(data)
        for item in items:
            try:
                account = item["account"]
                secret = item["secret"]
            except KeyError:
                raise ClientError(message="Invalid file format for importing data", return_code=4) from None
            try:
                self.storage.save_password(account, secret)
            except AlreadyExistsException:
                messages.append(f"Item {account} FAIL -> already exists")
            else:
                messages.append(f"Item {account} OK")

        return messages
