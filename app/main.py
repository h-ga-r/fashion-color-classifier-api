from fastapi import FastAPI, File, UploadFile  #FastAPI は、PythonでAPI（Webサービス）を構築するためのフレームワーク。UploadFile は、一時ファイルとしてメモリやディスクに保存しながら大きなファイルを効率的に扱うためのもの。
from fastapi.responses import HTMLResponse  #HTMLコンテンツを直接返すことができる。簡単なWebページを表示したり、フォームを作成したりする際に使用
import uvicorn   #uvicorn (ユービコーン) は、Pythonの非同期Webサーバー（ASGIサーバー）です。
import io  #Pythonで入出力（I/O）操作を行うためのツールを提供
import cv2  #OpenCVという非コンピュータビジョンライブラリのPythonバインディングです。
import numpy as np #Pythonで数値計算を効率的に行うためのライブラリです。
# ここで他のモジュールをインポートする予定
from .image_processing import identify_clothing_area, extract_dominant_colors #image_processing.pyからidentify_clothing_areaとextract_dominant_colorsを使えるように
from .color_classifier import classify_extracted_colors #分類された色情報をAPIに含める
from .color_combinations import suggest_color_combinations
# from .color_classifier import classify_color
# from .color_combinations import get_color_combinations

app = FastAPI() #今からwebアプリを作りますという合図

# ルートエンドポイント（HTMLページを表示）
@app.get("/", response_class=HTMLResponse) #fastapiでwebページを返す時に使う。@app.get("/"):WebサイトのルートURLにGETリクエストが来たときに、この下で定義されている関数を実行
async def read_root(): #非同期関数を定義　
    return """
    <html>
        <head>
            <title>服の色自動分類アプリ</title>  <!--タイトル表示-->
        </head>
        <body>
            <h1>服の画像をアップロードしてください</h1>  <!--<h1>一番大きい表示をさせる-->
            <form action="/uploadfile/" enctype="multipart/form-data" method="post">  <!--ファイルを選択アップロード-->
                <input name="file" type="file" accept="image/*">  
                <input type="submit" value="アップロード">   <!--ファイルを選択するためのボタン-->
            </form>  <!--ユーザーが情報を入力し、サーバーに送信するために使われます-->
            <hr>  <!--区切るための水平線-->
            <h2>APIドキュメント</h2>  <!--利用方法-->
            <p><a href="/docs">Swagger UI</a></p>  <!--<p> と </p>: 段落。APIドキュメントのリンクを表示-->
            <p><a href="/redoc">ReDoc</a></p>
        </body>
    </html>
    """

# 画像アップロードのエンドポイント
@app.post("/uploadfile/") #ここで定義
async def create_upload_file(file: UploadFile = File(...)):
    # アップロードされたファイルをメモリに読み込む
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    # OpenCVで画像としてデコード
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        return {"error": "画像の読み込みに失敗しました。有効な画像ファイルをアップロードしてください。"}

    # ここに画像処理と色分類のロジックを追加する予定
   
    clothing_area_img = identify_clothing_area(img) # 服の領域を識別

   
    # 少なめに設定
    dominant_colors_data = extract_dominant_colors(clothing_area_img, num_colors=3) # 識別された領域からメインの色を抽出
    classified_colors_data = classify_extracted_colors(dominant_colors_data) #抽出された色を色名に分類
    color_suggestions = suggest_color_combinations(classified_colors_data) #分類された色に合わせて提案
   

    #　抽出された色を辞書のリスト変換、APIレスポンスに含める
    # classified_colors_data は既に辞書のリストなので変換不要
    extracted_colors_for_response = [
        {"rgb": color.rgb, "percentage": color.percentage}
        for color in dominant_colors_data
    ]   

    # 例: 抽出された色 = process_image(img)
    # 例: 分類されたラベル = classify_color(抽出された色)
    # classified_colors_data は既に辞書のリストなので変換不要
    # 現時点では、画像のサイズとアップロードされたファイル名だけを返す
    height, width, _ = img.shape #画像の高さ、幅、そして（もしあれば）チャンネル数を取得
    return {
        "filename": file.filename, #Webアプリケーションでファイルをアップロードする
        "content_type": file.content_type, #ファイルのMIMEタイプ（Media Type / Content Type）を取得し、それを辞書（またはJSONオブジェクト）のキーと値のペアとして設定している
        "image_dimensions": {"width": width, "height": height}, #画像の高さと幅を辞書の形式で構造化
        "extracted_colors": extracted_colors_for_response, #画像から抽出されたメインの色をキーのもとに格納
        "classified_colors": classified_colors_data,  #分類された色の情報をclassified_colorsに格納
        "color_suggestions": color_suggestions,
        "message": "画像が正常にアップロードされ、主要な色が抽出・分類され、色の組み合わせが提案されました！"
    }