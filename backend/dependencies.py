import os
import logging
from fastapi import Depends
from services.llm_service import LLMService
from services.feedback_service import FeedbackService
from services.prompt_builder import PromptBuilder
from services.prompt_template_engine import PromptTemplateEngine
from services.llm_clients.base import LLMClientInterface
from services.llm_clients.gemini_client import GeminiClient
from services.error_handler import ErrorHandler
from services.image_request_detector import ImageRequestDetector
from services.image_prompt_analyzer import ImagePromptAnalyzer
from services.image_generation_service import ImageGenerationService

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service Initialization
def get_error_handler():
    return ErrorHandler(logger=logger)

def get_prompt_template_engine():
    return PromptTemplateEngine()

def get_prompt_builder(template_engine: PromptTemplateEngine = Depends(get_prompt_template_engine)):
    return PromptBuilder(template_engine)

def get_llm_client() -> LLMClientInterface:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")
    return GeminiClient(api_key=api_key)

def get_image_request_detector():
    return ImageRequestDetector()

def get_image_prompt_analyzer(llm_client: LLMClientInterface = Depends(get_llm_client)):
    return ImagePromptAnalyzer(llm_client)

def get_image_generation_service():
    return ImageGenerationService()

def get_llm_service(
    prompt_builder: PromptBuilder = Depends(get_prompt_builder),
    llm_client: LLMClientInterface = Depends(get_llm_client),
    error_handler: ErrorHandler = Depends(get_error_handler),
    image_request_detector: ImageRequestDetector = Depends(get_image_request_detector),
    image_prompt_analyzer: ImagePromptAnalyzer = Depends(get_image_prompt_analyzer),
    image_generation_service: ImageGenerationService = Depends(get_image_generation_service)
):
    return LLMService(
        prompt_builder,
        llm_client,
        error_handler,
        image_request_detector,
        image_prompt_analyzer,
        image_generation_service
    )

def get_feedback_service(
    prompt_builder: PromptBuilder = Depends(get_prompt_builder),
    llm_client: LLMClientInterface = Depends(get_llm_client),
    error_handler: ErrorHandler = Depends(get_error_handler)
):
    return FeedbackService(prompt_builder, llm_client, error_handler)