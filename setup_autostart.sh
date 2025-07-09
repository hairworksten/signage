#!/bin/bash

# Raspberry Pi用サイネージシステム自動起動設定スクリプト

echo "サイネージシステムの自動起動を設定します..."

# 現在のディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "プロジェクトディレクトリ: $SCRIPT_DIR"

# 必要なパッケージをインストール
echo "必要なパッケージをインストール中..."
sudo apt update
sudo apt install -y python3-pip python3-tk python3-pil python3-pil.imagetk network-manager

# Pythonパッケージをインストール
echo "Pythonパッケージをインストール中..."
pip3 install -r "$SCRIPT_DIR/requirements.txt"

# 日本語フォントをインストール
echo "日本語フォントをインストール中..."
sudo apt install -y fonts-noto-cjk

# 自動起動用のデスクトップファイルを作成
AUTOSTART_DIR="$HOME/.config/autostart"
mkdir -p "$AUTOSTART_DIR"

cat > "$AUTOSTART_DIR/signage-system.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Signage System
Comment=予約状況サイネージシステム
Exec=python3 $SCRIPT_DIR/main.py
Icon=application-x-executable
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF

echo "自動起動ファイルを作成しました: $AUTOSTART_DIR/signage-system.desktop"

# 実行権限を付与
chmod +x "$SCRIPT_DIR/main.py"
chmod +x "$SCRIPT_DIR/setup_window.py"
chmod +x "$SCRIPT_DIR/signage_display.py"

# 必要なファイルを作成
echo "設定ファイルを初期化中..."
echo "0" > "$SCRIPT_DIR/setup.txt"
echo "0" > "$SCRIPT_DIR/rotate.txt"

# 背景画像用のサンプルファイルを作成（実際の画像は後で置き換える）
echo "サンプル背景画像ファイルを作成中..."
for i in {1..10}; do
    if [ ! -f "$SCRIPT_DIR/${i}.png" ]; then
        # 簡単な色付き画像を作成（実際の画像に置き換えてください）
        convert -size 1920x1080 xc:"#$(printf '%02x%02x%02x' $((i*25)) $((i*20)) $((i*15)))" "$SCRIPT_DIR/${i}.png" 2>/dev/null || true
    fi
done

echo ""
echo "セットアップが完了しました！"
echo ""
echo "次の手順を実行してください："
echo "1. Firebase-key.jsonファイルをプロジェクトディレクトリに配置"
echo "2. 1.png～10.pngの背景画像ファイルを配置（1920x1080推奨）"
echo "3. システムを再起動して自動起動を確認"
echo ""
echo "手動でプログラムを実行する場合："
echo "cd $SCRIPT_DIR && python3 main.py"
echo ""
