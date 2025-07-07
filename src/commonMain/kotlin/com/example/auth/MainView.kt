package com.example.auth

import androidx.compose.runtime.*
import com.example.auth.storage.createSettings
import com.example.auth.ui.screens.AccountListScreen
import com.example.auth.ui.screens.SettingsScreen
import com.example.auth.ui.theme.KotlinAuthenticatorTheme
import com.example.auth.viewmodel.SettingsViewModel
import com.example.auth.ui.components.PasswordDialog

@Composable
fun MainView(context: Any) {
    val settings = remember { createSettings(context) }
    val settingsViewModel = remember { SettingsViewModel(settings) }
    var showSettings by remember { mutableStateOf(false) }
    var isAuthenticated by remember { mutableStateOf(false) }
    var showPasswordDialog by remember { mutableStateOf(false) }
    var isPasswordSetup by remember { mutableStateOf(false) }

    // Check if we need to authenticate
    LaunchedEffect(Unit) {
        val hasStoredAccounts = Storage.hasStoredAccounts(context)
        val hasPasswordHash = settings.passwordHash != null
        
        if (hasStoredAccounts && hasPasswordHash) {
            // Need to authenticate
            showPasswordDialog = true
            isPasswordSetup = false
        } else if (!hasStoredAccounts && !hasPasswordHash) {
            // First time setup
            showPasswordDialog = true
            isPasswordSetup = true
        } else {
            // No stored accounts, no need for password
            isAuthenticated = true
        }
    }

    KotlinAuthenticatorTheme(
        darkTheme = settingsViewModel.isDarkTheme,
        themeColor = settingsViewModel.themeColor
    ) {
        if (showPasswordDialog) {
            PasswordDialog(
                isSetup = isPasswordSetup,
                onPasswordEntered = { password ->
                    if (isPasswordSetup) {
                        // Set up new password
                        val passwordHash = PasswordManager.hashPassword(password)
                        settings.passwordHash = passwordHash
                        isAuthenticated = true
                        showPasswordDialog = false
                    } else {
                        // Verify existing password
                        val storedHash = settings.passwordHash
                        if (storedHash != null && PasswordManager.verifyPassword(password, storedHash)) {
                            isAuthenticated = true
                            showPasswordDialog = false
                        } else {
                            // Wrong password - dialog will show error
                            // For now, just keep dialog open
                        }
                    }
                },
                onDismiss = {
                    // Don't allow dismissal during authentication
                    if (!isAuthenticated) return@PasswordDialog
                    showPasswordDialog = false
                }
            )
        }

        if (isAuthenticated) {
            if (showSettings) {
                SettingsScreen(
                    settingsViewModel = settingsViewModel,
                    onBack = { showSettings = false }
                )
            } else {
                AccountListScreen(context = context, onSettingsClick = { showSettings = true })
            }
        }
    }
}
