
def get_color_category(color_name: str) -> str: #->はこの型で返すという意味
    """
    色名をより広いカテゴリに分類します。
    色の組み合わせルールを作るために使用します。
    """
    neutral_colors = ["黒", "白", "グレー", "ベージュ", "茶"]
    warm_colors = ["赤", "オレンジ", "黄", "茶", "ピンク"] # ピンクは赤系として含める
    cool_colors = ["青", "緑", "紫", "青緑", "黄緑"] # 黄緑は寒色寄りとして

    if color_name in neutral_colors:
        return "ニュートラル"
    elif color_name in warm_colors:
        return "暖色"
    elif color_name in cool_colors:
        return "寒色"
    else:
        return "その他"
    
def suggest_color_combinations(classified_colors: list[dict]) -> list[str]:
    """
    分類された色名に基づいて、ファッションにおける色の組み合わせを提案します。

    Args:
        classified_colors (list[dict]): classify_extracted_colorsから返された色名と割合のリスト。
                                       例: [{"rgb": (R,G,B), "name": "赤", "percentage": 70.0}]

    Returns:
        list[str]: 提案される色の組み合わせのヒント。
    """
    if not classified_colors:
        return ["画像から色を検出できませんでした。"]

    # 主となる色（最も割合が高い色）を取得
    main_color_data = classified_colors[0] #分類された色のリストから一番メインの色を取り出し代入する
    main_color_name = main_color_data["name"] #色名だけ取り出して代入
    main_color_rgb = main_color_data["rgb"] # RGB値も参考にできる
    main_color_category = get_color_category(main_color_name) #メインの色名からさらに抽象度の高いカテゴリを取得代入

    suggestions = [] #提案用の空のリストを生成

    # 1. ニュートラルカラーとの組み合わせ
    if main_color_name not in ["黒", "白", "グレー"]:
        suggestions.append(f"{main_color_name}には、白、黒、グレーなどのニュートラルカラーがよく合います。")
    
    # 2. 類似色との組み合わせ (例: 青には青緑、緑には黄緑など)
    if main_color_name == "赤":
        suggestions.append("赤には、ピンクやオレンジなどの類似色でグラデーションを作るのもおすすめです。")
    elif main_color_name == "青":
        suggestions.append("青には、青緑や紫などの類似色で統一感を出すと良いでしょう。")
    elif main_color_name == "黄":
        suggestions.append("黄には、オレンジや黄緑などの類似色で明るい印象に。")
    elif main_color_name == "緑":
        suggestions.append("緑には、黄緑や青緑などの類似色で自然な印象に。")

    # 3. 補色（コントラスト）との組み合わせ
    # HSVの色相環で反対側に位置する色　特定の色をキーとして補色を結び付け
    complementary_colors = {
        "赤": "緑", "緑": "赤",
        "青": "オレンジ", "オレンジ": "青",
        "黄": "紫", "紫": "黄",
        "茶": "青緑", # ファッションにおける茶色の補色は青〜青緑系
        "ピンク": "緑" # ピンクの補色は緑系
    }
    if main_color_name in complementary_colors: #メインの色に対する補色が設定せれていれば
        comp_color = complementary_colors[main_color_name] #辞書から対応する色を取り出す
        suggestions.append(f"{main_color_name}には、{comp_color}を差し色にしてコントラストを楽しむこともできます。")# リストに追加

    # 4.メインの色のカテゴリに応じて提案
    if main_color_category == "暖色": 
        suggestions.append("暖色系の色は、暖かみがあり親しみやすい印象を与えます。")
    elif main_color_category == "寒色":
        suggestions.append("寒色系の色は、クールで落ち着いた印象を与えます。")

    # 5. 特定の色のヒント
    if main_color_name == "黒":
        suggestions.append("黒はどんな色とも合わせやすい万能カラーです。")
    elif main_color_name == "白":
        suggestions.append("白は清潔感があり、他の色を引き立てます。")
    elif main_color_name == "グレー":
        suggestions.append("グレーは上品で洗練された印象を与え、どんな色とも相性が良いです。")
    elif main_color_name == "ベージュ":
        suggestions.append("ベージュはナチュラルで優しい印象を与え、オフィススタイルにも最適です。")

    # 検出された複数の色を考慮した提案（簡易版　今後改良）
    if len(classified_colors) > 1:
        # 2番目に割合が高い色を取得
        secondary_color_data = classified_colors[1]
        secondary_color_name = secondary_color_data["name"]
        secondary_color_category = get_color_category(secondary_color_name) 
        # ニュートラル + 色物 の組み合わせ
        if main_color_category == "ニュートラル" and secondary_color_category != "ニュートラル":
             suggestions.append(f"{main_color_name}と{secondary_color_name}の組み合わせは、モダンでバランスが良いでしょう。")
        elif main_color_category != "ニュートラル" and secondary_color_category == "ニュートラル":
             suggestions.append(f"{main_color_name}に{secondary_color_name}を合わせると、メインの色が引き立ちます。")

    if not suggestions:
        suggestions.append("この色の組み合わせについては、特別な提案はありません。")

    # 重複する提案を排除し、ユニークなリストにする
    return list(set(suggestions))

# (テスト用)
if __name__ == "__main__":
    # テストデータ
    test_classified_colors = [
        {"rgb": (200, 50, 50), "name": "赤", "percentage": 75.23},
        {"rgb": (240, 240, 240), "name": "白", "percentage": 15.10},
        {"rgb": (100, 100, 100), "name": "グレー", "percentage": 9.67},
    ]
    # suggestions = suggest_color_combinations(test_classified_colors)
    # for s in suggestions:
    #     print(s)
    pass