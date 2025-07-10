# Pythonの公式イメージをベースにする (軽量なslim-busterを使用)
FROM python:3.10-slim-buster

# 作業ディレクトリを設定
WORKDIR /app

#OpenCVが依存するグラフィックスライブらりをインストール
RUN apt update && apt install -y libgl1-mesa-glx libglib2.0-0

# 依存関係ファイルをコピーしてインストール (Dockerのキャッシュを有効に活用するため先に)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY app/ app/

# ポートを公開 (FastAPIがリッスンするポート)
EXPOSE 8000

# アプリケーションを起動するためのコマンド
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]