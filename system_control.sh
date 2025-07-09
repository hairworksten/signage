#!/bin/bash

# サイネージシステム制御スクリプト

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROCESS_NAME="main.py"

show_usage() {
    echo "使用方法: $0 [start|stop|restart|status|reset|logs]"
    echo ""
    echo "  start   - サイネージシステムを開始"
    echo "  stop    - サイネージシステムを停止"
    echo "  restart - サイネージシステムを再起動"
    echo "  status  - 現在の状態を確認"
    echo "  reset   - 設定をリセット（初期設定から開始）"
    echo "  logs    - ログを表示"
}

start_system() {
    echo "サイネージシステムを開始しています..."
    cd "$SCRIPT_DIR"
    
    # 仮想環境が存在する場合は使用
    if [ -d "$SCRIPT_DIR/venv" ]; then
        nohup "$SCRIPT_DIR/start_signage.sh" > signage.log 2>&1 &
    else
        nohup python3 main.py > signage.log 2>&1 &
    fi
    echo "システムが開始されました。"
}

stop_system() {
    echo "サイネージシステムを停止しています..."
    pkill -f "$PROCESS_NAME"
    pkill -f "setup_window.py"
    pkill -f "signage_display.py"
    echo "システムが停止されました。"
}

restart_system() {
    stop_system
    sleep 3
    start_system
}

check_status() {
    if pgrep -f "$PROCESS_NAME" > /dev/null; then
        echo "✓ サイネージシステムは動作中です"
        echo "プロセスID: $(pgrep -f "$PROCESS_NAME")"
    else
        echo "✗ サイネージシステムは停止中です"
    fi
    
    echo ""
    echo "設定状況:"
    if [ -f "$SCRIPT_DIR/setup.txt" ]; then
        setup_status=$(cat "$SCRIPT_DIR/setup.txt")
        echo "  初期設定: $setup_status (0=未設定, 1以上=設定済み)"
    else
        echo "  初期設定: 設定ファイルが見つかりません"
    fi
    
    if [ -f "$SCRIPT_DIR/rotate.txt" ]; then
        rotate_status=$(cat "$SCRIPT_DIR/rotate.txt")
        echo "  画面回転: $rotate_status (0=通常, 1=180度回転)"
    else
        echo "  画面回転: 設定ファイルが見つかりません"
    fi
    
    echo ""
    echo "ネットワーク状況:"
    if ping -c 1 google.com > /dev/null 2>&1; then
        echo "  ✓ インターネット接続: 正常"
    else
        echo "  ✗ インターネット接続: 異常"
    fi
}

reset_settings() {
    echo "設定をリセットしています..."
    stop_system
    
    # 設定ファイルをリセット
    echo "0" > "$SCRIPT_DIR/setup.txt"
    echo "0" > "$SCRIPT_DIR/rotate.txt"
    
    # ログファイルをクリア
    : > "$SCRIPT_DIR/signage.log"
    
    echo "設定がリセットされました。次回起動時に初期設定が表示されます。"
}

show_logs() {
    if [ -f "$SCRIPT_DIR/signage.log" ]; then
        echo "=== サイネージシステムログ ==="
        tail -50 "$SCRIPT_DIR/signage.log"
    else
        echo "ログファイルが見つかりません。"
    fi
}

# メイン処理
case "$1" in
    start)
        start_system
        ;;
    stop)
        stop_system
        ;;
    restart)
        restart_system
        ;;
    status)
        check_status
        ;;
    reset)
        read -p "設定をリセットしてもよろしいですか？ (y/N): " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            reset_settings
        else
            echo "キャンセルされました。"
        fi
        ;;
    logs)
        show_logs
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
