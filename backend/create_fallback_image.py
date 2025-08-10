#!/usr/bin/env python3
"""フォールバック画像を生成するスクリプト"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_fallback_image():
    """シンプルなフォールバック画像を生成します。"""
    # 画像サイズ
    width, height = 512, 512
    
    # 背景色（薄いグレー）
    background_color = (240, 240, 240)
    
    # 画像を作成
    image = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(image)
    
    # 円形のアバター領域を描画（濃いグレー）
    avatar_color = (180, 180, 180)
    center = (width // 2, height // 2)
    radius = 150
    draw.ellipse(
        [center[0] - radius, center[1] - radius,
         center[0] + radius, center[1] + radius],
        fill=avatar_color
    )
    
    # シンプルな人型シルエット
    silhouette_color = (140, 140, 140)
    # 頭
    head_radius = 50
    draw.ellipse(
        [center[0] - head_radius, center[1] - 80 - head_radius,
         center[0] + head_radius, center[1] - 80 + head_radius],
        fill=silhouette_color
    )
    # 体
    draw.ellipse(
        [center[0] - 80, center[1] - 30,
         center[0] + 80, center[1] + 100],
        fill=silhouette_color
    )
    
    # テキストを追加
    text = "No Image"
    # フォントサイズを調整（システムフォントを使用）
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # テキストのバウンディングボックスを取得
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # テキストを中央下部に配置
    text_position = ((width - text_width) // 2, height - 100)
    draw.text(text_position, text, fill=(100, 100, 100), font=font)
    
    # 画像を保存
    output_dir = "static"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "fallback_agent.png")
    image.save(output_path)
    print(f"Fallback image created: {output_path}")

if __name__ == "__main__":
    create_fallback_image()