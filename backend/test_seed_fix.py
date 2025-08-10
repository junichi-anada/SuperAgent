import asyncio
import logging
from database import SessionLocal, get_db
from services.image_generation_service import ImageGenerationService
import crud

# ロガー設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AGENT_ID_TO_TEST = 15
# このユーザーIDは crud.get_agent を呼び出す際に必要ですが、
# 実際の画像生成ロジックでは使用されません。
# get_agent_without_user_check を使うので、任意のIDで問題ありません。
DUMMY_USER_ID = 1

async def main():
    """
    特定のagent_idに対して画像生成を強制的に実行し、
    シード値が保存されるかテストするスクリプト。
    """
    logger.info(f"--- Starting image regeneration test for agent_id: {AGENT_ID_TO_TEST} ---")
    
    db = SessionLocal()
    try:
        # 認証を回避してエージェントを取得
        agent = crud.get_agent_without_user_check(db, agent_id=AGENT_ID_TO_TEST)
        
        if not agent:
            logger.error(f"Agent with id {AGENT_ID_TO_TEST} not found.")
            return

        logger.info(f"Found agent: {agent.name} (Owner ID: {agent.owner_id})")
        logger.info(f"Current image_seed before generation: {agent.image_seed}")

        # 画像生成サービスを初期化
        image_service = ImageGenerationService()

        # 画像を強制的に再生成
        logger.info("Calling generate_and_save_image with force_regenerate=True...")
        await image_service.generate_and_save_image(
            agent_id=AGENT_ID_TO_TEST,
            user_id=agent.owner_id,  # エージェントの実際の所有者IDを使用
            force_regenerate=True
        )
        logger.info("Image generation task finished.")

        # データベースの変更を反映させるためにエージェントを再取得
        db.refresh(agent)
        
        logger.info(f"--- Test Verification ---")
        logger.info(f"New image_url: {agent.image_url}")
        logger.info(f"New image_seed: {agent.image_seed}")

        if agent.image_seed and agent.image_seed != -1:
            logger.info("✅ SUCCESS: A new valid seed value was saved to the database.")
        else:
            logger.error("❌ FAILURE: A valid seed value was NOT saved to the database.")

    finally:
        db.close()
        logger.info("--- Test script finished ---")

if __name__ == "__main__":
    asyncio.run(main())