import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# R18関連のキーワードとスコアのマッピング
# スコアは、単語の直接性や重要度に応じて設定
R18_KEYWORDS: Dict[str, int] = {
    # 軽度な表現 (スコア: 10-30)
    "キス": 10, "kiss": 10,
    "抱きしめる": 10, "hug": 10,
    "肌": 15, "skin": 15,
    "下着": 20, "underwear": 20, "lingerie": 25,
    "ビキニ": 20, "bikini": 20,
    "水着": 20, "swimsuit": 20,
    "胸": 25, "breast": 25, "boobs": 30,
    "お尻": 25, "ass": 25, "butt": 25,
    "太もも": 20, "thigh": 20,
    "裸": 30, "nude": 30, "naked": 30,

    # 中度な表現 (スコア: 40-60)
    "エッチ": 40, "ecchi": 40,
    "セクシー": 40, "sexy": 40,
    "誘惑": 50, "seduce": 50,
    "オーガズム": 60, "orgasm": 60,
    "マスターベーション": 60, "masturbation": 60,

    # 重度な表現 (スコア: 70-100)
    "セックス": 80, "sex": 80,
    "fuck": 80,
    "ペニス": 80, "penis": 80,
    "ヴァギナ": 80, "vagina": 80,
    "射精": 90, "cum": 90, "ejaculation": 90,
    "レイプ": 100, "rape": 100,
    "輪姦": 100, "gangbang": 100,
    "獣姦": 100, "bestiality": 100,
}

class R18ContentAnalyzer:
    def analyze(self, text: str) -> int:
        """
        テキストを分析してR18スコアを計算します。
        このメソッドは、既存の `analyze_r18_score` 関数をラップします。
        """
        return analyze_r18_score(text)

def analyze_r18_score(text: str) -> int:
    """
    入力されたテキストを分析し、R18コンテンツのスコアを計算します。
    スコアは0から100の範囲で、60以上がR18コンテンツと見なされます。

    Args:
        text: 分析対象のテキスト。

    Returns:
        計算されたR18スコア。
    """
    if not text:
        return 0

    total_score = 0
    lower_text = text.lower()
    found_keywords = []

    # テキストに含まれるキーワードをチェックし、スコアを加算
    for keyword, score in R18_KEYWORDS.items():
        if keyword in lower_text:
            total_score += score
            found_keywords.append(keyword)

    # スコアが100を超えないように調整
    final_score = min(total_score, 100)

    if final_score > 0:
        logger.info(f"R18 score analyzed. Score: {final_score}, Found keywords: {found_keywords}")
    
    return final_score
