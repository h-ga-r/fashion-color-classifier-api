from fastapi import FastAPI, File, UploadFile  #FastAPI は、PythonでAPI（Webサービス）を構築するためのフレームワーク。UploadFile は、一時ファイルとしてメモリやディスクに保存しながら大きなファイルを効率的に扱うためのもの。
from fastapi.responses import HTMLResponse  #HTMLコンテンツを直接返すことができる。簡単なWebページを表示したり、フォームを作成したりする際に使用
import uvicorn   #uvicorn (ユービコーン) は、Pythonの非同期Webサーバー（ASGIサーバー）です。
import io  #Pythonで入出力（I/O）操作を行うためのツールを提供
import cv2  #OpenCVという非コンピュータビジョンライブラリのPythonバインディングです。
import numpy as np #Pythonで数値計算を効率的に行うためのライブラリです。
import base64 # 画像をBase64エンコードするために追加
from .image_processing import identify_clothing_area, extract_dominant_colors #image_processing.pyからidentify_clothing_areaとextract_dominant_colorsを使えるように
from .color_classifier import classify_extracted_colors #分類された色情報をAPIに含める
from .color_combinations import suggest_color_combinations


app = FastAPI() #今からwebアプリを作りますという合図

# ルートエンドポイント（HTMLページを表示）
@app.get("/", response_class=HTMLResponse) #fastapiでwebページを返す時に使う。@app.get("/"):WebサイトのルートURLにGETリクエストが来たときに、この下で定義されている関数を実行
async def read_root(): #非同期関数を定義　
    return """
    <!DOCTYPE html>  <!--文書型宣言-->
    <html lang="ja"> <!--主要言語が日本語-->
    <head>
        <meta charset="UTF-8"> <!--文字エンコーディング（cpがどのように数字のコードに変換し保存、表示）utf-8は最も広く使われている-->
        <meta name="viewport" content="width=device-width, initial-scale=1.0"> <!--レスポンシブデザインを実現-->
        <title>服の色自動分類アプリ</title> <!--タイトル表示-->
        <style>
            body { 
                font-family: Arial, sans-serif; /* テキストのフォント */
                margin: 20px; /* ページの外側の余白を設定 */
                background-color: #f4f4f4; /* ページの背景色 */
                color: #333; /* テキストの色 */
            }
            .container { /* cssのクラスセレクタ */ 
                max-width: 800px; /* 最大の幅が800px */
                margin: 0 auto; /* 要素を水平方向の中央に配置 */
                background-color: #fff; /* 背景色を白、薄いグレーの上に浮かび上がる感じ */
                padding: 30px; /* 内側に余白 */
                border-radius: 8px; /* 要素の角を丸める */
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); /* 影を付ける */
            }
            h1, h2 {  /* 見出しのスタイル設定 */
                color: #0056b3; /* 文字の色 */
                border-bottom: 2px solid #eee; /* 下線を付ける */
                padding-bottom: 10px; /* 下側の内側に余白 */
                margin-top: 20px; /* 上側の外側に余白 */
            }
            .form-section { /* セクション間の余白 */
                margin-bottom: 30px;
            }
            input[type="file"] { /* 見た目を整える（ファイルであるinput要素、uppボタンにのみ適用）*/
                padding: 10px; /* ボタン内側の余白 */
                border: 1px solid #ccc; /* ボタンの境界線を設定、1pxは線の太さ */
                border-radius: 4px; /* ボタンの角を丸くする */
                background-color: #f9f9f9; /* ボタンの背景色 */
            }
            input[type="submit"] { /* 送信ボタンの見た目 */
                background-color: #007bff; /* ボタンの背景色 */
                color: white; /* ボタンの文字色 */
                padding: 10px 20px; /* ボタンの内側の余白 */
                border: none; /* ボタンの境界線をなくす */
                border-radius: 4px; /* 角を丸くする */
                cursor: pointer; /* ボタンにカーソルを合したときに指の形に */
                font-size: 16px; /* ボタンの文字サイズ */
                transition: background-color 0.3s ease; /* ボタンの背景色の変化にアニメーション */
            } 
            input[type="submit"]:hover { /* マウスを合わせたときの見た目（ホバー効果）*/
                background-color: #0056b3; /* ホバーした時の背景色 */
            }
            .results-section { /* 結果表示セクションのスタイル */
                border-top: 1px solid #eee; /* 上部に境界線を追加,1pxは線の太さ */
                padding-top: 20px; /* 要素の上側の内側余白 */
                margin-top: 20px; /* 要素の上側の外側余白 */
            }
            .color-palette { /*カラーパレットを表示するスタイル */
                display: flex; /* フレックスコンテナとして設定。要素の直接の子要素が横並びに配置されようになる */
                margin-top: 10px; /* 要素の上の外側余白 */
                margin-bottom: 20px; /* 下部の外側余白 */
                border-radius: 4px; /* 要素の角を丸める */
                overflow: hidden; /* 角丸を適用するため */
            }
            .color-block { /* 指定された要素にスタイルを設定
                height: 50px; /* カラーブロックの高さ */
                display: flex; /* フレックスコンテナとして設定。要素の直接の子要素が横並びに配置されようになる */ 
                align-items: center; /* 垂直方向の中央に配置 */
                justify-content: center; /* 水平方向の中央に配置 */
                color: white; /* カラーブロック内の文字色 */
                font-weight: bold; /* カラーブロック内の文字を太字 */
                text-shadow: 1px 1px 2px rgba(0,0,0,0.7); /* テキストシャドウ */
                flex-grow: 1; /* 各ブロックが均等に幅を占めるように */
                flex-basis: 0; /* flex-growと合わせて均等に */
            }
            .color-block span { /* カラーパレット内の各色見本ブロックの文字サイズ */
                font-size: 14px;
            }
            .suggestions ul { /* 提案リストのスタイル設定 */
                list-style-type: disc; /*デフォルトの塗りつぶされた〇 */
                padding-left: 20px; /* 左の内側余白 */
            }
            .suggestions li { /* 提案リストの各項目のスタイル */
                margin-bottom: 8px; /* 下の外側余白 */
            }
            .error-message { /* エラーメッセージの表示スタイル */
                color: #dc3545; /* 文字色 */
                font-weight: bold; /* 文字を太字 */
                margin-top: 15px; /* 要素上部の外側余白 */
                border: 1px solid #dc3545; /* 要素に境界線 */
                padding: 10px; /* 要素の内側余白 */
                border-radius: 4px; /* 要素の角を丸くする */
                background-color: #f8d7da; /* 要素の背景色 */
            }
            .loading-message { /* 読み込み中のメッセージスタイル */
                margin-top: 15px; /* 要素の上部の外側余白を設定 */
                font-style: italic; /* フォントスタイルを設定 */
                color: #6c757d; /* 文字色 */
            }
            img {
                max-width: 70%; /* 画像サイズの調整 */
                height: auto; /* 画像の高さを調整 */
                display: block; /* 画像をブロックレベル要素 */
                margin-top: 20px; /* 画像上部の外側余白 */
                border: 1px solid #ddd; /* 画像に境界線 */
                border-radius: 4px; /* 角を丸く */
            }
            .api-docs a { /* APIドキュメント<a>のスタイル */
                color: #007bff; /* 文字色 */
                text-decoration: none; /* 下線を無くす */
                }
            .api-docs a:hover { /* APIドキュメントセクション内のマウスカーソルを合わせたときのスタイル */
                text-decoration: underline; /* ホバーしたときに再度下線 */
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>服の色自動分類アプリ</h1>  <!--<h1>一番大きい表示をさせる-->

            <div class="form-section"> <!--フォームの特定の部分をグループ化-->
                <p>服の画像をアップロードしてください。画像から主要な色を抽出、分類しファッションの色の組み合わせを提案します。</p>
                <input type="file" id="fileInput" accept="image/*"> <!--ファイルをコンピューターから選択するボタン-->
                <button id="uploadButton">アップロード</button> <!--サーバーにファイルを送信するボタン-->
            </div>

            <div class="loading-message" id="loadingMessage" style="display:none;"> <!--読み込み中のメッセージ表示-->
                画像を処理中...しばらくお待ちください。
            </div>
            <div class="error-message" id="errorMessage" style="display:none;"></div> <!--エラーが発生した際のメッセージ-->

            <div class="results-section" id="resultsSection" style="display:none;"> <!--処理を完了した後の結果-->
                <h2>分析結果</h2>
                <div id="imagePreviewContainer"> <!--UPした画像と関連するのをまとめて表示-->
                    <h3>アップロードされた画像</h3>
                    <img id="uploadedImage" src="#" alt="アップロードされた画像">
                </div>

                <div id="extractedColorsContainer"> <!--抽出した色の表示-->
                    <h3>抽出された色</h3>
                    <div class="color-palette" id="colorPalette"></div>
                </div>
                
                <div id="classifiedColorsContainer"> <!--分類された色の表示-->
                    <h3>分類された色</h3>
                    <ul id="classifiedColorsList"></ul>
                </div>

                <div id="suggestionsContainer"> <!--色の組み合わせ提案の表示-->
                    <h3>色の組み合わせ提案</h3>
                    <ul class="suggestions" id="suggestionsList"></ul>
                </div>
            </div>

            <hr>
            <div class="api-docs"> <!--APIドキュメントへのリンクを提供-->
                <h2>APIドキュメント</h2>
                <p><a href="/docs">Swagger UI</a></p>
                <p><a href="/redoc">ReDoc</a></p>
            </div>
        </div>

        <script> //webページに動的な機能を持たせる(以下の要素をHTMLから取得、変数に代入)
            const fileInput = document.getElementById('fileInput'); 
            const uploadButton = document.getElementById('uploadButton');
            const loadingMessage = document.getElementById('loadingMessage');
            const errorMessage = document.getElementById('errorMessage');
            const resultsSection = document.getElementById('resultsSection');
            const uploadedImage = document.getElementById('uploadedImage');
            const colorPalette = document.getElementById('colorPalette');
            const classifiedColorsList = document.getElementById('classifiedColorsList');
            const suggestionsList = document.getElementById('suggestionsList');

            uploadButton.addEventListener('click', async () => { //アップロードボタンがクリックされたときに実行されるもの
                const file = fileInput.files[0];
                if (!file) { //ファイルが選択されているかどうか
                    errorMessage.textContent = 'ファイルを１つ選択してください。';
                    errorMessage.style.display = 'block';
                    return;
                }

                // UIのリセット
                resultsSection.style.display = 'none';
                errorMessage.style.display = 'none';
                loadingMessage.style.display = 'block';
                colorPalette.innerHTML = '';
                classifiedColorsList.innerHTML = '';
                suggestionsList.innerHTML = '';

                const formData = new FormData(); //ウェブフォームのフィールドと値を表現するためのオブジェクト
                formData.append('file', file); //データ追加

                try { //エラーしてもアプリケーションがクラッシュするのを防ぐ
                    const response = await fetch('/uploadfile/', { //サーバーとでーたやり取り
                        method: 'POST', //HTTPのリクエストメソッド
                        body: formData, //画像ファイルがサーバーに送信
                    });

                    loadingMessage.style.display = 'none'; // ロードメッセージを非表示

                    if (!response.ok) { //サーバーからの応答がエラーの場合
                        const errorData = await response.json();
                        errorMessage.textContent = `エラーが発生しました: ${errorData.detail || errorData.error || response.statusText}`;
                        errorMessage.style.display = 'block';
                        return;
                    }

                    const data = await response.json(); //成功応答のデータを解析

                    // 画像プレビューの表示 (Base64エンコードされた画像を受け取る場合)
                    if (data.image_base64) {
                        uploadedImage.src = `data:${data.content_type};base64,${data.image_base64}`;
                        uploadedImage.style.display = 'block';
                    } else {
                        // もしBase64画像を受け取らない場合、ファイルリーダーでローカルプレビュー
                        const reader = new FileReader();
                        reader.onload = function(e) {
                            uploadedImage.src = e.target.result;
                            uploadedImage.style.display = 'block';
                        };
                        reader.readAsDataURL(file);
                    }


                    // 抽出された色の表示
                    if (data.extracted_colors && data.extracted_colors.length > 0) {
                        data.extracted_colors.forEach(color => {
                            const block = document.createElement('div');
                            block.className = 'color-block';
                            block.style.backgroundColor = `rgb(${color.rgb[0]}, ${color.rgb[1]}, ${color.rgb[2]})`;
                            block.innerHTML = `<span>${color.percentage}%</span>`;
                            // テキスト色を自動調整（簡易版：明度が低い場合白、高い場合黒）
                            const brightness = (color.rgb[0] * 299 + color.rgb[1] * 587 + color.rgb[2] * 114) / 1000;
                            if (brightness < 128) {
                                block.style.color = 'white';
                            } else {
                                block.style.color = 'black';
                            }
                            colorPalette.appendChild(block);
                        });
                    } else {
                        colorPalette.innerHTML = '<p>抽出された色はありませんでした。</p>';
                    }

                    // 分類された色の表示
                    if (data.classified_colors && data.classified_colors.length > 0) {
                        data.classified_colors.forEach(color => {
                            const li = document.createElement('li');
                            li.textContent = `${color.name} (RGB: ${color.rgb[0]},${color.rgb[1]},${color.rgb[2]}, ${color.percentage}%)`;
                            classifiedColorsList.appendChild(li);
                        });
                    } else {
                        classifiedColorsList.innerHTML = '<p>分類された色はありませんでした。</p>';
                    }

                    // 組み合わせ提案の表示
                    if (data.color_suggestions && data.color_suggestions.length > 0) {
                        data.color_suggestions.forEach(suggestion => {
                            const li = document.createElement('li');
                            li.textContent = suggestion;
                            suggestionsList.appendChild(li);
                        });
                    } else {
                        suggestionsList.innerHTML = '<p>色の組み合わせ提案はありませんでした。</p>';
                    }

                    resultsSection.style.display = 'block'; // 結果セクションを表示
                } catch (error) {
                    console.error('Fetch error:', error);
                    loadingMessage.style.display = 'none';
                    errorMessage.textContent = `ネットワークエラーが発生しました: ${error.message}`;
                    errorMessage.style.display = 'block';
                }
            });
        </script>
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

   
    clothing_area_img = identify_clothing_area(img) # 服の領域を識別

   
    # 少なめに設定(改良予定)
    dominant_colors_data = extract_dominant_colors(clothing_area_img, num_colors=3) # 識別された領域からメインの色を抽出
    classified_colors_data = classify_extracted_colors(dominant_colors_data) #抽出された色を色名に分類
    color_suggestions = suggest_color_combinations(classified_colors_data) #分類された色に合わせて提案
   

    #　抽出された色を辞書のリスト変換、APIレスポンスに含める
    # classified_colors_data は既に辞書のリストなので変換不要
    extracted_colors_for_response = [
        {"rgb": color.rgb, "percentage": color.percentage}
        for color in dominant_colors_data
    ]   

    # --- アップロード画像をBase64エンコードして返す (UI側でプレビューするため) ---
    # 画像をPNG形式でエンコード
    is_success, buffer = cv2.imencode(".png", img)
    if not is_success:
        return {"error": "画像のエンコードに失敗しました。"}
    # Base64文字列に変換
    img_base64 = base64.b64encode(buffer).decode('utf-8')

    height, width, _ = img.shape #画像の高さ、幅、そして（もしあれば）チャンネル数を取得
    return {
        "filename": file.filename, #Webアプリケーションでファイルをアップロードする
        "content_type": file.content_type, #ファイルのMIMEタイプ（Media Type / Content Type）を取得し、それを辞書（またはJSONオブジェクト）のキーと値のペアとして設定している
        "image_dimensions": {"width": width, "height": height}, #画像の高さと幅を辞書の形式で構造化
        "extracted_colors": extracted_colors_for_response, #画像から抽出されたメインの色をキーのもとに格納
        "classified_colors": classified_colors_data,  #分類された色の情報をclassified_colorsに格納
        "color_suggestions": color_suggestions,
        "image_base64": img_base64, # Base64エンコードされた画像データを追加
        "message": "画像が正常にアップロードされ、主要な色が抽出・分類され、色の組み合わせが提案されました！"
    }