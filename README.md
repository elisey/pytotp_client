# TOTP client for macOS

- Written in Python
- Secrets are stored in macOS keychain.

## How to work with pytotp_client

Add secret to keychain

```shell
totp add google.com BBBBDDDD
```

Get one time password

```shell
totp get google.com
```

Remove secret from keychain

```shell
totp delete google.com
```

## Where is my secrets stored?

In macOS default keychain.
 - Name: pytotp_client
 - Type: application password