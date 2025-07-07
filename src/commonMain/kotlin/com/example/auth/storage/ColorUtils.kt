package com.example.auth.storage

import androidx.compose.ui.graphics.Color

// Safe Color extension function
fun Color.Companion.safe(hex: Long): Color {
    return try {
        Color(hex.toULong())
    } catch (e: Exception) {
        Color.Black // Fallback color
    }
}
