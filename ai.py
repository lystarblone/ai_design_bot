from huggingface_hub import InferenceClient
from config import config
import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are an expert in Human Design, a system that includes concepts like types, centers, profiles, authority, gates, lines, and channels. 
Answer questions only related to Human Design in a clear, professional, and friendly manner. 
If the question is about unrelated topics (e.g., astrology, tarot, psychology, or natal charts), respond with: 
"I specialize only in Human Design. For this question, I recommend consulting a relevant expert or bot."
Use the user's selected language (Russian or English) for all responses and maintain this language throughout the conversation.
All responses must be in {language}.
"""

client = InferenceClient(
    api_key=config.AI_API_KEY,
    model="mistralai/Mixtral-8x7B-Instruct-v0.1"
)

async def query_ai(message: str, language: str, conversation_history: list = None) -> str:
    """Запрос к AI для обработки вопросов по Human Design."""
    try:
        language = "Русский" if language.lower() == "ru" else "English"
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT.format(language=language)}
        ]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})
        
        logger.info(f"Отправка запроса с сообщениями: {messages}")
        
        response = client.chat_completion(
            messages=messages,
            max_tokens=500,
            temperature=0.2,
            top_p=0.9
        )
        
        generated_text = response.choices[0].message.content.strip()
        return generated_text
        
    except Exception as e:
        logger.error(f"Ошибка обращения к AI: {str(e)}")
        return "Произошла ошибка. Пожалуйста, попробуйте снова."