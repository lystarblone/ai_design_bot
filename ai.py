import logging
from langchain_core.prompts import PromptTemplate
from langchain_mistralai.chat_models import ChatMistralAI
from langchain.chains import LLMChain
from config import config

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are an expert in Human Design, a system that includes concepts like types, centers, profiles, authority, gates, lines, and channels. 
Answer questions only related to Human Design in a clear, professional, and friendly manner. 
If the question is about unrelated topics (e.g., astrology, tarot, psychology, or natal charts), respond with: 
"I specialize only in Human Design. For this question, I recommend consulting a relevant expert or bot."
Use the user's selected language (Russian or English) for all responses and maintain this language throughout the conversation.
All responses must be in {language}.
"""

llm = ChatMistralAI(
    model_name="Mixtral-8x7B-Instruct-v0.1",
    api_key=config.AI_API_KEY,
    temperature=0.2
)

prompt_template = PromptTemplate(
    input_variables=["user_input", "language"],
    template=SYSTEM_PROMPT + "\nUser question: {user_input}"
)

human_design_chain = LLMChain(llm=llm, prompt=prompt_template)

async def query_ai(message: str, language: str, conversation_history: list = None) -> str:
    """Запрос к AI для обработки вопросов по Human Design."""
    try:
        context = ""
        if conversation_history:
            for entry in conversation_history:
                role = "User" if entry["role"] == "user" else "Assistant"
                context += f"{role}: {entry['content']}\n"
        
        context += f"User: {message}"
        
        response = human_design_chain.run(user_input=context, language=language)
        return response.strip()
    except Exception as e:
        logger.error(f"Ошибка обращения к AI: {str(e)}")
        raise