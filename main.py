#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import time
import threading
from pathlib import Path

def read_setup_status():
    """setup.txtから設定状況を読み取り"""
    try:
        with open('setup.txt', 'r') as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        # ファイルが存在しない場合は0を返す
        with open('setup.txt', 'w') as f:
            f.write('0')
        return 0

def check_internet_connection():
    """インターネット接続をチェック"""
    try:
        import requests
        response = requests.get('https://www.google.com', timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    # 必要なファイルの存在確認
    required_files = ['setup.txt', 'rotate.txt']
    for file in required_files:
        if not os.path.exists(file):
            if file == 'setup.txt':
                with open(file, 'w') as f:
                    f.write('0')
            elif file == 'rotate.txt':
                with open(file, 'w') as f:
                    f.write('0')
    
    setup_status = read_setup_status()
    
    if setup_status == 0:
        # 初回起動 - 初期設定プログラムを実行
        print("初回起動：初期設定プログラムを実行します")
        subprocess.run([sys.executable, 'setup_window.py'])
    else:
        # 2回目以降 - Wi-Fi接続チェック後サイネージ表示
        print("起動中...")
        
        # 接続確認ウィンドウを表示
        import tkinter as tk
        from tkinter import ttk
        
        root = tk.Tk()
        root.geometry("1080x1920")
        root.title("システム起動中")
        root.attributes('-fullscreen', True)
        root.configure(bg='black')
        
        # メッセージ表示
        message_label = tk.Label(
            root, 
            text="起動中...\nネットワーク接続を確認しています...", 
            font=('Arial', 24, 'bold'), 
            fg='white', 
            bg='black'
        )
        message_label.place(relx=0.5, rely=0.5, anchor='center')
        
        root.update()
        
        # Wi-Fi接続確認（最大30秒間リトライ）
        connected = False
        for attempt in range(30):
            if check_internet_connection():
                connected = True
                break
            time.sleep(1)
            message_label.config(text=f"起動中...\nネットワーク接続を確認しています...({attempt+1}/30)")
            root.update()
        
        root.destroy()
        
        if connected:
            # 接続成功 - setup.txtの値を+1してサイネージ表示
            with open('setup.txt', 'w') as f:
                f.write(str(setup_status + 1))
            print("ネットワーク接続確認完了：サイネージプログラムを実行します")
            subprocess.run([sys.executable, 'signage_display.py'])
        else:
            # 接続失敗 - 初期設定ウィンドウを表示
            print("ネットワーク接続失敗：初期設定プログラムを実行します")
            subprocess.run([sys.executable, 'setup_window.py'])

if __name__ == "__main__":
    main()
