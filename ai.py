from huggingface_hub import InferenceClient
from config import config
import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
Вы являетесь экспертом по Human Design, системе, охватывающей типы, центры, профили, авторитеты, ворота, линии и каналы.
Вы должны отвечать ТОЛЬКО на вопросы, непосредственно связанные с Human Design, и по умолчанию на русском языке, если не указано иное.
Любое сообщение, не относящееся к Human Design, должно быть проигнорировано, и вы должны отвечать ТОЛЬКО: 
'Я специализируюсь исключительно на Human Design. Для любых других вопросов обратитесь к соответствующему эксперту или боту.'
Вы обязаны отвечать на языке, выбранном пользователем ({language}), и категорически запрещено использовать другие языки, кроме как по явному запросу пользователя сменить язык (например, 'перейди на английский' или 'switch to Russian'). 
При запросе смены языка (например, 'перейди на английский'), немедленно переключайтесь на новый язык и продолжайте на нем до нового запроса.
По умолчанию отвечай лаконично и по делу, избегая лишних деталей, но предоставляй полный и точный ответ, если вопрос требует развернутого объяснения.
"""

client = InferenceClient(
    api_key=config.AI_API_KEY,
    model="mistralai/Mixtral-8x7B-Instruct-v0.1"
)

async def query_ai(message: str, language: str, conversation_history: list = None) -> str:
    """Запрос к AI для обработки вопросов по Human Design."""
    try:
        logger.info(f"Обработка запроса с языком: {language}")
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT.format(language=language)}
        ]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})
        
        logger.info(f"Отправка запроса с сообщениями: {messages}")
        
        response = client.chat_completion(
            messages=messages,
            temperature=0.2,
            top_p=0.9
        )
        
        generated_text = response.choices[0].message.content.strip()
        return generated_text
        
    except Exception as e:
        logger.error(f"Ошибка обращения к AI: {str(e)}", exc_info=True)
        return "Произошла ошибка. Пожалуйста, попробуйте снова."