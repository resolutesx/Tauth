# Project TODO

This document outlines the current status, planned improvements, and future features for the Authenticator application.

## Current Features (Done)

*   **Account Management:**
    *   Add new TOTP accounts (name and secret).
    *   Edit existing TOTP accounts.
    *   Delete TOTP accounts.
    *   Persist accounts to `accounts.json` file.
*   **TOTP Generation:**
    *   Generate 6-digit TOTP codes based on provided secret keys.
    *   Display real-time countdown for TOTP code expiration (30 seconds).
    *   Copy TOTP code to clipboard.
*   **Basic UI:**
    *   List accounts with their generated codes.
    *   Basic dialogs for Add/Edit account.

## UI/UX Improvements (Planned)

*   **Modern Design Language:** Implement a cleaner, more modern visual style using Material Design principles.
*   **Improved Layouts:**
    *   Enhance spacing, alignment, and overall visual hierarchy.
    *   Consider a responsive layout for different window sizes (though primarily desktop).
*   **Visual Feedback:** Provide better visual feedback for actions (e.g., "Copied!" message).
*   **Error Handling UI:** Display user-friendly error messages for invalid secret keys or other issues.
*   **Empty State:** Improve the "No accounts yet" message and call to action.
*   **Theming:** Basic light/dark theme support.

## New Features (Planned)

*   **Account Search/Filter:** Allow users to quickly find accounts by name.
*   **Secret Key Input Validation:** Validate secret key format (e.g., Base32) during input.
*   **QR Code Scanning (Future Consideration):** Ability to add accounts by scanning a QR code (requires camera access, more complex for desktop).
*   **Account Reordering:** Allow users to reorder accounts in the list.
*   **Export/Import Accounts:** Functionality to export and import accounts (e.g., encrypted JSON).
*   **Settings/Preferences:**
    *   Option to change TOTP time step (default 30s).
    *   Option to change TOTP digit length (default 6).
*   **Security Enhancements:**
    *   Password protection for the application.
    *   Encryption of `accounts.json` (beyond `prettyPrint`).

## Code Quality & Production Readiness (Planned)

*   **Refactor UI Components:** Break down `Main.kt` into smaller, more manageable Composable functions.
*   **Robust Error Handling:** Implement comprehensive error handling for file operations and TOTP generation.
*   **Testing:** Add unit and integration tests for core logic and UI components.
*   **Dependency Management:** Review and update dependencies as needed.
*   **Documentation:** Add inline comments for complex logic and update project README.