package com.example.auth.storage

import androidx.compose.ui.graphics.Color
import java.util.prefs.Preferences

/**
 * Safely creates a Color from a hex string "#RRGGBB" or "#AARRGGBB".
 * Uses the safe Color constructor to avoid crashes.
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

actual class Settings actual constructor(context: Any?) {
    private val prefs = Preferences.userNodeForPackage(Settings::class.java)

    init {
        // Clear corrupted color data if it exists
        val savedColorHex = prefs.get("themeColor", null)
        if (savedColorHex != null) {
            try {
                hexToColor(savedColorHex)
            } catch (e: Exception) {
                println("Desktop Settings: Clearing corrupted color data: $savedColorHex")
                prefs.remove("themeColor")
            }
        }
    }

    actual var isDarkTheme: Boolean
        get() = prefs.getBoolean("isDarkTheme", false)
        set(value) = prefs.putBoolean("isDarkTheme", value)

    actual var themeColor: Color
        get() {
            val savedColorHex = prefs.get("themeColor", null)
            println("Desktop Settings: Loading themeColor, savedColorHex = $savedColorHex")
            
            return if (savedColorHex != null) {
                try {
                    val color = hexToColor(savedColorHex)
                    println("Desktop Settings: Loaded color = ${color.value.toLong()}")
                    color
                } catch (e: Exception) {
                    println("Desktop Settings: Error loading color, using default: ${e.message}")
                    val defaultColor = hexToColor("#1E88E5") // Blue500 default
                    defaultColor
                }
            } else {
                val defaultColor = hexToColor("#1E88E5") // Blue500 default
                println("Desktop Settings: Using default color = ${defaultColor.value.toLong()}")
                defaultColor
            }
        }
        set(value) {
            // Convert color to hex string for safe storage
            val r = (value.red * 255).toInt()
            val g = (value.green * 255).toInt()
            val b = (value.blue * 255).toInt()
            val hexString = "#%02X%02X%02X".format(r, g, b)
            println("Desktop Settings: Saving themeColor hex = $hexString")
            prefs.put("themeColor", hexString)
        }

    actual var passwordHash: String?
        get() = prefs.get("passwordHash", null)
        set(value) = if (value != null) prefs.put("passwordHash", value) else prefs.remove("passwordHash")
}

actual fun createSettings(context: Any?): Settings {
    return Settings(context)
}

