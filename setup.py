from cx_Freeze import setup, Executable
import sys
import os

# Base belirleme
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Eğer GUI uygulamasıysa kullanılır, değilse 'None' bırakın

# Ek data dosyaları
additional_files = [
    ("icon.ico", "icon.ico"),
    ("libs", "libs"),
    ("ui", "ui"),
    ("coindashboard", "coindashboard")
]

# requirements.txt içindeki bağımlılıkları yükleyin
with open("requirements.txt") as f:
    required_packages = f.read().splitlines()

# Uygulama ayarları
executables = [
    Executable(
        script="app.py",
        base=base,
        icon="icon.ico",
        target_name="crypto-dashboard"
    )
]

# Setup fonksiyonu
setup(
    name="crypto-dashboard",
    version="1.0-1",
    description="A comprehensive dashboard for monitoring cryptocurrency markets.",
    options={
        "build_exe": {
            "packages": [],
            "include_files": additional_files,
            "includes": required_packages
        }
    },
    executables=executables
)
