package com.example.auth

import androidx.compose.runtime.*
import androidx.compose.ui.window.Window
import androidx.compose.ui.window.application
import com.example.auth.storage.createSettings
import com.example.auth.ui.screens.AccountListScreen
import com.example.auth.ui.screens.SettingsScreen
import com.example.auth.ui.theme.KotlinAuthenticatorTheme
import com.example.auth.viewmodel.SettingsViewModel

fun main() = application {
    val settings = remember { createSettings(null) }
    val settingsViewModel = remember { SettingsViewModel(settings) }
    var showSettings by remember { mutableStateOf(false) }

    Window(onCloseRequest = ::exitApplication, title = "Authenticator") {
        KotlinAuthenticatorTheme(
            darkTheme = settingsViewModel.isDarkTheme,
            themeColor = settingsViewModel.themeColor
        ) {
            if (showSettings) {
                SettingsScreen(
                    settingsViewModel = settingsViewModel,
                    onBack = { showSettings = false }
                )
            } else {
                AccountListScreen(context = Any(), onSettingsClick = { showSettings = true })
            }
        }
    }
}
