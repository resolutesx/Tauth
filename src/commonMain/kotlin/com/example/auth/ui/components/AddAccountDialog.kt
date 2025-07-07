package com.example.auth.ui.components

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.VpnKey
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusDirection
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.DialogProperties
import com.example.auth.Account
import com.example.auth.Totp

@Composable
fun AddAccountDialog(
    onDismiss: () -> Unit,
    onConfirm: (Account) -> Unit
) {
    var name by remember { mutableStateOf("") }
    var secret by remember { mutableStateOf("") }
    var isSecretValid by remember { mutableStateOf(true) }
    val focusManager = LocalFocusManager.current
    
    val isNameValid = name.trim().isNotBlank()
    val isFormValid = isNameValid && secret.trim().isNotBlank() && isSecretValid
    
    // Validate secret on change
    LaunchedEffect(secret) {
        if (secret.isNotEmpty()) {
            isSecretValid = Totp.isValidSecret(secret.trim())
        }
    }
    
    AlertDialog(
        onDismissRequest = onDismiss,
        shape = RoundedCornerShape(16.dp),
        backgroundColor = MaterialTheme.colors.surface,
        modifier = Modifier
            .width(500.dp)
            .wrapContentHeight(),
        properties = DialogProperties(usePlatformDefaultWidth = false),
        title = {
            Text(
                text = "Add Account",
                fontSize = 22.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colors.onSurface
            )
        },
        text = {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 8.dp)
            ) {
                // Subtitle
                Text(
                    text = "Enter your account details to generate TOTP codes",
                    fontSize = 14.sp,
                    color = MaterialTheme.colors.onSurface.copy(alpha = 0.7f),
                    modifier = Modifier.padding(bottom = 16.dp)
                )
                
                // Account Name Field
                OutlinedTextField(
                    value = name,
                    onValueChange = { name = it },
                    label = { Text("Account Name") },
                    placeholder = { Text("e.g., Google, GitHub") },
                    leadingIcon = {
                        Icon(
                            Icons.Default.Person,
                            contentDescription = "Account name",
                            tint = MaterialTheme.colors.primary
                        )
                    },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth(),
                    colors = TextFieldDefaults.outlinedTextFieldColors(
                        focusedBorderColor = MaterialTheme.colors.primary,
                        focusedLabelColor = MaterialTheme.colors.primary
                    ),
                    keyboardOptions = KeyboardOptions(imeAction = ImeAction.Next),
                    keyboardActions = KeyboardActions(
                        onNext = { focusManager.moveFocus(FocusDirection.Down) }
                    )
                )
                
                Spacer(modifier = Modifier.height(16.dp))
                
                // Secret Key Field
                OutlinedTextField(
                    value = secret,
                    onValueChange = {
                        secret = it.trim()
                        isSecretValid = secret.isEmpty() || Totp.isValidSecret(secret)
                    },
                    label = { Text("Secret Key") },
                    placeholder = { Text("Paste your TOTP secret key") },
                    leadingIcon = {
                        Icon(
                            Icons.Default.VpnKey,
                            contentDescription = "Secret key",
                            tint = if (isSecretValid) MaterialTheme.colors.primary else MaterialTheme.colors.error
                        )
                    },
                    isError = !isSecretValid && secret.isNotEmpty(),
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth(),
                    colors = TextFieldDefaults.outlinedTextFieldColors(
                        focusedBorderColor = if (isSecretValid) MaterialTheme.colors.primary else MaterialTheme.colors.error,
                        focusedLabelColor = if (isSecretValid) MaterialTheme.colors.primary else MaterialTheme.colors.error
                    ),
                    keyboardOptions = KeyboardOptions(imeAction = ImeAction.Done),
                    keyboardActions = KeyboardActions(
                        onDone = { focusManager.clearFocus() }
                    )
                )
                
                // Simple error message
                if (!isSecretValid && secret.isNotEmpty()) {
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "Invalid secret key format",
                        color = MaterialTheme.colors.error,
                        fontSize = 12.sp,
                        modifier = Modifier.padding(start = 16.dp)
                    )
                }
            }
        },
        confirmButton = {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(8.dp),
                horizontalArrangement = Arrangement.End
            ) {
                TextButton(
                    onClick = onDismiss,
                    modifier = Modifier.padding(end = 8.dp)
                ) {
                    Text("Cancel")
                }
                
                Button(
                    onClick = { onConfirm(Account(name.trim(), secret.trim())) },
                    enabled = isFormValid,
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text("Add Account")
                }
            }
        },
        dismissButton = {}
    )
}