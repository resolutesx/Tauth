package com.example.auth

import kotlinx.serialization.encodeToString
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.json.Json
import java.io.File
import android.content.Context

private val json = Json { prettyPrint = true }

actual fun saveAccounts(context: Any, accounts: List<Account>, password: String) {
    val ctx = context as Context
    val file = File(ctx.filesDir, "accounts.encrypted")
    val data = json.encodeToString(accounts)
    val encryptedData = SecureStorage.encrypt(data, password)
    file.writeText(encryptedData)
}

actual fun loadAccounts(context: Any, password: String): List<Account> {
    val ctx = context as Context
    val file = File(ctx.filesDir, "accounts.encrypted")
    if (!file.exists()) return emptyList()
    val encryptedData = file.readText()
    val decryptedData = SecureStorage.decrypt(encryptedData, password)
    return json.decodeFromString<List<Account>>(decryptedData)
}

actual fun checkForStoredAccounts(context: Any): Boolean {
    val ctx = context as Context
    val file = File(ctx.filesDir, "accounts.encrypted")
    return file.exists()
}