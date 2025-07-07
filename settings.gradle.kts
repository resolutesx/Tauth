pluginManagement {
    repositories {
        google()
        gradlePluginPortal()
        mavenCentral()
        maven("https://maven.pkg.jetbrains.space/public/p/compose/dev")
    }
}

rootProject.name = "KotlinAuthenticator"

plugins {
    id("org.gradle.toolchains.foojay-resolver-convention") version "0.8.0"
}
