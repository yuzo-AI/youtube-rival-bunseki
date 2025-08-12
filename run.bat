@echo off
echo ====================================
echo YouTube競合チャンネル分析システム
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

REM .envファイルの確認
if not exist ".env" (
    echo エラー: .envファイルが見つかりません
    echo .env.exampleを.envにコピーして、APIキーを設定してください
    pause
    exit /b 1
)

REM input/url_list.txtの確認
if not exist "input\url_list.txt" (
    echo エラー: input\url_list.txtが見つかりません
    echo 分析対象のYouTubeチャンネルURLを記載してください
    pause
    exit /b 1
)

echo 処理を開始します...
echo.

REM メインスクリプトの実行
python main.py

if %errorlevel% neq 0 (
    echo.
    echo エラーが発生しました
    echo ログファイル（youtube_analysis.log）を確認してください
) else (
    echo.
    echo 処理が完了しました
    echo 結果はoutputフォルダに保存されています
)

echo.
pause