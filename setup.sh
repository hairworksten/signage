#!/bin/bash

# Raspberry Pi用サイネージシステム修正版セットアップスクリプト

echo "サイネージシステムの依存関係を修正します..."

# 現在のディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "プロジェクトディレクトリ: $SCRIPT_DIR"

# システムパッケージを更新
echo "システムパッケージを更新中..."
sudo apt update

# 必要なシステムパッケージをインストール
echo "必要なシステムパッケージをインストール中..."
sudo apt install -y \
    python3-pip \
    python3-tk \
    python3-pil \
    python3-pil.imagetk \
    python3-requests \
    python3-venv \
    python3-full \
    network-manager \
    fonts-noto-cjk

# 仮想環境を作成
echo "Python仮想環境を作成中..."
python3 -m venv "$SCRIPT_DIR/venv"

# 仮想環境を有効化してパッケージをインストール
echo "仮想環境でPythonパッケージをインストール中..."
source "$SCRIPT_DIR/venv/bin/activate"
pip install --upgrade pip
pip install firebase-admin>=6.0.0 Pillow>=9.0.0 requests>=2.25.0

# 仮想環境用の起動スクリプトを作成
cat > "$SCRIPT_DIR/start_signage.sh" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/venv/bin/activate"
cd "$SCRIPT_DIR"
python main.py
EOF

chmod +x "$SCRIPT_DIR/start_signage.sh"

# 自動起動用のデスクトップファイルを更新
AUTOSTART_DIR="$HOME/.config/autostart"
mkdir -p "$AUTOSTART_DIR"

cat > "$AUTOSTART_DIR/signage-system.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Signage System
Comment=予約状況サイネージシステム
Exec=$SCRIPT_DIR/start_signage.sh
Icon=application-x-executable
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF

echo "自動起動ファイルを更新しました: $AUTOSTART_DIR/signage-system.desktop"

# 実行権限を付与
chmod +x "$SCRIPT_DIR/main.py"
chmod +x "$SCRIPT_DIR/setup_window.py"
chmod +x "$SCRIPT_DIR/signage_display.py"

# 必要なファイルを作成
echo "設定ファイルを初期化中..."
echo "0" > "$SCRIPT_DIR/setup.txt"
echo "0" > "$SCRIPT_DIR/rotate.txt"

echo ""
echo "修正版セットアップが完了しました！"
echo ""
echo "次の手順を実行してください："
echo "1. Firebase-key.jsonファイルをプロジェクトディレクトリに配置"
echo "2. 1.png～10.pngの背景画像ファイルを配置（1920x1080推奨）"
echo "3. システムを再起動して自動起動を確認"
echo ""
echo "手動でプログラムを実行する場合："
echo "$SCRIPT_DIR/start_signage.sh"
echo ""
echo "または："
echo "source $SCRIPT_DIR/venv/bin/activate && cd $SCRIPT_DIR && python3 main.py"
echo ""
