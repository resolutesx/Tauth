package com.example.auth

import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.json.Json
import org.apache.commons.codec.binary.Base64
import javax.crypto.Cipher
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec
import javax.crypto.spec.SecretKeySpec
import java.security.MessageDigest
import java.security.SecureRandom

@Serializable
private data class EncryptedData(
    val iv: String,
    val data: String
)

object SecureStorage {
    private val json = Json { prettyPrint = true }
    private const val ALGORITHM = "AES/GCM/NoPadding"
    private const val KEY_SIZE = 256
    private const val IV_SIZE = 12
    private const val TAG_LENGTH = 128
    
    /**
     * Derives a secret key from a password using PBKDF2
     */
    private fun deriveKey(password: String, salt: ByteArray): SecretKey {
        val digest = MessageDigest.getInstance("SHA-256")
        val hash = digest.digest((password + String(salt)).toByteArray())
        return SecretKeySpec(hash, "AES")
    }
    
    /**
     * Encrypts data using AES-GCM
     */
    fun encrypt(data: String, password: String): String {
        val salt = ByteArray(16)
        SecureRandom().nextBytes(salt)
        
        val iv = ByteArray(IV_SIZE)
        SecureRandom().nextBytes(iv)
        
        val key = deriveKey(password, salt)
        val cipher = Cipher.getInstance(ALGORITHM)
        val gcmSpec = GCMParameterSpec(TAG_LENGTH, iv)
        cipher.init(Cipher.ENCRYPT_MODE, key, gcmSpec)
        
        val encryptedData = cipher.doFinal(data.toByteArray())
        val encryptedDataWithSalt = salt + encryptedData
        
        val result = EncryptedData(
            iv = Base64.encodeBase64String(iv),
            data = Base64.encodeBase64String(encryptedDataWithSalt)
        )
        
        return json.encodeToString(result)
    }
    
    /**
     * Decrypts data using AES-GCM
     */
    fun decrypt(encryptedString: String, password: String): String {
        val encryptedData = json.decodeFromString<EncryptedData>(encryptedString)
        
        val iv = Base64.decodeBase64(encryptedData.iv)
        val encryptedDataWithSalt = Base64.decodeBase64(encryptedData.data)
        
        val salt = encryptedDataWithSalt.sliceArray(0 until 16)
        val encryptedDataOnly = encryptedDataWithSalt.sliceArray(16 until encryptedDataWithSalt.size)
        
        val key = deriveKey(password, salt)
        val cipher = Cipher.getInstance(ALGORITHM)
        val gcmSpec = GCMParameterSpec(TAG_LENGTH, iv)
        cipher.init(Cipher.DECRYPT_MODE, key, gcmSpec)
        
        val decryptedData = cipher.doFinal(encryptedDataOnly)
        return String(decryptedData)
    }
    
    /**
     * Checks if the provided password can decrypt the stored data
     */
    fun isValidPassword(encryptedString: String, password: String): Boolean {
        return try {
            decrypt(encryptedString, password)
            true
        } catch (e: Exception) {
            false
        }
    }
} 