package com.example.auth

import kotlinx.datetime.Clock
import org.apache.commons.codec.binary.Base32
import javax.crypto.Mac
import javax.crypto.spec.SecretKeySpec
import kotlin.experimental.and

object Totp {
    private const val T0 = 0L
    private const val X = 30L
    private const val a = "HmacSHA1"

    fun generate(secret: String): String {
        val c = (Clock.System.now().epochSeconds - T0) / X
        val h = hmac(key = decode(secret), msg = c.toByteArray())
        val o = (h.last() and 0x0f).toInt()
        val dbc = toInt(h.sliceArray(o..o + 3))
        val hotp = (dbc and 0x7fffffff) % 1000000
        return "%06d".format(hotp)
    }

    private fun hmac(key: ByteArray, msg: ByteArray): ByteArray {
        val h = Mac.getInstance(a)
        h.init(SecretKeySpec(key, a))
        return h.doFinal(msg)
    }

    private fun toInt(b: ByteArray): Int {
        return b.fold(0) { i, byte -> (i shl 8) or (byte.toInt() and 0xff) }
    }

    private fun Long.toByteArray(): ByteArray {
        var l = this
        val b = ByteArray(8)
        for (i in 7 downTo 0) {
            b[i] = (l and 0xff).toByte()
            l = l shr 8
        }
        return b
    }

    private fun decode(s: String): ByteArray {
        return Base32().decode(s)
    }

    fun isValidSecret(secret: String): Boolean {
        return try {
            decode(secret)
            true
        } catch (e: IllegalArgumentException) {
            false
        }
    }
}
