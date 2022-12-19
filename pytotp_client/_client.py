import binascii

import pyotp
from pykeychain import AlreadyExistsException, NotFoundException, Storage


class ClientError(Exception):
    def __init__(self, message: str, return_code: int) -> None:
        self.message = message
        self.return_code = return_code

    def __str__(self) -> str:
        return self.message


class Client:
    def __init__(self, storage: Storage):
        self.storage = storage

    def get_otp(self, account: str) -> str:
        try:
            secret = self.storage.get_password(account)
        except NotFoundException:
            raise ClientError(message=f"Entry {account} not found.", return_code=1)

        totp = pyotp.TOTP(secret)
        one_time_password = totp.now()
        return one_time_password

    def set_secret(self, account: str, secret: str) -> None:
        try:
            pyotp.TOTP(secret).now()
        except binascii.Error as e:
            raise ClientError(message=f"Invalid TOTP secret. {e}", return_code=3)

        try:
            self.storage.save_password(account, secret)
        except AlreadyExistsException:
            raise ClientError(message=f"Entry {account} already exists.", return_code=2)

    def delete_secret(self, account: str) -> None:
        try:
            self.storage.delete(account)
        except NotFoundException:
            raise ClientError(message=f"Entry {account} not found.", return_code=1)
