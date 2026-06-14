import logging 
from openai import OpenAI
from sqlalchemy.orm import Session

from app.config import settings 
from app.prompts.therapist_prompt import THERAPIST_SYSTEM_PROMPT
from app.modules.memory_service import get_session_history, add_message

logger = logging.getLogger(__name__)

#Groq client
client = OpenAI(
            api_key=settings.groq_api_key,
            base_url=settings.groq_base_url
            )

    
def generate_response(session_id: str, user_message: str, db: Session = None) -> str:
    """
    Generate AI therapist response using Groq LLM

    Args:
        session_id: User ID for session tracking
        user_message: User input message 
        db: Database session for storing messages

    Returns:
        AI generated therapist response

    """

    try:

        history = get_session_history(session_id, db)

        messages = [
                {
                    "role": "system",
                    "content": THERAPIST_SYSTEM_PROMPT
                } 
            ]
        
        messages.extend(history)

        messages.append({
            "role": "user",
            "content": user_message
        })

        response = client.chat.completions.create(
            model = settings.model_name,
            messages = messages,
            temperature=0.75,
            max_tokens=300
        )

        ai_response = response.choices[0].message.content

        #store conversation
        add_message(session_id, "user", user_message, db)
        add_message(session_id, "assistant", ai_response, db)

        return ai_response
    
    except Exception as e:
        logger.error(f"Groq LLM Error: {str(e)}")
        return "I'm here to listen, but something went wrong. Please try again."
