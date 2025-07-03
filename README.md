# Tautth

Cross-platform password manager that has so far only TOTP features, built with Python and KivyMD.

**Version:** V0.2
**Status:** In development
**Author:** Tex

---

## Features

- **TOTP Generation:** Securely generate time-based one-time passwords.
- **Settings:** Customize the app's appearance, including the theme color.

---

## Screenshots

*Screenshots coming soon!*

---

## Installation

### Desktop (Windows)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/resolutesx/Tauth.git
   cd tautth
   ```

2. **Install dependencies:**
   ```bash
   pip install kivy kivymd pyotp cryptography cffi openssl plyer pyperclip
   ```

3. **Run the app:**
   ```bash
   python main.py
   ```

Im planning on releasing actual installation setups, this has been tested only on Windows 11 with Python 3.13, you can try building it yourself on other OS's but I dont guarantee any functionality at all.

### Android (APK)

1. **Install [Buildozer](https://github.com/kivy/buildozer) and the required dependencies**.

2. **Build the APK:**
   ```bash
   buildozer -v android debug
   ```

3. **Install on your device:**
   ```bash
   buildozer android deploy run
   ```

**This is NOT RECOMMENDED. Buildozer is made for Python 2, and there are a lot of compatibility issues while compiling with Python 3, theres a lot of other things that could go wrong, for example missing dependencies. The way I managed to compile to APK is by changing the source code of some dependencies myself, there has been glitches with compiling on WSL, but since you NEED a Linux enviroment to compile this, I used a github codespace. Dont do it if you dont want to spend hours debugging.**

---

## Usage

- **Add Account:**  
  Tap the "+" button, enter the account name and TOTP secret.

- **Copy Code:**  
  Long-press an account card to copy the current code to clipboard.

- **Backup:**  
  Use the menu to create a password-protected backup file.

- **Restore:**  
  Use the menu to restore from a backup file (password required).

- **Settings:**
  Access the settings from the menu to change the app's theme color and view the app version.

---

## Security

- All secrets are stored locally and never leave your device.
- Backup files are encrypted with a password using PBKDF2 and Fernet (AES).
- TOTP secrets are validated before use or restore.

---

## Requirements

- Python 3.8+
- Kivy
- KivyMD
- pyotp
- cryptography
- cffi
- openssl
- plyer
- pyperclip

More may be added in later versions.

*(All dependencies are listed in `buildozer.spec` for Android builds.)*

---

## License

MIT License.  
See [LICENSE](LICENSE) for details.

---

## Author

- **Tex**

---

## Contributing

Pull requests and issues are welcome!  
Please open an issue for bugs, feature requests, or questions.

### Use this at your own risk, it is expected for the application to have a lot of issues, bugs and glitches.