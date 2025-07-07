package com.example.auth

import kotlinx.serialization.Serializable

@Serializable
data class Account(
    val name: String,
    val secret: String
)
