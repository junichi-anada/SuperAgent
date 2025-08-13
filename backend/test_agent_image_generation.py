#!/usr/bin/env python3
"""
エージェントの外見情報から自動画像生成をテストするスクリプト
"""
import os
import sys
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# プロジェクトのルートディレクトリをパスに追加
sys.path.append('/app')

# モジュールのインポート
import models
from database import Base
from services.image_generation_service import ImageGenerationService

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_agent(db_session):
    """テスト用のエージェントを作成"""
    test_agent = models.Agent(
        name="テストエージェント",
        description="画像生成テスト用のエージェント",
        owner_id=1,  # テスト用のユーザーID
        gender="女性",
        background="オフィス",
        hair_style="long",
        eye_color="brown",
        ethnicity="asian",
        age=25,
        body_type="slim",
        clothing="business"
    )
    
    db_session.add(test_agent)
    db_session.commit()
    db_session.refresh(test_agent)
    
    logger.info(f"テストエージェントを作成しました: ID={test_agent.id}, 名前={test_agent.name}")
    return test_agent

def test_prompt_generation(db_session, agent):
    """プロンプト生成のテスト"""
    service = ImageGenerationService()
    prompt = service._generate_prompt(agent)
    
    logger.info(f"生成されたプロンプト: {prompt}")
    
    # プロンプトに各属性が含まれているかチェック
    expected_elements = [agent.gender, agent.ethnicity, agent.hair_style, agent.eye_color, agent.body_type, agent.clothing]
    for element in expected_elements:
        if element and element not in prompt:
            logger.error(f"プロンプトに '{element}' が含まれていません")
            return False
    
    logger.info("✅ プロンプト生成テスト成功")
    return True

async def test_image_generation_without_actual_api(db_session, agent):
    """実際のAPI呼び出しなしで画像生成処理をテスト"""
    service = ImageGenerationService()
    
    # クライアントをNoneに設定して実際のAPI呼び出しを回避
    service.client = None
    
    # 画像生成を試行（APIエラーで失敗するはず）
    await service.generate_and_save_image(agent_id=agent.id, user_id=agent.owner_id)
    log = service.get_generation_log(agent.id)
    
    if log and log.get("status") == "failed" and "Image generation client is not available." in log.get("error", ""):
        logger.info("✅ 期待通りのエラーが発生しました（API未利用設定）")
        return True
    else:
        logger.error(f"予期しない結果となりました。ログ: {log}")
        return False

import asyncio

async def test_image_generation_with_api(db_session, agent):
    """実際のAPI呼び出しありで画像生成処理をテスト"""
    if os.getenv("IMAGE_GENERATION_PROVIDER") != "webui":
        logger.info("WebUIプロバイダーが設定されていないため、API呼び出しテストをスキップします。")
        return True

    service = ImageGenerationService()
    
    logger.info("--- 1回目の画像生成（IP-Adapterなし）を開始 ---")
    await service.generate_and_save_image(agent_id=agent.id, user_id=agent.owner_id)
    
    log = service.get_generation_log(agent.id)
    if not log or log.get("status") != "completed":
        logger.error(f"1回目の画像生成に失敗しました。ログ: {log}")
        return False
    
    first_image_url = log.get("image_url")
    logger.info(f"✅ 1回目の画像生成成功: {first_image_url}")

    # エージェントに画像URLを反映
    agent.image_url = first_image_url
    db_session.add(agent)
    db_session.commit()
    db_session.refresh(agent)

    logger.info("--- 2回目の画像生成（IP-Adapterあり）を開始 ---")
    await service.generate_and_save_image(agent_id=agent.id, user_id=agent.owner_id, force_regenerate=True)

    log = service.get_generation_log(agent.id)
    if not log or log.get("status") != "completed":
        logger.error(f"2回目の画像生成に失敗しました。ログ: {log}")
        return False

    second_image_url = log.get("image_url")
    logger.info(f"✅ 2回目の画像生成成功: {second_image_url}")
    
    if first_image_url == second_image_url:
        logger.error("画像が再生成されていません。URLが同じです。")
        return False

    logger.info("✅ IP-Adapterを利用した画像生成テスト成功")
    return True


def main():
    """メイン関数"""
    print("エージェント画像生成テストを開始します...")
    
    # 環境変数をロード
    load_dotenv()
    
    # データベース接続
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        logger.error("DATABASE_URLが設定されていません")
        return False
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # テストセッション開始
    db_session = SessionLocal()
    
    try:
        # テストエージェントを作成
        test_agent = create_test_agent(db_session)
        
        # プロンプト生成テスト
        if not test_prompt_generation(db_session, test_agent):
            return False
        
        # 画像生成処理テスト（API呼び出しなし）
        if not asyncio.run(test_image_generation_without_actual_api(db_session, test_agent)):
            return False

        # 画像生成処理テスト（API呼び出しあり）
        if not asyncio.run(test_image_generation_with_api(db_session, test_agent)):
            return False
        
        logger.info("🎉 全てのテストが成功しました！")
        return True
        
    except Exception as e:
        logger.error(f"テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # テストデータをクリーンアップ
        try:
            db_session.query(models.Agent).filter(models.Agent.name == "テストエージェント").delete()
            db_session.commit()
            logger.info("テストデータをクリーンアップしました")
        except Exception as e:
            logger.warning(f"クリーンアップ中にエラー: {e}")
        
        db_session.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)