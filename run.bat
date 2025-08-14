@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
title YouTube競合チャンネル分析システム

echo.
echo ╔════════════════════════════════════════╗
echo ║   YouTube競合チャンネル分析システム    ║
echo ║        Rival Channel Analyzer          ║
echo ╚════════════════════════════════════════╝
echo.

REM カラー表示の設定
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "RESET=[0m"

REM ステップ1: Python確認
echo %YELLOW%[1/4] Python環境を確認中...%RESET%
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%✗ エラー: Pythonがインストールされていません%RESET%
    echo.
    echo Python 3.10以上を以下からインストールしてください:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
python --version 2>&1 | findstr /R "3\.[1-9][0-9]" >nul
if %errorlevel% equ 0 (
    echo %GREEN%✓ Python環境: OK%RESET%
) else (
    echo %YELLOW%⚠ 警告: Python 3.10以上を推奨%RESET%
)

REM ステップ2: 設定ファイル確認
echo %YELLOW%[2/4] 設定ファイルを確認中...%RESET%
if not exist ".env" (
    echo %RED%✗ エラー: .envファイルが見つかりません%RESET%
    echo.
    echo 初回セットアップを実行しますか？ (Y/N)
    set /p setup=
    if /i "!setup!"=="Y" (
        if exist "setup.bat" (
            call setup.bat
        ) else (
            copy .env.example .env >nul 2>&1
            echo %YELLOW%.envファイルを作成しました%RESET%
            echo notepad.exeで.envファイルを開いてAPIキーを設定してください
            notepad .env
        )
    ) else (
        echo セットアップをキャンセルしました
        pause
        exit /b 1
    )
)

REM APIキーの確認
findstr "YOUR_API_KEY_HERE" .env >nul 2>&1
if %errorlevel% equ 0 (
    echo %RED%✗ エラー: APIキーが設定されていません%RESET%
    echo .envファイルを開いてYOUTUBE_API_KEYを設定してください
    echo.
    echo .envファイルを開きますか？ (Y/N)
    set /p openv=
    if /i "!openv!"=="Y" (
        notepad .env
    )
    pause
    exit /b 1
)
echo %GREEN%✓ 設定ファイル: OK%RESET%

REM ステップ3: 入力ファイル確認
echo %YELLOW%[3/4] 入力ファイルを確認中...%RESET%
if not exist "input\url_list.txt" (
    echo %YELLOW%⚠ url_list.txtが見つかりません%RESET%
    echo サンプルファイルから作成します...
    if exist "input\url_list_sample.txt" (
        copy "input\url_list_sample.txt" "input\url_list.txt" >nul
        echo %GREEN%✓ url_list.txtを作成しました%RESET%
        echo.
        echo url_list.txtを編集してチャンネルURLを追加してください
        notepad "input\url_list.txt"
    ) else (
        mkdir input >nul 2>&1
        echo # YouTubeチャンネルURLを1行に1つずつ記載してください > "input\url_list.txt"
        echo # 例: https://www.youtube.com/@channelname >> "input\url_list.txt"
        echo %GREEN%✓ url_list.txtを作成しました%RESET%
        notepad "input\url_list.txt"
    )
)

REM URLが記載されているか確認
findstr /v /c:"#" "input\url_list.txt" | findstr /r /c:"youtube\.com" >nul 2>&1
if %errorlevel% neq 0 (
    echo %YELLOW%⚠ 警告: 有効なURLが見つかりません%RESET%
    echo input\url_list.txtにYouTubeチャンネルURLを追加してください
    echo.
    echo ファイルを開きますか？ (Y/N)
    set /p openurl=
    if /i "!openurl!"=="Y" (
        notepad "input\url_list.txt"
    )
    pause
    exit /b 1
)
echo %GREEN%✓ 入力ファイル: OK%RESET%

REM ステップ4: 実行
echo %YELLOW%[4/4] 分析を開始します...%RESET%
echo ════════════════════════════════════════
echo.

REM Pythonスクリプトの実行
python main.py
set result=%errorlevel%

echo.
echo ════════════════════════════════════════
echo.

if %result% neq 0 (
    echo %RED%✗ エラーが発生しました%RESET%
    echo.
    echo 詳細はログファイル（youtube_analysis.log）を確認してください
    echo ログファイルを開きますか？ (Y/N)
    set /p openlog=
    if /i "!openlog!"=="Y" (
        if exist "youtube_analysis.log" (
            notepad "youtube_analysis.log"
        )
    )
) else (
    echo %GREEN%✓ 処理が正常に完了しました！%RESET%
    echo.
    
    REM 出力ファイルの確認
    for /f "tokens=*" %%a in ('dir /b /o-d "output\*" 2^>nul ^| findstr /r "^20[0-9][0-9]"') do (
        set latest=%%a
        goto :found
    )
    :found
    
    if defined latest (
        echo 📁 結果の保存先: output\!latest!\
        echo.
        echo フォルダを開きますか？ (Y/N)
        set /p openfolder=
        if /i "!openfolder!"=="Y" (
            explorer "output\!latest!\"
        )
    ) else (
        echo 結果はoutputフォルダに保存されています
    )
)

echo.
echo 終了するには何かキーを押してください...
pause >nul
endlocal