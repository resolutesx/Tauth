package com.example.auth.ui.components

import androidx.compose.foundation.layout.*
import androidx.compose.material.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.auth.Account
import com.example.auth.Totp
import kotlinx.coroutines.delay
import java.awt.Toolkit
import java.awt.datatransfer.StringSelection

@Composable
fun AccountItemCard(account: Account, onEdit: (Account) -> Unit, onDelete: (Account) -> Unit) {
    var code by remember { mutableStateOf("") }
    var remainingTime by remember { mutableStateOf(0L) }
    var showCopiedMessage by remember { mutableStateOf(false) }

    LaunchedEffect(account) {
        while (true) {
            code = Totp.generate(account.secret)
            remainingTime = 30 - (System.currentTimeMillis() / 1000) % 30
            delay(1000)
        }
    }

    Card(
        modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
        elevation = 4.dp
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(account.name, style = MaterialTheme.typography.h6)
            Spacer(modifier = Modifier.height(8.dp))
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(code, style = MaterialTheme.typography.h4)
                Row {
                    Button(onClick = {
                        val clipboard = Toolkit.getDefaultToolkit().systemClipboard
                        clipboard.setContents(StringSelection(code), null)
                        showCopiedMessage = true
                    }) {
                        Text("Copy")
                    }
                    Spacer(modifier = Modifier.width(8.dp))
                    Button(onClick = { onEdit(account) }) {
                        Text("Edit")
                    }
                    Spacer(modifier = Modifier.width(8.dp))
                    Button(onClick = { onDelete(account) }) {
                        Text("Delete")
                    }
                }
                CircularProgressIndicator(
                    progress = remainingTime / 30f,
                    modifier = Modifier.size(24.dp)
                )
            }
            if (showCopiedMessage) {
                LaunchedEffect(Unit) {
                    delay(2000) // Show message for 2 seconds
                    showCopiedMessage = false
                }
                Text("Copied!", style = MaterialTheme.typography.caption)
            }
        }
    }
}
