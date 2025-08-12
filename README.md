# YouTube競合チャンネル分析システム

YouTubeショート動画の競合チャンネルを分析し、データをCSVファイルとして出力するバッチ処理システムです。

## 主な機能

- 複数のYouTubeチャンネルからショート動画データを自動収集
- チャンネルごと・日付ごとにCSVファイル出力
- ローカル環境とGoogle Cloud Run両対応
- 詳細なロギング機能

## 必要なもの

### ローカル実行の場合
- Python 3.10以上
- YouTube Data API v3のAPIキー

### Cloud Run実行の場合（追加で必要）
- Google Cloudプロジェクト
- Cloud Storage バケット
- Secret Manager（APIキー管理用）

## セットアップ

### 1. YouTube API キーの取得

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新規プロジェクトを作成または既存プロジェクトを選択
3. 「APIとサービス」→「ライブラリ」から「YouTube Data API v3」を有効化
4. 「APIとサービス」→「認証情報」からAPIキーを作成

### 2. ローカル環境のセットアップ

```bash
# リポジトリのクローン
git clone [repository-url]
cd youtube_rival_bunseki

# 依存関係のインストール（グローバル）
pip install -r requirements.txt

# または仮想環境を使用する場合
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt

# 環境変数の設定
copy .env.example .env
# .envファイルを編集してYOUTUBE_API_KEYを設定
```

### 3. 分析対象チャンネルの設定

`input/url_list.txt`に分析対象のYouTubeチャンネルURLを記載：

```
https://www.youtube.com/@channelname1
https://www.youtube.com/channel/UCxxxxxxxxxxxxxx
https://www.youtube.com/@channelname2
```

## 実行方法

### ローカル実行

```bash
# 直接実行
python main.py

# バッチファイルで実行（Windows）
run.bat
```

### テスト実行

```bash
pytest tests/
```

## 出力ファイル

CSVファイルは以下の場所に保存されます：

```
output/
└── YYYYMMDD/
    ├── チャンネル名1_YYYYMMDD.csv
    ├── チャンネル名2_YYYYMMDD.csv
    └── ...
```

### CSV項目

| 列 | 項目名 | 説明 |
|---|---|---|
| A | チャンネル名 | YouTubeチャンネル名 |
| B | チャンネル開始日 | チャンネル作成日 |
| C | チャンネル概要 | チャンネルの説明文 |
| D | 動画タイトル | ショート動画のタイトル |
| E | 動画URL | 動画の再生URL |
| F | アップロード日 | 動画の公開日 |
| G | 再生回数 | 動画の再生回数 |
| H | 高評価数 | いいねの数 |
| I | コメント数 | コメントの数 |
| J | 動画の長さ(秒) | 動画の再生時間 |
| K | サムネイル画像URL | サムネイル画像のURL |
| L | 動画タグ | 動画に設定されたタグ |

## Cloud Runへのデプロイ

### 1. Google Cloud設定

```bash
# プロジェクトの設定
gcloud config set project YOUR_PROJECT_ID

# 必要なAPIを有効化
gcloud services enable run.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Secret ManagerにAPIキーを登録
echo -n "YOUR_YOUTUBE_API_KEY" | gcloud secrets create youtube-api-key --data-file=-

# Cloud Storageバケットの作成
gsutil mb gs://YOUR_BUCKET_NAME
```

### 2. デプロイ

```bash
# コンテナイメージのビルドとデプロイ
gcloud run deploy youtube-analyzer \
  --source . \
  --region asia-northeast1 \
  --platform managed \
  --memory 1Gi \
  --timeout 3600 \
  --set-env-vars GCP_PROJECT_ID=YOUR_PROJECT_ID,GCS_BUCKET_NAME=YOUR_BUCKET_NAME \
  --service-account YOUR_SERVICE_ACCOUNT@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

### 3. Cloud Storageにurl_list.txtをアップロード

```bash
gsutil cp input/url_list.txt gs://YOUR_BUCKET_NAME/input/
```

### 4. 手動実行

```bash
gcloud run services describe youtube-analyzer --region asia-northeast1 --format 'value(status.url)'
# 表示されたURLにアクセスして実行
```

## トラブルシューティング

### APIクォータエラー
- 1日のクォータ制限（デフォルト10,000ユニット）を超えた場合は翌日まで待つ
- Google Cloud Consoleでクォータの増加をリクエスト可能

### チャンネルが見つからない
- URLが正しいか確認（@ハンドル名またはchannel/IDの形式）
- チャンネルが存在し、公開されているか確認

### CSVファイルの文字化け
- UTF-8 BOM付きで出力されるため、Excelでも正常に開けます
- 文字化けする場合は、テキストエディタで開いて文字コードを確認

## ライセンス

MIT License