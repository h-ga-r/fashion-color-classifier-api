import cv2
import numpy as np

# ExtractedColor データクラスをインポート（image_processing.pyからコピーしても良いですが、
# 共通で使うなら共通ファイルにするか、ここでインポートします）
# 現状はimage_processing.pyから参照しているので、直接インポートしないでおきます。
# 必要に応じて後で変更。
# from .image_processing import ExtractedColor # <-- 将来的に必要になるかも

def rgb_to_hsv(rgb_tuple: tuple[int, int, int]) -> tuple[int, int, int]:
    """
    RGBタプルをHSVタプルに変換します。
    HSV値はOpenCVの範囲（H:0-179, S:0-255, V:0-255）に変換されます。
    """
    # NumPy配列に変換してOpenCVに渡す
    color_bgr = np.uint8([[list(rgb_tuple)[::-1]]]) # RGBをBGRに、タプルをリスト、さらに二次元配列に変換
    color_hsv = cv2.cvtColor(color_bgr, cv2.COLOR_BGR2HSV)[0][0] #与えられたBGRカラー値をHSV空間に変換（色相、彩度、明度）の配列を取り出し格納
    return tuple(color_hsv)

def classify_hsv_color(hsv_tuple: tuple[int, int, int]) -> str: #どの色のカテゴリに分類されるかを文字列で返す
    """
    HSV値に基づいて一般的な色名に分類します。

    Args:
        hsv_tuple (tuple): HSV値 (H:0-179, S:0-255, V:0-255)。

    Returns:
        str: 分類された色名。
    """
    h, s, v = hsv_tuple #h 色相　s 彩度　V　明度

    # 明度と彩度の閾値（これらの値は調整が必要かもしれません）
    # 明度が低い（暗い）場合は黒
    if v < 40: # 暗さの閾値。例: 0-255
        return "黒"
    # 明度が高い（明るい）場合は白
    if v > 200 and s < 50: # 明るさの閾値、彩度が低い
        return "白"
    # 彩度が低い場合はグレー
    if s < 30: # 彩度の閾値
        return "グレー"

    # ここから色相（Hue）に基づく分類 (H: 0-179)
    if (h >= 0 and h <= 10) or (h >= 160 and h <= 179):
        return "赤"
    elif h >= 11 and h <= 25:
        return "オレンジ"
    elif h >= 26 and h <= 35:
        return "茶" # オレンジと黄色の中間だが、ファッションでは茶色も重要
    elif h >= 36 and h <= 75:
        return "黄"
    elif h >= 76 and h <= 85:
        return "黄緑"
    elif h >= 86 and h <= 100:
        return "緑"
    elif h >= 101 and h <= 120:
        return "青緑"
    elif h >= 121 and h <= 140:
        return "青"
    elif h >= 141 and h <= 159:
        return "紫"
    else:
        return "その他" # 上記の範囲にない場合

def classify_extracted_colors(extracted_colors: list) -> list[dict]: # 抽出された色のリストを受け取り、それぞれを色名に分類辞書のリストで返す
    """
    抽出された色のリストを受け取り、それぞれを色名に分類します。

    Args:
        extracted_colors (list): image_processing.pyから返されたExtractedColorオブジェクトのリスト。

    Returns:
        list[dict]: 色名と割合を含む辞書のリスト。
    """
    classified_results = [] #からのリストを初期化
    for color_data in extracted_colors: #抽出されたメインの色に対して色名を分類、結果を返す
        rgb_tuple = color_data.rgb
        percentage = color_data.percentage

        hsv_tuple = rgb_to_hsv(rgb_tuple)
        color_name = classify_hsv_color(hsv_tuple)

        classified_results.append({
            "rgb": rgb_tuple,
            "name": color_name,
            "percentage": percentage
        })
    return classified_results

# (このモジュールは直接実行しないが、テスト用に残しておく)
if __name__ == "__main__":
    # テストデータ
    test_colors_data = [
        # RGBは適当な値。実際はimage_processingから来る
        # ExtractedColor(rgb=(200, 50, 50), percentage=75.23), # 赤っぽい
        # ExtractedColor(rgb=(240, 240, 240), percentage=15.10), # 白っぽい
        # ExtractedColor(rgb=(10, 10, 10), percentage=9.67), # 黒っぽい
        # ExtractedColor(rgb=(0, 0, 255), percentage=50.0), # 純粋な青
        # ExtractedColor(rgb=(128, 128, 128), percentage=50.0), # グレー
        # ExtractedColor(rgb=(255, 165, 0), percentage=50.0), # オレンジ
    ]

    # classify_extracted_colors(test_colors_data)
    pass