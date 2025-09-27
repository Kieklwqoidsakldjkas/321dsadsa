@echo off
REM Скрипт для исправления проблем с установкой зависимостей

echo 🔧 Исправление проблем с установкой зависимостей
echo ================================================

REM Обновление pip и setuptools
echo 📦 Обновление pip и setuptools...
python -m pip install --upgrade pip setuptools wheel

REM Установка Microsoft Visual C++ Build Tools (если нужно)
echo 🔧 Проверка Visual C++ Build Tools...
python -c "import distutils.util; print('Build tools:', distutils.util.get_platform())" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️ Возможно, нужны Visual C++ Build Tools
    echo 💡 Скачайте с: https://visualstudio.microsoft.com/visual-cpp-build-tools/
)

REM Установка упрощенных зависимостей
echo 📚 Установка упрощенных зависимостей...
pip install -r requirements-simple.txt

REM Проверка установки
echo 🔍 Проверка установки...
python -c "import aiogram, aiohttp, aiofiles, psutil, requests; print('✅ Все пакеты установлены успешно')"

if %errorlevel% neq 0 (
    echo ❌ Проблемы с установкой
    echo.
    echo 💡 Попробуйте следующие решения:
    echo 1. Установите Visual C++ Build Tools
    echo 2. Запустите от имени администратора
    echo 3. Используйте conda вместо pip
    echo 4. Установите пакеты по одному
) else (
    echo ✅ Установка завершена успешно!
    echo 🚀 Теперь можно запустить: run.bat
)

pause
