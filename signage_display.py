#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from PIL import Image, ImageTk
import firebase_admin
from firebase_admin import credentials, firestore
import threading
import time
from datetime import datetime, timedelta
import os
import math

class SignageDisplay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("予約状況サイネージ")
        self.root.geometry("1080x1920")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        
        # スリープ無効化（エラーを無視）
        try:
            os.system('xset s off 2>/dev/null')
            os.system('xset -dpms 2>/dev/null')
            os.system('xset s noblank 2>/dev/null')
        except:
            pass
        
        # Firebase初期化
        self.init_firebase()
        
        # 回転状態を読み込み
        self.rotation = self.read_rotation()
        
        # データ格納用
        self.now_population = 0
        self.reservations = []
        self.background_image = None
        self.background_photo = None
        
        # メインフレーム
        self.main_frame = tk.Frame(self.root, bg='black')
        self.main_frame.pack(fill='both', expand=True)
        
        self.create_widgets()
        self.apply_rotation()  # 回転設定を適用
        self.load_background()
        
        # 初期表示（テストデータ）
        self.now_population = 3
        self.reservations = [("09:00", 2), ("10:30", 1)]
        self.update_display()
        
        # ウィジェットを最前面に配置
        self.bring_widgets_to_front()
        
        self.start_data_monitoring()
        self.start_clock_update()
        self.start_background_rotation()
        
    def read_rotation(self):
        """rotate.txtから回転状態を読み込み"""
        try:
            with open('rotate.txt', 'r') as f:
                return int(f.read().strip())
        except:
            return 0
    
    def init_firebase(self):
        """Firebase初期化"""
        try:
            if not firebase_admin._apps:
                if os.path.exists('Firebase-key.json'):
                    cred = credentials.Certificate('Firebase-key.json')
                    firebase_admin.initialize_app(cred)
                    self.db = firestore.client()
                    print("Firebase接続成功")
                else:
                    print("警告: Firebase-key.jsonが見つかりません")
                    self.db = None
            else:
                self.db = firestore.client()
        except Exception as e:
            print(f"Firebase初期化エラー: {e}")
            self.db = None
    
    def create_widgets(self):
        """ウィジェットを作成"""
        # 利用可能な日本語フォントを確認して使用
        japanese_fonts = [
            'DejaVu Sans',
            'Liberation Sans', 
            'Noto Sans CJK JP',
            'Takao Gothic',
            'IPAexGothic',
            'Arial Unicode MS'
        ]
        
        main_font = 'Arial'  # デフォルト
        for font in japanese_fonts:
            try:
                # フォントのテスト
                test_label = tk.Label(self.main_frame, font=(font, 12))
                test_label.destroy()
                main_font = font
                print(f"使用するフォント: {font}")
                break
            except:
                continue
        
        # 日時表示（左上）
        self.datetime_label = tk.Label(
            self.main_frame,
            text="",
            font=(main_font, 40, 'bold'),
            fg='white',
            bg='black'
        )
        self.datetime_label.place(x=50, y=50)
        
        # 待ち人数表示（右上）
        self.wait_frame = tk.Frame(self.main_frame, bg='black')
        self.wait_frame.place(x=650, y=50)
        
        self.wait_title = tk.Label(
            self.wait_frame,
            text="現在の待ち人数",
            font=(main_font, 24, 'bold'),
            fg='white',
            bg='black'
        )
        self.wait_title.pack()
        
        self.wait_count = tk.Label(
            self.wait_frame,
            text="0人",
            font=(main_font, 64, 'bold'),
            fg='white',
            bg='black'
        )
        self.wait_count.pack()
        
        # 予約表示（中央）
        self.reservation_frame = tk.Frame(self.main_frame, bg='black')
        self.reservation_frame.place(x=200, y=600)
        
        self.reservation_title = tk.Label(
            self.reservation_frame,
            text="本日の予約状況",
            font=(main_font, 32, 'bold'),
            fg='white',
            bg='black'
        )
        self.reservation_title.pack(pady=(0, 30))
        
        # 予約リスト用のラベル（最大5件）
        self.reservation_labels = []
        for i in range(5):
            label = tk.Label(
                self.reservation_frame,
                text="",
                font=(main_font, 28, 'bold'),
                fg='white',
                bg='black'
            )
            label.pack(pady=8)
            self.reservation_labels.append(label)
    
    def apply_rotation(self):
        """画面回転を適用"""
        if self.rotation == 1:
            # 180度回転の場合、ウィジェットの位置も調整
            print("180度回転モード: ウィジェット位置を調整")
            
            # 日時表示を右下に移動
            self.datetime_label.place(x=1080-350, y=1920-150)
            
            # 待ち人数表示を左下に移動
            self.wait_frame.place(x=50, y=1920-250)
            
            # 予約表示を中央上部に移動
            self.reservation_frame.place(x=200, y=200)
        else:
            # 通常配置
            print("通常モード: 標準ウィジェット位置")
            self.datetime_label.place(x=50, y=50)
            self.wait_frame.place(x=650, y=50)
            self.reservation_frame.place(x=200, y=600)
    
    def load_background(self):
        """背景画像を読み込み"""
        current_hour = datetime.now().hour
        image_number = (current_hour % 10) + 1  # 1-10の画像をローテーション
        image_path = f"{image_number}.png"
        
        try:
            if os.path.exists(image_path):
                image = Image.open(image_path)
                print(f"背景画像を読み込み: {image_path} (回転設定: {self.rotation})")
                
                # 回転に応じて画像を回転
                if self.rotation == 1:
                    # rotate.txtが1の時のみ180度回転
                    image = image.rotate(180, expand=True)
                    print("背景画像を180度回転")
                else:
                    # 通常時: 回転なし（元画像が縦画面対応）
                    print("背景画像: 回転なし")
                
                # 画面サイズにリサイズ（1080x1920）
                image = image.resize((1080, 1920), Image.Resampling.LANCZOS)
                self.background_photo = ImageTk.PhotoImage(image)
                
                # 背景として設定
                self.bg_label = tk.Label(self.main_frame, image=self.background_photo)
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                self.bg_label.lower()  # 背景として最背面に配置
                
                print("背景画像の設定完了")
                
        except Exception as e:
            print(f"背景画像読み込みエラー: {e}")
            # エラー時はデフォルトの背景色
            self.main_frame.configure(bg='#1a1a2e')
            
    def bring_widgets_to_front(self):
        """テキストウィジェットを最前面に配置"""
        try:
            self.datetime_label.lift()
            self.wait_frame.lift()
            self.wait_title.lift()
            self.wait_count.lift()
            self.reservation_frame.lift()
            self.reservation_title.lift()
            for label in self.reservation_labels:
                label.lift()
            print("ウィジェットを最前面に配置しました")
        except Exception as e:
            print(f"ウィジェット配置エラー: {e}")
    
    def start_clock_update(self):
        """時計更新を開始"""
        def update_clock():
            while True:
                now = datetime.now()
                time_str = now.strftime("%m月%d日 %H:%M")
                self.datetime_label.config(text=time_str)
                time.sleep(1)
        
        threading.Thread(target=update_clock, daemon=True).start()
    
    def start_background_rotation(self):
        """背景画像のローテーションを開始"""
        def rotate_background():
            while True:
                time.sleep(3600)  # 1時間待機
                self.load_background()
        
        threading.Thread(target=rotate_background, daemon=True).start()
    
    def start_data_monitoring(self):
        """Firestoreデータ監視を開始"""
        def monitor_data():
            while True:
                try:
                    print("データを取得中...")
                    self.fetch_current_population()
                    self.fetch_reservations()
                    self.update_display()
                    print(f"現在の待ち人数: {self.now_population}")
                    print(f"予約件数: {len(self.reservations)}")
                    time.sleep(10)  # 10秒ごとに更新
                except Exception as e:
                    print(f"データ取得エラー: {e}")
                    time.sleep(30)  # エラー時は30秒待機
        
        threading.Thread(target=monitor_data, daemon=True).start()
    
    def fetch_current_population(self):
        """現在の待ち人数を取得"""
        if not self.db:
            print("Firebase未接続のため、テストデータを使用")
            self.now_population = 5  # テスト用データ
            return
        
        try:
            print("Firestoreから待ち人数を取得中...")
            doc_ref = self.db.collection('now_population').document('signage')
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                old_population = self.now_population
                self.now_population = data.get('now', 0)
                print(f"待ち人数を更新: {old_population} -> {self.now_population}")
                print(f"取得データ: {data}")
            else:
                print("signageドキュメントが存在しません")
                self.now_population = 0
        except Exception as e:
            print(f"待ち人数取得エラー: {e}")
            # エラー時は前回の値を維持
    
    def fetch_reservations(self):
        """予約情報を取得"""
        if not self.db:
            print("Firebase未接続のため、テストデータを使用")
            self.reservations = [("09:00", 2), ("10:30", 1), ("14:00", 3)]
            return
        
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            current_time = datetime.now().strftime("%H:%M")
            print(f"予約情報を取得中... 日付: {today}, 現在時刻: {current_time}")
            
            # 予約コレクションから本日分を取得
            reservations_ref = self.db.collection('reservations')
            docs = reservations_ref.where('date', '==', today).where('states', '==', 0).get()
            
            print(f"取得した予約数: {len(docs)}")
            
            # 時間別に集計
            time_counts = {}
            for doc in docs:
                data = doc.to_dict()
                time_slot = data.get('Time', '')
                print(f"予約データ: {data}")
                if time_slot >= current_time:  # 現在時刻以降のみ
                    if time_slot in time_counts:
                        time_counts[time_slot] += 1
                    else:
                        time_counts[time_slot] = 1
            
            # 時間順にソートして上位5件を取得
            sorted_times = sorted(time_counts.items())
            self.reservations = sorted_times[:5]
            print(f"処理後の予約情報: {self.reservations}")
            
        except Exception as e:
            print(f"予約情報取得エラー: {e}")
            self.reservations = []
    
    def update_display(self):
        """表示を更新"""
        try:
            # 待ち人数更新
            wait_text = f"{self.now_population}人"
            self.wait_count.config(text=wait_text)
            print(f"待ち人数表示を更新: {wait_text}")
            
            # 予約情報更新
            for i, label in enumerate(self.reservation_labels):
                if i < len(self.reservations):
                    time_slot, count = self.reservations[i]
                    reservation_text = f"{time_slot}  {count}人"
                    label.config(text=reservation_text)
                    print(f"予約{i+1}: {reservation_text}")
                else:
                    label.config(text="")
            
            # ウィジェットを最前面に持ってくる
            self.bring_widgets_to_front()
            
            # 強制的に画面を更新
            self.root.update_idletasks()
            
        except Exception as e:
            print(f"表示更新エラー: {e}")
    
    def run(self):
        """サイネージを実行"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SignageDisplay()
    app.run()
