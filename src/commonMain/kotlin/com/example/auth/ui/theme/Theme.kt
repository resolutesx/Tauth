package com.example.auth.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material.MaterialTheme
import androidx.compose.material.darkColors
import androidx.compose.material.lightColors
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

/**
 * Safely creates a Color from a hex string "#RRGGBB" or "#AARRGGBB".
 * Uses the safe Color constructor to avoid Android crashes.
 */
private fun hexToColor(hex: String): Color {
    val clean = hex.removePrefix("#")
    return when (clean.length) {
        6 -> {
            // RRGGBB format - assume fully opaque
            val r = clean.substring(0, 2).toInt(16)
            val g = clean.substring(2, 4).toInt(16)
            val b = clean.substring(4, 6).toInt(16)
            Color(red = r / 255f, green = g / 255f, blue = b / 255f, alpha = 1f)
        }
        8 -> {
            // AARRGGBB format
            val a = clean.substring(0, 2).toInt(16)
            val r = clean.substring(2, 4).toInt(16)
            val g = clean.substring(4, 6).toInt(16)
            val b = clean.substring(6, 8).toInt(16)
            Color(red = r / 255f, green = g / 255f, blue = b / 255f, alpha = a / 255f)
        }
        else -> error("Invalid color format: $hex")
    }
}

// define your palette using hex strings
private val Blue500    = hexToColor("#1E88E5")
private val Blue700    = hexToColor("#1565C0")
private val CyanA400   = hexToColor("#00E5FF")
private val Teal200    = hexToColor("#03DAC5")
private val LightBg    = hexToColor("#F6F8FB")
private val LightSurf  = hexToColor("#FFFFFF")
private val LightOnBg  = hexToColor("#1A1A1A")
private val DarkBg     = hexToColor("#121212")
private val DarkSurf   = hexToColor("#1E1E1E")
private val DarkOnBg   = hexToColor("#E0E0E0")

@Composable
fun KotlinAuthenticatorTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    themeColor: Color = Blue500,
    content: @Composable () -> Unit
) {
    println("Theme: Received themeColor = ${themeColor.value.toLong()}")
    println("Theme: Received themeColor hex = #${themeColor.value.toULong().toString(16).uppercase()}")
    
    val colors = if (darkTheme) {
        darkColors(
            primary         = themeColor,
            primaryVariant  = Blue700,
            secondary       = Teal200,
            background      = DarkBg,
            surface         = DarkSurf,
            onPrimary       = DarkOnBg,
            onSecondary     = Color.Black,
            onBackground    = DarkOnBg,
            onSurface       = DarkOnBg
        )
    } else {
        lightColors(
            primary         = themeColor,
            primaryVariant  = Blue700,
            secondary       = CyanA400,
            background      = LightBg,
            surface         = LightSurf,
            onPrimary       = Color.White,
            onSecondary     = Color.Black,
            onBackground    = LightOnBg,
            onSurface       = LightOnBg
        )
    }

    MaterialTheme(
        colors  = colors,
        content = content
    )
}
