#!/usr/bin/env python3
"""
构建桌面应用脚本
使用方法: python build_desktop.py
"""
import subprocess
import sys
import os

def install_pyinstaller():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def build():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, "app.py")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=互动小说引擎",
        "--onefile",
        "--windowed",
        "--noconfirm",
        "--clean",
        "--add-data", f"{os.path.join(script_dir, 'utils')};utils",
        "--add-data", f"{os.path.join(script_dir, 'data')};data",
        "--add-data", f"{os.path.join(script_dir, '.env')};.",
        "--hidden-import", "streamlit",
        "--hidden-import", "langchain",
        "--hidden-import", "langchain_openai",
        "--hidden-import", "langchain_community",
        "--hidden-import", "chromadb",
        "--hidden-import", "dashscope",
        "--collect-all", "streamlit",
        "--collect-all", "langchain",
        app_path,
    ]

    print("🔨 正在构建桌面应用...")
    print(f"命令: {' '.join(cmd)}")
    print()

    subprocess.check_call(cmd)

    print()
    print("✅ 构建完成!")
    print(f"📦 输出目录: {os.path.join(script_dir, 'dist')}")
    print("   可执行文件在 dist/ 目录下")

if __name__ == "__main__":
    install_pyinstaller()
    build()
