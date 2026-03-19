import os
import base64
from backend.agents.base_agent import BaseAgent
from langchain_core.messages import HumanMessage

class VisionAgent(BaseAgent):
    def __init__(self):
        # Using a vision-capable model
        super().__init__(model_name="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0.2)

    def describe_image(self, image_bytes: bytes, question: str = "What is in this image?", session_id: str = "default_session") -> dict:
        """
        Processes an image and answers a question about it.
        """
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        # Structure the message with image data
        # Note: LangChain's ChatGroq handles this format for vision models
        message = HumanMessage(
            content=[
                {"type": "text", "text": question},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ]
        )
        
        # For vision agent, we might want to bypass the standard BaseAgent.run 
        # because of the complex message structure, but we still want to save it.
        
        self.save_message(session_id, "user", f"[Visual Question] {question}")
        
        response = self.llm.invoke([message])
        
        return {"answer": response.content}

def run_vision_agent(image_bytes: bytes, question: str, session_id: str = "default_session") -> dict:
    agent = VisionAgent()
    return agent.describe_image(image_bytes, question, session_id)
