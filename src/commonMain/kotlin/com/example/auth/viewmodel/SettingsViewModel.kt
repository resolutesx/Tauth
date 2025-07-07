package com.example.auth.viewmodel

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.graphics.Color
import com.example.auth.storage.Settings

class SettingsViewModel(private val settings: Settings) {
    var isDarkTheme by mutableStateOf(settings.isDarkTheme)
        private set

    var themeColor by mutableStateOf(settings.themeColor)
        private set

    init {
        println("SettingsViewModel: Initial themeColor = ${themeColor.value.toLong()}")
        println("SettingsViewModel: Initial themeColor hex = #${themeColor.value.toULong().toString(16).uppercase()}")
    }

    fun updateDarkTheme(isDark: Boolean) {
        isDarkTheme = isDark
        settings.isDarkTheme = isDark
    }

    fun updateThemeColor(color: Color) {
        println("SettingsViewModel: Updating themeColor to ${color.value.toLong()}")
        println("SettingsViewModel: New themeColor hex = #${color.value.toULong().toString(16).uppercase()}")
        themeColor = color
        settings.themeColor = color
    }
}
