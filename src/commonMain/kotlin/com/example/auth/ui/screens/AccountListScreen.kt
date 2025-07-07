package com.example.auth.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Settings
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.example.auth.Account
import com.example.auth.Storage
import com.example.auth.storage.createSettings
import com.example.auth.ui.components.AccountCard
import com.example.auth.ui.components.AddAccountDialog
import com.example.auth.ui.components.PasswordDialog
import kotlinx.coroutines.launch

@Composable
fun AccountListScreen(context: Any, onSettingsClick: () -> Unit) {
    var accounts by remember { mutableStateOf<List<Account>>(emptyList()) }
    var showAddAccountDialog by remember { mutableStateOf(false) }
    var showPasswordDialog by remember { mutableStateOf(false) }
    val scaffoldState = rememberScaffoldState()
    val scope = rememberCoroutineScope()
    val settings = remember { createSettings(context) }

    // Load accounts on first launch
    LaunchedEffect(Unit) {
        if (Storage.hasStoredAccounts(context)) {
            // We need to get the password from the user
            showPasswordDialog = true
        }
    }

    Scaffold(
        scaffoldState = scaffoldState,
        topBar = {
            TopAppBar(
                title = { Text("Accounts") },
                actions = {
                    IconButton(onClick = onSettingsClick) {
                        Icon(Icons.Default.Settings, contentDescription = "Settings")
                    }
                },
                backgroundColor = MaterialTheme.colors.primary,
                contentColor = Color.White
            )
        },
        floatingActionButton = {
            FloatingActionButton(
                onClick = { showAddAccountDialog = true },
                backgroundColor = MaterialTheme.colors.primary
            ) {
                Icon(Icons.Default.Add, contentDescription = "Add Account")
            }
        }
    ) { paddingValues ->
        LazyColumn(
            modifier = Modifier.padding(paddingValues),
            contentPadding = PaddingValues(8.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(accounts) { account ->
                AccountCard(account = account, scaffoldState = scaffoldState)
            }
        }

        if (showAddAccountDialog) {
            AddAccountDialog(
                onDismiss = { showAddAccountDialog = false },
                onConfirm = { newAccount ->
                    val newAccounts = accounts + newAccount
                    // For now, we'll use a simple approach - store the password temporarily
                    // In a real app, you'd want to use a more secure method
                    val tempPassword = "temp_password" // This should be handled more securely
                    Storage.save(context, newAccounts, tempPassword)
                    accounts = newAccounts
                    showAddAccountDialog = false
                    scope.launch {
                        scaffoldState.snackbarHostState.showSnackbar("Account added successfully")
                    }
                }
            )
        }

        if (showPasswordDialog) {
            PasswordDialog(
                isSetup = false,
                onPasswordEntered = { password ->
                    try {
                        val loadedAccounts = Storage.load(context, password)
                        accounts = loadedAccounts
                        showPasswordDialog = false
                    } catch (e: Exception) {
                        // Wrong password - dialog will show error
                        scope.launch {
                            scaffoldState.snackbarHostState.showSnackbar("Incorrect password")
                        }
                    }
                },
                onDismiss = {
                    showPasswordDialog = false
                }
            )
        }
    }
}
