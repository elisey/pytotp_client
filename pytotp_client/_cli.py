from __future__ import annotations

import argparse
import sys

from pykeychain import Storage

from ._client import Client, ClientError, Item
from ._clipboard import write_to_clipboard
from ._constants import SERVICE_NAME


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

    parser_search = subparser.add_parser("search", help="Search for items")
    parser_search.add_argument("pattern", type=str, help="search pattern")

    return parser.parse_args()


def print_items(items: list[Item]) -> None:
    for item in items:
        print(f"{item.account}: {item.otp}")


def entrypoint() -> None:
    args = _parce_cli_arguments()
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

        elif args.command == "search":
            items = client.search_items(args.pattern)
            if not items:
                print(f"Nothing found for search pattern {args.pattern}")
            print_items(items)

    except ClientError as e:
        print(str(e))
        sys.exit(e.return_code)


if __name__ == "__main__":
    entrypoint()
