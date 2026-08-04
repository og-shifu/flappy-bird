[app]

# Application name
title = Flappy Bird

# Package name
package.name = flappybird

# Package domain
package.domain = org.flappybird

# Folder containing main.py
source.dir = .

# Files included in the APK
source.include_exts = py,png,jpg,jpeg,wav,mp3

# Version
version = 1.0

# Python + Kivy
requirements = python3,kivy

# Phone orientation
orientation = portrait

# Fullscreen
fullscreen = 1


[buildozer]

# Log level
log_level = 2

# Don't warn about root
warn_on_root = 1


[android]

# Automatically accept SDK license
android.accept_sdk_license = True


# Android API
android.api = 35

# Minimum Android version
android.minapi = 23

# 64-bit Android
android.archs = arm64-v8a
