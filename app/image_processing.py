import cv2 #画像認識などを使えるようにする
import numpy as np #numpyは数値計算を効率よく行う。as npでnumpyをnpとする
from sklearn.cluster import MiniBatchKMeans #KMeansよりも大規模データに効率的

# 色情報を保存するデータクラス
from dataclasses import dataclass

@dataclass
class ExtractedColor:
    rgb: tuple[int, int, int]  # RGB値 (0-255, 0-255, 0-255)
    percentage: float          # 全体に対する色の割合 (0-100%)

def extract_dominant_colors(image_np: np.ndarray, num_colors: int = 3) -> list[ExtractedColor]:
    """
    OpenCV画像（NumPy配列）からメインの色を抽出する。

    Args: #引数
        image_np (np.ndarray): OpenCV形式の画像（NumPy配列）。
        num_colors (int): 抽出する色の数。

    Returns: #返り値
        list[ExtractedColor]: 抽出された主要な色のリスト（RGB値と割合）。
    """

    # 画像のサイズを変更して処理を高速化（任意）
    # 500ピクセル幅にリサイズ
    h, w = image_np.shape[:2] #hには画像の高さ、wには画像の幅が代入される
    if w > 500:
         image_np = cv2.resize(image_np, (500, int(500 * h / w)), interpolation=cv2.INTER_AREA)

    # 画像をBGRからRGBに変換　理由OpenCVはBGR、K-meansはRGBを想定されているから
    image_rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)

    # ピクセルをリストに平坦化
    pixels = image_rgb.reshape(-1, 3) # (高さ*幅, 3) の配列に変換

    # K-meansクラスタリングで支配的な色を抽出
    # MiniBatchKMeans は大規模なデータセットに対してKMeansよりも高速
    kmeans = MiniBatchKMeans(n_clusters=num_colors, random_state=0, n_init='auto', verbose=0)
    kmeans.fit(pixels) #学習を実行

    # 各クラスター（色）のピクセル数をカウント
    # np.bincount は非負の整数配列の出現回数をカウント
    labels = kmeans.labels_
    counts = np.bincount(labels)

    # クラスターの中心（メインの色）とそれぞれの割合を取得
    dominant_colors = []
    for i, color_rgb in enumerate(kmeans.cluster_centers_):
        percentage = (counts[i] / len(pixels)) * 100
        dominant_colors.append(
            ExtractedColor(
                rgb=tuple(int(c) for c in color_rgb.astype(int)),
                percentage=round(percentage, 2)
            )
        )
    # 割合が高い順にソート
    dominant_colors.sort(key=lambda x: x.percentage, reverse=True)

    return dominant_colors

def identify_clothing_area(image_np: np.ndarray) -> np.ndarray:
    """
    画像から服の領域を識別する（簡易版）。
    この関数は非常に基本的なもので、背景と前景を単純に区別するのに役立ちます。
    より高度な服のセグメンテーションには、深層学習モデル（例: Mask R-CNN, U-Net）が必要です。

    Args:
        image_np (np.ndarray): OpenCV形式の画像（NumPy配列）。

    Returns:
        np.ndarray: 服の領域のみを含む画像（背景は黒または透明）。
    """
    # ここでは簡易的に、画像全体を服の領域と見なします。
    # 今後、モデルを使って人物や服のセグメンテーションを行う必要（例: 背景除去 (GrabCut, Deep Learning based Background Removal)）

    # 現状は、画像全体を返す。
    return image_np

