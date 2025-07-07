package com.example.auth

import androidx.compose.runtime.*
import androidx.compose.ui.window.Window
import androidx.compose.ui.window.application
import com.example.auth.storage.Settings
import com.example.auth.ui.screens.AccountListScreen
import com.example.auth.ui.screens.SettingsScreen
import com.example.auth.ui.theme.KotlinAuthenticatorTheme
import com.example.auth.viewmodel.SettingsViewModel

fun main() = application {
    val settings = remember { Settings() }
    val settingsViewModel = remember { SettingsViewModel(settings) }
    var showSettings by remember { mutableStateOf(false) }

    val darkTheme by remember(settingsViewModel.isDarkTheme) { mutableStateOf(settingsViewModel.isDarkTheme) }
    val themeColor by remember(settingsViewModel.themeColor) { mutableStateOf(settingsViewModel.themeColor) }

    Window(onCloseRequest = ::exitApplication, title = "Authenticator") {
        KotlinAuthenticatorTheme(
            darkTheme = darkTheme,
            themeColor = themeColor
        ) {
            if (showSettings) {
                SettingsScreen(
                    settingsViewModel = settingsViewModel,
                    onBack = { showSettings = false }
                )
            } else {
                AccountListScreen(onSettingsClick = { showSettings = true })
            }
        }
    }
}
