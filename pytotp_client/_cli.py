# ruff: noqa: T201, C901, PLR0912

from __future__ import annotations

import argparse
import sys

import qrcode
from pykeychain import Storage

from ._client import Client, ClientError, Item
from ._clipboard import write_to_clipboard
from ._colorizer import Color, colorize
from ._constants import PACKAGE_NAME, SERVICE_NAME


def _parce_cli_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest="command", help="Command")

    parser_get = subparser.add_parser("get", help="Get one time password")
    parser_get.add_argument("account", type=str, nargs="?", default="", help="Account name")

    parser_add = subparser.add_parser("add", help="Add secret for TOTP")
    parser_add.add_argument("account", type=str, help="Account name")
    parser_add.add_argument("secret", type=str, help="Secret")

    parser_delete = subparser.add_parser("delete", help="Delete entry")
    parser_delete.add_argument("account", type=str, help="Account name")

    subparser.add_parser("list", help="list all items to stdout")

    parser_add = subparser.add_parser("rename", help="Rename TOTP account")
    parser_add.add_argument("old_account", type=str, help="Old account name")
    parser_add.add_argument("new_account", type=str, help="New account name")

    parser_search = subparser.add_parser("search", help="Search for items")
    parser_search.add_argument("pattern", type=str, help="search pattern")

    parser_qr = subparser.add_parser("qr", help="Generate QR code for the account")
    parser_qr.add_argument("email", type=str, help="User's email")
    parser_qr.add_argument("account", type=str, help="Account name")

    subparser.add_parser("export", help="Export all items to stdout")
    subparser.add_parser("import", help="Import items from stdin")

    parser.add_argument("--version", action="store_true", default=False)

    return parser.parse_args()


def print_items(items: list[Item]) -> None:
    for item in items:
        print(f"{item.account}: {item.otp}")


def print_error(message: str) -> None:
    print(colorize(message, Color.RED))


def print_version() -> None:
    import importlib.metadata

    try:
        version = importlib.metadata.version(PACKAGE_NAME)
        print(version)
    except importlib.metadata.PackageNotFoundError:
        print("Package version not found.")


def entrypoint() -> None:
    args = _parce_cli_arguments()

    if args.version:
        print_version()
        sys.exit(0)

    storage = Storage(SERVICE_NAME)
    client = Client(storage)

    try:
        if args.command == "get":
            items = client.get_otp(args.account)
            print_items(items)
            write_to_clipboard(items[0].otp)

        elif args.command == "add":
            client.set_secret(args.account, args.secret)

        elif args.command == "delete":
            reply = input(f"Are you sure want to delete TOTP secret for {args.account}? (Yy/Nn): ")
            if reply in ["Y", "y"]:
                client.delete_secret(args.account)

        elif args.command == "list":
            data = client.list_all()
            print(data)

        elif args.command == "rename":
            client.rename_account(args.old_account, args.new_account)

        elif args.command == "search":
            items = client.search_items(args.pattern)
            if not items:
                print_error(f"Nothing found for search pattern {args.pattern}")
            else:
                print_items(items)

        elif args.command == "qr":
            url = client.generate_otp_auth_url(args.email, args.account)
            qr = qrcode.make(url)
            qr.show()

        elif args.command == "export":
            data = client.export_all()
            print(data)

        elif args.command == "import":
            data = sys.stdin.read()
            messages = client.import_data(data)
            for message in messages:
                if "OK" in message:
                    print(colorize(message, Color.GREEN))
                else:
                    print_error(message)

        else:
            print_error("Missing required argument 'command'")
            sys.exit(4)

    except ClientError as e:
        print_error(str(e))
        sys.exit(e.return_code)


if __name__ == "__main__":
    entrypoint()
