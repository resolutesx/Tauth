package com.example.auth

import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.json.Json
import org.apache.commons.codec.binary.Base64
import java.security.MessageDigest
import java.security.SecureRandom

@Serializable
private data class PasswordHash(
    val salt: String,
    val hash: String
)

object PasswordManager {
    private val json = Json { prettyPrint = true }
    
    /**
     * Creates a password hash for storage
     */
    fun hashPassword(password: String): String {
        val salt = ByteArray(32)
        SecureRandom().nextBytes(salt)
        
        val hash = hashPasswordWithSalt(password, salt)
        val passwordHash = PasswordHash(
            salt = Base64.encodeBase64String(salt),
            hash = Base64.encodeBase64String(hash)
        )
        
        return json.encodeToString(passwordHash)
    }
    
    /**
     * Verifies a password against a stored hash
     */
    fun verifyPassword(password: String, storedHash: String): Boolean {
        val passwordHash = json.decodeFromString<PasswordHash>(storedHash)
        val salt = Base64.decodeBase64(passwordHash.salt)
        val storedHashBytes = Base64.decodeBase64(passwordHash.hash)
        
        val computedHash = hashPasswordWithSalt(password, salt)
        return storedHashBytes.contentEquals(computedHash)
    }
    
    private fun hashPasswordWithSalt(password: String, salt: ByteArray): ByteArray {
        val digest = MessageDigest.getInstance("SHA-256")
        return digest.digest((password + String(salt)).toByteArray())
    }
} 