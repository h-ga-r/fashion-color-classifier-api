# 服の色自動分類・組み合わせ提案API 

[![GitHub Actions Status](https://github.com/h-ga-r/fashion-color-classifier-api/workflows/CI/badge.svg)](https://github.com/h-ga-r/fashion-color-classifier-api/actions) 

## 概要

本プロジェクトは、ユーザーがアップロードした自分が服を着用している画像から、その主要な色を自動で抽出し、一般的な色名に分類するWeb APIです。さらに、ファッションにおける色彩理論に基づいた相性の良い色の組み合わせを提案することで、ユーザーが服を選ぶ際の色の悩みを解決し、より豊かなファッション体験を提供することを目指しています。（現時点ではUI/UXの部分であったり色分類調整のところが未完成であり取組中である。また提案する言葉についてもより詳細にしていきたいです。）

FastAPIをバックエンドとして利用し、画像処理にはOpenCVとscikit-learnを、デプロイにはDockerを活用しています。

## 機能 

**画像アップロード機能**: JPEG, PNGなどの画像ファイルをAPI経由でアップロードできます。
**服の主要色抽出**: アップロードされた画像から、K-meansクラスタリングを用いて支配的な色（RGB値と割合）を複数抽出します。
**色名分類**: 抽出されたRGB値を、HSV色空間における定義に基づき「赤」「青」「黒」などの一般的な色名に自動で分類します。
**色の組み合わせ提案**: 分類された色名に基づき、ファッションにおけるニュートラルカラー、類似色、補色などのルールを活用したおすすめの組み合わせを提案します。
**Dockerによるコンテナ化**: アプリケーション全体がDockerコンテナとして動作するため、環境依存性を低減し、どこでも容易にデプロイ可能です。

**前提条件** 
Docker Desktop がインストールされ、WSL2統合が有効になっていること。
WSL2 (Ubuntuなどのディストリビューション) がセットアップされていること。

### セットアップ 

1.  **リポジトリのクローン**:
    ```bash
    git clone [https://github.com/h-ga-r/fashion-color-classifier-api.git](https://github.com/h-ga-r/fashion-color-classifier-api.git)
    cd fashion-color-classifier-api
    ```

2.  **Dockerイメージのビルド**:
    プロジェクトのルートディレクトリ (`fashion-color-classifier-api` ) で以下のコマンドを実行します。
    （初回ビルド時や `Dockerfile`、`requirements.txt` を変更した場合は再ビルドが必要です。）
    ```bash
    docker build -t fashion-app .
    ```

3.  **Dockerコンテナの実行**:
    ```bash
    docker run -d -p 8000:8000 --name fashion_api fashion-app
    c64f08c90f9305d75ccc28957d88cceb149963e2159df9342e10524e97a6f012
    ```
    * `-d`: コンテナをバックグラウンドで実行します。
    * `-p 8000:8000`: ホストPCのポート8000をコンテナのポート8000にマッピングします。
    * `--name fashion_api`: コンテナに名前を付けます。

4.  **コンテナの動作確認**:
    コンテナが正常に起動しているか確認します。
    ```bash
    docker ps
    CONTAINER ID   IMAGE         COMMAND                  CREATED          STATUS          PORTS                                         NAMES
    c64f08c90f93  fashion-app  "uvicorn app.main:ap…"  16 minutes ago   Up 16 minutes   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp   fashion_api
    ```
    `fashion_api` コンテナが `Up` 状態であればOKです。

### アプリケーションへのアクセス 

* Webブラウザで以下のURLにアクセスしてください：
    ```
    [http://127.0.0.1:8000](http://127.0.0.1:8000)
    ```
* 表示されるHTMLフォームから服の画像をアップロードし、JSON形式の解析結果と提案を確認できます。

## デモ (Demo)

現在のバージョンでは、APIへのアクセスで以下のようなJSONレスポンスが返ってきます。

```json
{
  "filename": "uploaded_image.png",
  "content_type": "image/png",
  "image_dimensions": {
    "width": 500,
    "height": 375
  },
  "extracted_colors": [
    {"rgb": [44, 48, 50], "percentage": 43.79},
    {"rgb": [162, 127, 112], "percentage": 37.68},
    {"rgb": [155, 216, 222], "percentage": 18.53}
  ],
  "classified_colors": [
    {"rgb": [44, 48, 50], "name": "黒", "percentage": 43.79},
    {"rgb": [162, 127, 112], "name": "茶", "percentage": 37.68},
    {"rgb": [155, 216, 222], "name": "青", "percentage": 18.53}
  ],
  "color_suggestions": [
    "黒はどんな色とも合わせやすい万能カラーです。",
    "青には、青緑や紫などの類似色で統一感を出すと良いでしょう。",
    "茶色に青緑を差し色にしてコントラストを楽しむこともできます。",
    "黒と茶色の組み合わせは、モダンでバランスが良いでしょう。"
  ],
  "message": "画像が正常にアップロードされ、主要な色が抽出・分類され、色の組み合わせが提案されました！"
}
