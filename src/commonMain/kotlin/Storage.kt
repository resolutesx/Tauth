package com.example.auth

import kotlinx.serialization.Serializable
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

expect fun saveAccounts(context: Any, accounts: List<Account>, password: String)
expect fun loadAccounts(context: Any, password: String): List<Account>
expect fun checkForStoredAccounts(context: Any): Boolean

object Storage {
    private val json = Json { prettyPrint = true }

    fun save(context: Any, accounts: List<Account>, password: String) {
        saveAccounts(context, accounts, password)
    }

    fun load(context: Any, password: String): List<Account> {
        return loadAccounts(context, password)
    }
    
    fun hasStoredAccounts(context: Any): Boolean {
        return checkForStoredAccounts(context)
    }
}
