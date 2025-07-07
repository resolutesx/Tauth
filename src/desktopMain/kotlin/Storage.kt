package com.example.auth

import kotlinx.serialization.encodeToString
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.json.Json
import java.io.File

private val json = Json { prettyPrint = true }

actual fun saveAccounts(context: Any, accounts: List<Account>, password: String) {
    val file = File("accounts.encrypted")
    val data = json.encodeToString(accounts)
    val encryptedData = SecureStorage.encrypt(data, password)
    file.writeText(encryptedData)
}

actual fun loadAccounts(context: Any, password: String): List<Account> {
    val file = File("accounts.encrypted")
    if (!file.exists()) return emptyList()
    val data = file.readText()
    val decryptedData = SecureStorage.decrypt(data, password)
    return json.decodeFromString(data)
}

actual fun checkForStoredAccounts(context: Any): Boolean {
    val file = File("accounts.encrypted")
    return file.exists()
}