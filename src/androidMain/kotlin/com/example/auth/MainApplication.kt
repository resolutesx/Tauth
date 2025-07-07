package com.example.auth

import android.app.Application
import android.content.Context

class MainApplication : Application() {
    companion object {
        private var _applicationContext: Context? = null
        val applicationContext: Context
            get() = _applicationContext ?: throw IllegalStateException("Application context not initialized")
    }

    override fun onCreate() {
        super.onCreate()
        _applicationContext = this
    }
}
