package com.example.auth.ui.components

import androidx.compose.foundation.layout.*
import androidx.compose.material.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ContentCopy
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.auth.Account
import com.example.auth.Totp
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

@Composable
fun AccountCard(account: Account, scaffoldState: ScaffoldState) {
    val clipboardManager = LocalClipboardManager.current
    var totp by remember { mutableStateOf(Totp.generate(account.secret)) }
    var progress by remember { mutableStateOf(0f) }
    val scope = rememberCoroutineScope()

    LaunchedEffect(Unit) {
        while (true) {
            val remaining = 30 - (System.currentTimeMillis() / 1000) % 30
            progress = remaining / 30f
            if (remaining == 30L) {
                totp = Totp.generate(account.secret)
            }
            delay(1000)
        }
    }



    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp, horizontal = 8.dp),
        elevation = 4.dp
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = account.name,
                style = MaterialTheme.typography.h6
            )
            Spacer(modifier = Modifier.height(8.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = totp,
                    fontSize = 24.sp,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.weight(1f))
                IconButton(onClick = {
                    clipboardManager.setText(AnnotatedString(totp))
                    scope.launch {
                        scaffoldState.snackbarHostState.showSnackbar("Copied Code")
                    }
                }) {
                    Icon(Icons.Default.ContentCopy, contentDescription = "Copy Code")
                }
            }
            Spacer(modifier = Modifier.height(8.dp))
            LinearProgressIndicator(
                progress = progress,
                modifier = Modifier.fillMaxWidth()
            )
        }
    }
}
