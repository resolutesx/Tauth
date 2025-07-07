# Kotlin TOTP Authenticator

Cross-platform TOTP (Time-based One-Time Password) authenticator built with Kotlin Multiplatform and Jetpack Compose.

**Version:** 1.0.0
**Status:** In development
**Author:** Tex

---

## Features

- **TOTP Generation:** Securely generate time-based one-time passwords
- **Cross-platform:** Works on Android and Desktop
- **Encrypted Storage:** All TOTP secrets are encrypted with AES-GCM
- **Password Protection:** App requires a password to access encrypted data
- **Settings:** Customize the app's appearance with theme colors
- **Clipboard Integration:** Copy TOTP codes with a single tap

---

## Security Features

### 🔐 **Encryption**
- **AES-GCM Encryption:** All TOTP secrets are encrypted using AES-256-GCM
- **Password Protection:** App requires a master password to decrypt data
- **Secure Key Derivation:** Passwords are hashed using SHA-256 with salt
- **Local Storage Only:** All data stays on your device, never transmitted

### 🛡️ **Data Protection**
- **Encrypted File Storage:** Account data stored in `.encrypted` files
- **Password Hashing:** Master passwords are securely hashed and salted
- **Memory Safety:** Sensitive data is cleared from memory when possible
- **No Cloud Sync:** All data remains local to your device

---

## Installation

### Desktop

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd TOTPKotlin+JBCompose
   ```

2. **Build and run:**
   ```bash
   ./gradlew desktopRun
   ```

### Android

1. **Build APK:**
   ```bash
   ./gradlew assembleDebug
   ```

2. **Install on device:**
   ```bash
   adb install app/build/outputs/apk/debug/app-debug.apk
   ```

---

## Usage

### First Time Setup
1. Launch the app
2. Set a master password (minimum 6 characters)
3. This password will be required every time you open the app

### Adding Accounts
1. Tap the "+" button
2. Enter account name and TOTP secret
3. The secret will be encrypted and stored securely

### Using TOTP Codes
1. View your accounts in the main list
2. Tap any account to copy the current TOTP code
3. Codes automatically refresh every 30 seconds

### Settings
- Access settings via the gear icon
- Customize theme colors
- Toggle dark/light mode

---

## Technical Details

### Encryption Implementation
- **Algorithm:** AES-256-GCM
- **Key Derivation:** SHA-256 with random salt
- **File Format:** JSON encrypted with Base64 encoding
- **Password Storage:** Hashed with salt using SHA-256

### Platform Support
- **Android:** API 24+ (Android 7.0+)
- **Desktop:** Windows, macOS, Linux
- **UI Framework:** Jetpack Compose Multiplatform

---

## Requirements

- **Android:** API 24+ (Android 7.0+)
- **Desktop:** Java 11+
- **Build Tools:** Gradle 8.0+

---

## License

MIT License.  
See [LICENSE](LICENSE) for details.

---

## Security Notice

⚠️ **Important:** This is a development project. While encryption is implemented, please:
- Use strong, unique passwords
- Keep your device secure
- Consider this for educational/testing purposes
- Review the code before using for sensitive data

---

## Contributing

Pull requests and issues are welcome!  
Please open an issue for bugs, feature requests, or questions.