import argparse
import sys

from _client import Client, ClientError
from _clipboard import write_to_clipboard
from _constants import SERVICE_NAME
from pykeychain import Storage


def _parce_cli_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest="command", help="Command")

    parser_get = subparser.add_parser("get", help="Get one time password")
    parser_get.add_argument("account", type=str, help="Account name")

    parser_add = subparser.add_parser("add", help="Add secret for TOTP")
    parser_add.add_argument("account", type=str, help="Account name")
    parser_add.add_argument("secret", type=str, help="Secret")

    parser_delete = subparser.add_parser("delete", help="Delete entry")
    parser_delete.add_argument("account", type=str, help="Account name")

    return parser.parse_args()


def entrypoint() -> None:
    args = _parce_cli_arguments()
    storage = Storage(SERVICE_NAME)
    client = Client(storage)

    try:
        if args.command == "get":
            otp = client.get_otp(args.account)
            print(otp)
            write_to_clipboard(otp)

        elif args.command == "add":
            client.set_secret(args.account, args.secret)

        elif args.command == "delete":
            reply = input(f"Are you sure want to delete TOTP secret for {args.account}? (Yy/Nn): ")
            if reply in ["Y", "y"]:
                client.delete_secret(args.account)
    except ClientError as e:
        print(str(e))
        sys.exit(e.return_code)


if __name__ == "__main__":
    entrypoint()
