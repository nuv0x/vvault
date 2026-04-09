<p align="center">
  <img src="https://raw.githubusercontent.com/sololc/sololc-vvault/main/assets/sololc-vvault.svg" width="160" height="160" alt="vlt logo">
</p>

# 🛡️ sololc-vvault (vlt)

[![PyPI version](https://img.shields.io/pypi/v/sololc-vvault.svg?color=blue)](https://pypi.org/project/sololc-vvault/)
[![Python versions](https://img.shields.io/pypi/pyversions/sololc-vvault.svg)](https://pypi.org/project/sololc-vvault/)
[![License](https://img.shields.io/badge/License-BSD--3--Clause-orange.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Sponsor](https://img.shields.io/badge/Sponsor-Ko--fi-F16061?logo=ko-fi&logoColor=white)](https://ko-fi.com/sololc)

**Zero-Knowledge, Offline-First, and High-Performance CLI Authenticator.**

`vlt` (pronounced *Volt*) is a modern 2FA (Two-Factor Authentication) manager designed for the terminal. It provides industrial-grade security with a minimalist user experience, ensuring your TOTP secrets remain yours alone.

> 🚀 **Building fast, secure, and offline-first tools for the modern terminal.**
> 💡 **Passionate about developer productivity and system transparency.**
> 🏠 **Keep it local. ⚡ Keep it simple.**

---

## 🔒 Security Architecture

Unlike many authenticators, `vlt` employs a **Zero-Knowledge** encryption model. Your data is never stored in plain text.

* **Key Derivation (KDF)**: We use **Argon2id** (the winner of the Password Hashing Competition) to derive high-entropy keys from your Master Password. 
    * *Parameters*: `memory_cost=64MB`, `iterations=3`, `lanes=4`.
* **Encryption**: All data is encrypted using **AES-256-GCM** (Galois/Counter Mode), providing both confidentiality and authenticity (tamper-proof).
* **Local-Only**: No cloud sync, no tracking, no telemetry. Your vault stays in `~/.vlt/`.

## ✨ Features

* **⚡️ Live Dashboard**: A real-time terminal UI (`Rich` powered) to monitor TOTP codes and expiration countdowns.
* **📂 Smart Import**: Seamlessly import via QR codes or standard `otpauth://` URLs.
* **📋 Clipboard Integration**: Copy codes with a single flag for lightning-fast logins.
* **🛠️ Modern Tech Stack**: Built with `uv`, `Typer`, `cryptography`, and `QReader`.

## 🚀 Installation

Ensure you have **Python 3.11+** installed. We recommend [uv](https://github.com/astral-sh/uv) for the best experience.

```bash
# Clone the repository
git clone [https://github.com/nuv0x/sololc-vvault.git](https://github.com/nuv0x/sololc-vvault.git)
cd sololc-vvault

# Install dependencies and install the tool in editable mode
uv sync
pip install -e .
```

## 📖 Usage Guide
Vvault uses the short and punchy vlt command.

1. Initialization
Set up your secure storage directory at ~/.vlt/.
```bash
vlt init
```

2. Adding Accounts
You can add accounts manually or import them intelligently via QR codes.

Manual Add:
```bash
vlt add github --secret KHR2UEJ33JJG... --issuer GitHub --category Dev
```

QR Code Import:
```bash
vlt import --qr ./path/to/qr_code.png
```

URL Import:
```bash
vlt import --url "otpauth://totp/Service:User?secret=XYZ..."
```

3. Management & Viewing
Launch Live Dashboard:
```bash
vlt dash
```

Get a Single Code:
```bash
vlt get github          # Display the code
vlt get github --copy   # Display and automatically copy to clipboard
```

List All Accounts:
```bash
vlt list
```

4. Backup
Keep your data safe by exporting your vault.
```bash
vlt backup ./my_backup.yaml
```

## 🛠️ Project Structure
The project follows a modular, functional design for clarity and maintainability:
* src/sololc_vvault/core/: Core logic layer containing TOTP generation, physical storage, and vault operations.
* src/sololc_vvault/main.py: Interaction layer featuring the polished CLI interface built with Typer and Rich.
* ~/.vlt/: The default local data storage path.

## ☕ Support the Project
If vlt makes your terminal life easier, consider supporting the development!
[![Support me on Ko-fi](https://img.shields.io/badge/Support%20me%20on%20Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/sololc)


## 🤝 Contributing
Contributions are welcome! If you have ideas for new features (such as supporting the Google Migration protocol or adding Master Password encryption), please feel free to:
* Fork the Project
* Create your Feature Branch (git checkout -b feature/AmazingFeature)
* Commit your Changes (git commit -m 'Add some AmazingFeature')
* Push to the Branch (git push origin feature/AmazingFeature)
* Open a Pull Request
