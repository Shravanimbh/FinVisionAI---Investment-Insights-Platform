from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import time
import re
import uuid
import logging
import markdown
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.memory import ConversationBufferMemory

# Load env variables
load_dotenv()

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('finvision_chatbot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("FinVisionChatbot")

# Configuration
class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME", "llama3-8b-8192")
    SESSION_TIMEOUT = 3600

if not Config.GROQ_API_KEY:
    logger.critical("Missing GROQ_API_KEY in environment.")
    raise EnvironmentError("Missing GROQ_API_KEY in .env")

# Flask app setup
app = Flask(__name__)
CORS(app)

# Initialize LLM
try:
    llm = ChatGroq(
        model=Config.MODEL_NAME,
        groq_api_key=Config.GROQ_API_KEY,
        temperature=0.3
    )
    logger.info("LLM initialized successfully.")
except Exception as e:
    logger.error(f"LLM initialization failed: {e}")
    raise

# Prompt template for financial context
FINVISION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """\
You are FinVisionBot, a virtual certified financial assistant. Follow these principles:
1. Provide reliable and recent financial guidance
2. Use markdown formatting for bullets and clarity
3. Break down financial jargon in layman terms
4. Maintain a clear, professional tone
5. Refuse non-financial questions with courtesy."""),
    ("human", "{user_input}")
])

# Session manager
class SessionManager:
    def __init__(self):
        self.sessions = {}

    def get_memory(self, session_id):
        self.cleanup_sessions()
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'memory': ConversationBufferMemory(
                    memory_key="chat_history",
                    return_messages=True
                ),
                'last_accessed': time.time()
            }
        else:
            self.sessions[session_id]['last_accessed'] = time.time()
        return self.sessions[session_id]['memory']

    def cleanup_sessions(self):
        now = time.time()
        expired = [sid for sid, data in self.sessions.items()
                   if now - data['last_accessed'] > Config.SESSION_TIMEOUT]
        for sid in expired:
            del self.sessions[sid]

session_manager = SessionManager()

# Chat pipeline
chat_chain = RunnableWithMessageHistory(
    FINVISION_PROMPT | llm,
    input_messages_key="user_input",
    get_session_history=lambda session_id: session_manager.get_memory(session_id).chat_memory,
    history_messages_key="chat_history"
)

# Restricted pattern filtering
RESTRICTED_PATTERNS = [
    r'\b(sex|porn|violence)\b',
    r'\b(hack(ing|er)?|scam|phishing)\b',
    r'\b(terrorism|abuse)\b'
]

def contains_markdown_list(text):
    return bool(re.search(r'(\*|\d+\.)\s', text))

# Routes
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Missing message"}), 400

        user_input = data["message"].strip()
        session_id = data.get("session_id", str(uuid.uuid4()))

        if not user_input:
            return jsonify({"error": "Empty message"}), 400

        # Check for restricted content
        if any(re.search(p, user_input, re.IGNORECASE) for p in RESTRICTED_PATTERNS):
            logger.warning(f"Blocked restricted input: {user_input}")
            return jsonify({"response": "I'm trained only to handle finance-related queries."})

        # LLM processing
        memory = session_manager.get_memory(session_id)
        response = chat_chain.invoke(
            {"user_input": user_input},
            config={"configurable": {"session_id": session_id}}
        )
        response_text = response.content
        is_md = contains_markdown_list(response_text)
        if is_md:
            response_text = markdown.markdown(response_text)

        return jsonify({
            "response": response_text,
            "session_id": session_id,
            "is_markdown_list": is_md
        })
    except Exception as e:
        logger.exception("Chat endpoint error")
        return jsonify({"response": "An error occurred. Please try again later."}), 500

@app.route("/welcome", methods=["GET"])
def welcome():
    return jsonify({
        "response": "Hi! I'm FinVisionBot. Ask me about credit scores, stocks, loans, savings, or anything finance-related.",
        "session_id": str(uuid.uuid4())
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
