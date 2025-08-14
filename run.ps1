# YouTube競合チャンネル分析システム - PowerShell版
# 実行ポリシーエラーが出る場合: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

$Host.UI.RawUI.WindowTitle = "YouTube競合チャンネル分析システム"
Clear-Host

Write-Host ""
Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   YouTube競合チャンネル分析システム    ║" -ForegroundColor Cyan
Write-Host "║        Rival Channel Analyzer          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ステップ1: Python確認
Write-Host "[1/4] Python環境を確認中..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Python環境: OK ($pythonVersion)" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ エラー: Pythonがインストールされていません" -ForegroundColor Red
    Write-Host "Python 3.10以上を以下からインストールしてください:"
    Write-Host "https://www.python.org/downloads/" -ForegroundColor Cyan
    Read-Host "Enterキーを押して終了"
    exit 1
}

# ステップ2: 設定ファイル確認
Write-Host "[2/4] 設定ファイルを確認中..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "✗ エラー: .envファイルが見つかりません" -ForegroundColor Red
    $setup = Read-Host "初回セットアップを実行しますか？ (Y/N)"
    if ($setup -eq "Y") {
        if (Test-Path "setup.bat") {
            cmd /c setup.bat
        } else {
            Copy-Item ".env.example" ".env"
            Write-Host ".envファイルを作成しました" -ForegroundColor Yellow
            notepad .env
        }
    } else {
        Write-Host "セットアップをキャンセルしました"
        Read-Host "Enterキーを押して終了"
        exit 1
    }
}

# APIキーの確認
$envContent = Get-Content ".env"
if ($envContent -match "YOUR_API_KEY_HERE") {
    Write-Host "✗ エラー: APIキーが設定されていません" -ForegroundColor Red
    Write-Host ".envファイルを開いてYOUTUBE_API_KEYを設定してください"
    $openEnv = Read-Host ".envファイルを開きますか？ (Y/N)"
    if ($openEnv -eq "Y") {
        notepad .env
    }
    Read-Host "Enterキーを押して終了"
    exit 1
}
Write-Host "✓ 設定ファイル: OK" -ForegroundColor Green

# ステップ3: 入力ファイル確認
Write-Host "[3/4] 入力ファイルを確認中..." -ForegroundColor Yellow
if (-not (Test-Path "input\url_list.txt")) {
    Write-Host "⚠ url_list.txtが見つかりません" -ForegroundColor Yellow
    Write-Host "サンプルファイルから作成します..."
    if (Test-Path "input\url_list_sample.txt") {
        Copy-Item "input\url_list_sample.txt" "input\url_list.txt"
        Write-Host "✓ url_list.txtを作成しました" -ForegroundColor Green
        notepad "input\url_list.txt"
    } else {
        New-Item -ItemType Directory -Path "input" -Force | Out-Null
        @"
# YouTubeチャンネルURLを1行に1つずつ記載してください
# 例: https://www.youtube.com/@channelname
"@ | Out-File -FilePath "input\url_list.txt" -Encoding UTF8
        Write-Host "✓ url_list.txtを作成しました" -ForegroundColor Green
        notepad "input\url_list.txt"
    }
}

# URLが記載されているか確認
$urls = Get-Content "input\url_list.txt" | Where-Object { $_ -notmatch "^#" -and $_ -match "youtube\.com" }
if ($urls.Count -eq 0) {
    Write-Host "⚠ 警告: 有効なURLが見つかりません" -ForegroundColor Yellow
    Write-Host "input\url_list.txtにYouTubeチャンネルURLを追加してください"
    $openUrl = Read-Host "ファイルを開きますか？ (Y/N)"
    if ($openUrl -eq "Y") {
        notepad "input\url_list.txt"
    }
    Read-Host "Enterキーを押して終了"
    exit 1
}
Write-Host "✓ 入力ファイル: OK ($($urls.Count)件のURL)" -ForegroundColor Green

# ステップ4: 実行
Write-Host "[4/4] 分析を開始します..." -ForegroundColor Yellow
Write-Host "════════════════════════════════════════" -ForegroundColor Gray
Write-Host ""

# Pythonスクリプトの実行
$result = Start-Process python -ArgumentList "main.py" -NoNewWindow -Wait -PassThru

Write-Host ""
Write-Host "════════════════════════════════════════" -ForegroundColor Gray
Write-Host ""

if ($result.ExitCode -ne 0) {
    Write-Host "✗ エラーが発生しました" -ForegroundColor Red
    Write-Host "詳細はログファイル（youtube_analysis.log）を確認してください"
    $openLog = Read-Host "ログファイルを開きますか？ (Y/N)"
    if ($openLog -eq "Y" -and (Test-Path "youtube_analysis.log")) {
        notepad "youtube_analysis.log"
    }
} else {
    Write-Host "✓ 処理が正常に完了しました！" -ForegroundColor Green
    Write-Host ""
    
    # 最新の出力フォルダを取得
    $outputFolders = Get-ChildItem -Path "output" -Directory | Where-Object { $_.Name -match "^\d{8}$" } | Sort-Object -Descending
    if ($outputFolders.Count -gt 0) {
        $latestFolder = $outputFolders[0]
        Write-Host "📁 結果の保存先: output\$($latestFolder.Name)\" -ForegroundColor Cyan
        Write-Host ""
        $openFolder = Read-Host "フォルダを開きますか？ (Y/N)"
        if ($openFolder -eq "Y") {
            explorer "output\$($latestFolder.Name)\"
        }
    }
}

Write-Host ""
Read-Host "Enterキーを押して終了"