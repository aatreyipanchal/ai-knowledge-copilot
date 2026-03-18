import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from backend.database.database import SessionLocal, Conversation

class BaseAgent:
    def __init__(self, model_name: str = "llama-3.3-70b-versatile", temperature: float = 0.1):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables.")
        
        self.llm = ChatGroq(
            model=model_name,
            api_key=self.api_key,
            temperature=temperature,
        )

    def get_chat_history(self, session_id: str, limit: int = 10):
        db = SessionLocal()
        messages = db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).order_by(Conversation.timestamp.desc()).limit(limit).all()
        db.close()
        
        history = []
        for msg in reversed(messages):
            if msg.role == "user":
                history.append(HumanMessage(content=msg.content))
            else:
                history.append(AIMessage(content=msg.content))
        return history

    def save_message(self, session_id: str, role: str, content: str, metadata: dict = None):
        import json
        db = SessionLocal()
        meta_str = json.dumps(metadata) if metadata else None
        new_msg = Conversation(session_id=session_id, role=role, content=content, extra_info=meta_str)
        db.add(new_msg)
        db.commit()
        db.close()

    def run(self, prompt: str, session_id: str = "default_session", system_prompt: str = None, metadata: dict = None):
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        
        history = self.get_chat_history(session_id)
        messages.extend(history)
        
        messages.append(HumanMessage(content=prompt))
        
        # Save user message (no metadata usually)
        self.save_message(session_id, "user", prompt)
        
        response = self.llm.invoke(messages)
        return response.content
