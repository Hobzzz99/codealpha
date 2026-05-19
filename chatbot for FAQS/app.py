import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    print("Warning: GEMINI_API_KEY not found. Gemini fallback will be disabled.")
    model = None

# Download NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# FAQ Data
faqs = [
    {"question": "How do I reset my password?", "answer": "You can reset your password by clicking 'Forgot Password' on the login page and following the instructions sent to your email."},
    {"question": "Why is my internet so slow?", "answer": "Try restarting your router. If the issue persists, contact your ISP or check for local outages."},
    {"question": "How do I clear my browser cache?", "answer": "In most browsers, you can press Ctrl+Shift+Delete to open the clear browsing data menu."},
    {"question": "How can I update my drivers?", "answer": "You can update drivers through Windows Update or by visiting the manufacturer's website for your specific hardware."},
    {"question": "What should I do if my computer won't turn on?", "answer": "Check the power cables, ensure the outlet is working, and try a different power adapter if possible."},
    {"question": "How do I install a new software?", "answer": "Download the installer from a trusted source and follow the on-screen prompts after opening the file."},
    {"question": "How do I take a screenshot?", "answer": "You can use the 'Print Screen' key or the 'Snipping Tool' (Windows key + Shift + S)."},
    {"question": "How to fix blue screen error?", "answer": "Restart your computer. If it persists, boot in Safe Mode and uninstall recently added hardware or software."},
    {"question": "My printer is not working.", "answer": "Check if it's connected to the Wi-Fi/computer, ensure there's paper and ink, and try restarting the print spooler service."},
]

faq_questions = [faq["question"] for faq in faqs]

def preprocess(text):
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    tokens = [t for t in tokens if t.isalpha() and t not in stop_words]
    return " ".join(tokens)

preprocessed_faqs = [preprocess(q) for q in faq_questions]
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(preprocessed_faqs)

class Query(BaseModel):
    question: str

async def get_gemini_response(prompt):
    if not model:
        return "I'm sorry, I'm having trouble connecting to my brain (API Key missing). Please check the server logs."
    
    try:
        # Contextualize the prompt for Tech Support
        full_prompt = f"You are a helpful Tech Support Assistant. Answer the following user question clearly and concisely: {prompt}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "I'm sorry, I encountered an error while processing your request."

@app.post("/chat")
async def chat(query: Query):
    user_q = preprocess(query.question)
    
    if not user_q:
        # If preprocessing leaves nothing (e.g., "hi", "hello"), use Gemini for a conversational greeting
        return {"answer": await get_gemini_response(query.question)}
    
    user_tfidf = vectorizer.transform([user_q])
    similarities = cosine_similarity(user_tfidf, tfidf_matrix)
    
    index = similarities.argmax()
    score = similarities[0][index]
    
    # Threshold for FAQ match
    if score > 0.4:
        return {"answer": faqs[index]["answer"]}
    else:
        # Fallback to Gemini for low-confidence or out-of-FAQ questions
        return {"answer": await get_gemini_response(query.question)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
