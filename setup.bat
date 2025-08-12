@echo off
echo ====================================
echo セットアップスクリプト
echo ====================================
echo.

REM Python実行可能ファイルの確認
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo エラー: Pythonがインストールされていません
    echo Python 3.10以上をインストールしてください
    pause
    exit /b 1
)

echo 1. 依存パッケージをインストールしています...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo エラー: パッケージのインストールに失敗しました
    pause
    exit /b 1
)

echo.
echo 2. 設定ファイルを作成しています...
if not exist ".env" (
    copy .env.example .env
    echo .envファイルを作成しました
    echo ※ .envファイルを開いてYOUTUBE_API_KEYを設定してください
) else (
    echo .envファイルは既に存在します
)

echo.
echo 3. フォルダ構造を作成しています...
if not exist "input" mkdir input
if not exist "output" mkdir output
echo フォルダを作成しました

echo.
echo 4. サンプルファイルを確認しています...
if not exist "input\url_list.txt" (
    echo # YouTubeチャンネルURLを1行に1つずつ記載してください > input\url_list.txt
    echo # 例： >> input\url_list.txt
    echo # https://www.youtube.com/@channelname >> input\url_list.txt
    echo input\url_list.txtを作成しました
)

echo.
echo ====================================
echo セットアップが完了しました！
echo.
echo 次の手順：
echo 1. .envファイルを開いてYOUTUBE_API_KEYを設定
echo 2. input\url_list.txtに分析対象のチャンネルURLを記載
echo 3. run.batを実行して分析を開始
echo ====================================
echo.
pause