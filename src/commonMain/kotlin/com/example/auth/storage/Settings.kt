package com.example.auth.storage

import androidx.compose.ui.graphics.Color

expect class Settings(context: Any? = null) {
    var isDarkTheme: Boolean
    var themeColor: Color
    var passwordHash: String?
}

// Factory function to create Settings instance
expect fun createSettings(context: Any?): Settings
