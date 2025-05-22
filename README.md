# 🔐 TOTP Client for macOS

A lightweight, command-line utility written in **Python** to manage TOTP (Time-based One-Time Password) secrets securely on **macOS** using the native Keychain.

## 📌 Key Features

- 🔒 Secure storage using macOS Keychain
- 🧾 Add, delete, rename TOTP secrets
- 🔎 Search and list stored accounts
- 🔢 Generate and copy one-time passwords (OTPs)
- 📱 Display QR codes for account setup
- 📤 Export / 📥 Import secrets
- 🎨 Colorized output and clipboard integration

## 💻 Requirements

- macOS
- Python 3.13+
- [pykeychain](https://github.com/elisey/pykeychain/)
- [qrcode](https://github.com/lincolnloop/python-qrcode)

## Installation using pipx

```bash
pipx install pytotp-client
```

## 🔧 Usage

### Add a new TOTP secret

```bash
# account name - can be any string, no restrictions here 
totp add <account> <secret>
# Example:
totp add google.com BBBBDDDD
```

### Get one-time password (OTP)

```bash
totp get <pattenr>
# Example:
totp get google.com
# OTP will be printed and copied to clipboard

# you can use a search pattern here
totp get goo
# OTP for google.com will be printed here
```

### Delete an account

```bash
totp delete <account>
# Example:
totp delete google.com
```

### Rename an account

```bash
totp rename <old_account> <new_account>
# Example:
totp rename google.com gmail.personal
```

### Search for an account

```bash
totp search <pattern>
# Example:
totp search goog
# List of accounts with substring goog will be printed
```

### List all accounts

```bash
totp list
```

### Generate Google Auth compatible QR code

```bash
totp qr <email> <account>
# Example:
totp qr me@example.com google.com
# QR code will be shown using the system viewer
```

### Export all secrets

```bash
totp export > backup.txt
```

### Import secrets

```bash
totp import < backup.txt
```

### Show version

```bash
totp --version
```

## 🔐 Where are my secrets stored?

In the macOS default Keychain:
- Service name: pytotp_client
- Type: Application password

## 🧠 Tips

- The first OTP shown by get is also copied to your clipboard.
- Use export and import to backup/restore secrets between systems.
- The app exits with a non-zero status code on failure, allowing scripting/integration.
