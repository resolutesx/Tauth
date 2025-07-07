package com.example.auth.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.border
import androidx.compose.material.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.auth.viewmodel.SettingsViewModel

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

@Composable
fun SettingsScreen(settingsViewModel: SettingsViewModel, onBack: () -> Unit) {
    val colors = listOf(
        hexToColor("#1E88E5"), // Blue500 (default)
        Color.Blue,        // Safe blue
        Color.Cyan,        // Safe cyan  
        Color.Green,       // Safe green
        Color.Yellow,      // Safe yellow
        Color.Magenta,     // Safe magenta
        Color.Red,         // Safe red
        Color.DarkGray,    // Safe dark gray
        Color.Gray,        // Safe gray
        Color.LightGray,   // Safe light gray
        Color.Black        // Safe black
    )

    // Debug current theme color
    println("SettingsScreen: Current themeColor = ${settingsViewModel.themeColor.value.toLong()}")
    println("SettingsScreen: Current themeColor hex = #${settingsViewModel.themeColor.value.toULong().toString(16).uppercase()}")

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Settings") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                backgroundColor = MaterialTheme.colors.primary,
                contentColor = Color.White
            )
        }
    ) {
        Column(modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colors.background)
            .padding(0.dp)) {
            // App version section
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 16.dp, start = 16.dp, end = 16.dp),
                elevation = 0.dp,
                backgroundColor = MaterialTheme.colors.surface
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("App Version", fontSize = 12.sp, color = Color.Gray)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("0.1 Dev Alpha", fontSize = 14.sp, color = MaterialTheme.colors.onSurface)
                }
            }
            Spacer(modifier = Modifier.height(16.dp))
            // Settings section
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp),
                elevation = 0.dp,
                backgroundColor = MaterialTheme.colors.surface
            ) {
                Column {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(56.dp)
                            .padding(horizontal = 16.dp)
                    ) {
                        Text("Dark Mode", fontSize = 16.sp, color = MaterialTheme.colors.onSurface)
                        Spacer(modifier = Modifier.weight(1f))
                        Switch(
                            checked = settingsViewModel.isDarkTheme,
                            onCheckedChange = { settingsViewModel.updateDarkTheme(it) }
                        )
                    }
                    Divider()
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 8.dp)
                    ) {
                        Text("Theme Color", fontSize = 16.sp, color = MaterialTheme.colors.onSurface, modifier = Modifier.padding(start = 16.dp, bottom = 8.dp))
                        LazyRow(
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                            modifier = Modifier.padding(start = 16.dp, end = 16.dp)
                        ) {
                            items(colors) { color ->
                                Box(
                                    modifier = Modifier
                                        .size(40.dp)
                                        .clip(CircleShape)
                                        .background(color)
                                        .clickable { settingsViewModel.updateThemeColor(color) }
                                        .border(
                                            width = if (settingsViewModel.themeColor.value == color.value) 3.dp else 1.dp,
                                            color = if (settingsViewModel.themeColor.value == color.value) MaterialTheme.colors.primary else Color.LightGray,
                                            shape = CircleShape
                                        )
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}