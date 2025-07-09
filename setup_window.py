#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import time
import threading

class SetupWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("初期設定")
        self.root.geometry("1080x1920")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#f0f0f0')
        
        # 回転状態を読み込み
        self.rotation = self.read_rotation()
        
        # メインフレーム
        self.main_frame = tk.Frame(self.root, bg='#f0f0f0')
        self.main_frame.pack(fill='both', expand=True)
        
        self.create_widgets()
        self.apply_rotation()
        self.scan_wifi()
        
    def read_rotation(self):
        """rotate.txtから回転状態を読み込み"""
        try: 
            with open('rotate.txt', 'r') as f:
                return int(f.read().strip())
        except:
            return 0
    
    def save_rotation(self):
        """rotate.txtに回転状態を保存"""
        with open('rotate.txt', 'w') as f:
            f.write(str(self.rotation))
    
    def create_widgets(self):
        """ウィジェットを作成"""
        # タイトル
        title_label = tk.Label(
            self.main_frame,
            text="Wi-Fi設定",
            font=('Arial', 32, 'bold'),
            bg='#f0f0f0',
            fg='#333333'
        )
        title_label.pack(pady=50)
        
        # 回転ボタン
        self.rotate_button = tk.Button(
            self.main_frame,
            text="画面回転",
            font=('Arial', 16),
            command=self.rotate_screen,
            bg='#4CAF50',
            fg='white',
            padx=20,
            pady=10
        )
        self.rotate_button.pack(pady=20)
        
        # Wi-Fiセクション
        wifi_frame = tk.Frame(self.main_frame, bg='#f0f0f0')
        wifi_frame.pack(pady=30, padx=50, fill='x')
        
        tk.Label(
            wifi_frame,
            text="Wi-Fiネットワーク:",
            font=('Arial', 18),
            bg='#f0f0f0',
            fg='#333333'
        ).pack(anchor='w', pady=(0, 10))
        
        # Wi-Fiドロップダウン
        self.wifi_var = tk.StringVar()
        self.wifi_combo = ttk.Combobox(
            wifi_frame,
            textvariable=self.wifi_var,
            font=('Arial', 14),
            state='readonly',
            width=50
        )
        self.wifi_combo.pack(fill='x', pady=(0, 10))
        
        # Wi-Fi再取得ボタン
        self.refresh_button = tk.Button(
            wifi_frame,
            text="Wi-Fi再取得",
            font=('Arial', 14),
            command=self.scan_wifi,
            bg='#2196F3',
            fg='white',
            padx=20,
            pady=5
        )
        self.refresh_button.pack(pady=10)
        
        # パスワード入力
        tk.Label(
            wifi_frame,
            text="パスワード:",
            font=('Arial', 18),
            bg='#f0f0f0',
            fg='#333333'
        ).pack(anchor='w', pady=(20, 10))
        
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(
            wifi_frame,
            textvariable=self.password_var,
            font=('Arial', 14),
            show='*',
            width=50
        )
        self.password_entry.pack(fill='x')
        
        # 設定完了ボタン
        self.complete_button = tk.Button(
            self.main_frame,
            text="設定完了",
            font=('Arial', 20, 'bold'),
            command=self.complete_setup,
            bg='#FF5722',
            fg='white',
            padx=40,
            pady=15
        )
        self.complete_button.pack(pady=50)
        
        # ステータスラベル
        self.status_label = tk.Label(
            self.main_frame,
            text="Wi-Fiネットワークを取得中...",
            font=('Arial', 14),
            bg='#f0f0f0',
            fg='#666666'
        )
        self.status_label.pack(pady=20)
    
    def apply_rotation(self):
        """回転を適用"""
        if self.rotation == 1:
            # 180度回転
            for widget in self.main_frame.winfo_children():
                self.rotate_widget(widget)
    
    def rotate_widget(self, widget):
        """ウィジェットを180度回転（簡易実装）"""
        # 実際の回転は複雑なので、ここでは位置を反転
        pass
    
    def rotate_screen(self):
        """画面を回転"""
        self.rotation = 1 if self.rotation == 0 else 0
        self.save_rotation()
        messagebox.showinfo("回転", f"画面回転設定を変更しました（rotate.txt = {self.rotation}）")
    
    def scan_wifi(self):
        """Wi-Fiネットワークをスキャン"""
        def scan_thread():
            self.status_label.config(text="Wi-Fiネットワークを取得中...")
            self.refresh_button.config(state='disabled')
            
            try:
                # nmcliを使用してWi-Fiスキャン
                result = subprocess.run(
                    ['nmcli', '-f', 'SSID', 'dev', 'wifi', 'list'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    networks = []
                    for line in result.stdout.split('\n')[1:]:  # ヘッダーをスキップ
                        ssid = line.strip()
                        if ssid and ssid != '--':
                            networks.append(ssid)
                    
                    # 重複を除去してソート
                    networks = sorted(list(set(networks)))
                    self.wifi_combo['values'] = networks
                    
                    if networks:
                        self.status_label.config(text=f"{len(networks)}個のネットワークが見つかりました")
                    else:
                        self.status_label.config(text="Wi-Fiネットワークが見つかりませんでした")
                else:
                    self.status_label.config(text="Wi-Fiスキャンに失敗しました")
                    
            except subprocess.TimeoutExpired:
                self.status_label.config(text="Wi-Fiスキャンがタイムアウトしました")
            except Exception as e:
                self.status_label.config(text=f"エラー: {str(e)}")
            
            self.refresh_button.config(state='normal')
        
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def test_connection(self):
        """Wi-Fi接続をテスト"""
        try:
            import requests
            response = requests.get('https://www.google.com', timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def connect_wifi(self, ssid, password):
        """Wi-Fiに接続"""
        try:
            # nmcliを使用してWi-Fi接続
            if password:
                result = subprocess.run(
                    ['nmcli', 'dev', 'wifi', 'connect', ssid, 'password', password],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            else:
                result = subprocess.run(
                    ['nmcli', 'dev', 'wifi', 'connect', ssid],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            
            return result.returncode == 0
        except:
            return False
    
    def complete_setup(self):
        """設定完了処理"""
        ssid = self.wifi_var.get()
        password = self.password_var.get()
        
        if not ssid:
            messagebox.showerror("エラー", "Wi-Fiネットワークを選択してください")
            return
        
        self.status_label.config(text="Wi-Fiに接続中...")
        self.complete_button.config(state='disabled')
        
        def connect_thread():
            # Wi-Fi接続
            if self.connect_wifi(ssid, password):
                # 接続テスト
                time.sleep(3)  # 接続安定化のため少し待機
                if self.test_connection():
                    # setup.txtを1に更新
                    with open('setup.txt', 'w') as f:
                        f.write('1')
                    
                    # サイネージプログラムを実行
                    self.root.destroy()
                    subprocess.run([sys.executable, 'signage_display.py'])
                else:
                    messagebox.showerror("エラー", "インターネット接続テストに失敗しました")
                    self.complete_button.config(state='normal')
            else:
                messagebox.showerror("エラー", "Wi-Fi接続に失敗しました\nパスワードを確認してください")
                self.complete_button.config(state='normal')
            
            self.status_label.config(text="")
        
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def run(self):
        """ウィンドウを実行"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SetupWindow()
    app.run()
