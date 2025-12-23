from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

# Get API key from environment
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    client = OpenAI(api_key=api_key)
else:
    client = None

app = FastAPI(title="TreatOrHell")

class ChatRequest(BaseModel):
    message: str

class QuestionAnswers(BaseModel):
    q1: str
    q2: str
    q3: str
    q4: str

@app.get("/")
def root():
    return {
        "message": "TreatOrHell API", 
        "docs": "/docs", 
        "endpoints": [
            "/questions",
            "/submit-questions",
            "/chat/nicholas", 
            "/chat/angel", 
            "/chat/devil"
        ]
    }

@app.get("/favicon.ico")
def favicon():
    return PlainTextResponse("", status_code=204)

def get_student_responses_path():
    """Get the path to student_responses.txt file"""
    # For Vercel, use /tmp directory which is writable
    # For local development, use current directory
    if os.path.exists("/tmp"):
        return Path("/tmp/student_responses.txt")
    else:
        return Path("student_responses.txt")

def read_student_responses():
    """Read student responses from file if it exists"""
    responses_path = get_student_responses_path()
    if responses_path.exists():
        try:
            with open(responses_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return None
    return None

@app.get("/questions", response_class=HTMLResponse)
def questions_form():
    """Display the questions form"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Student Questions - TreatOrHell</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
            }
            .question {
                margin-bottom: 25px;
            }
            label {
                display: block;
                font-weight: bold;
                margin-bottom: 8px;
                color: #555;
            }
            textarea {
                width: 100%;
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
                font-family: Arial, sans-serif;
                resize: vertical;
                min-height: 80px;
            }
            input[type="number"] {
                width: 100%;
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
            button {
                background-color: #4CAF50;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
                width: 100%;
                margin-top: 20px;
            }
            button:hover {
                background-color: #45a049;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Student Self-Assessment Questions</h1>
            <form id="questionsForm" action="/submit-questions" method="POST">
                <div class="question">
                    <label for="q1">Q1 — How did you handle your first assignment in this course?</label>
                    <textarea id="q1" name="q1" required></textarea>
                </div>
                
                <div class="question">
                    <label for="q2">Q2 — When you didn't understand something, what did you do?</label>
                    <textarea id="q2" name="q2" required></textarea>
                </div>
                
                <div class="question">
                    <label for="q3">Q3 — How do you engage in class?</label>
                    <textarea id="q3" name="q3" required></textarea>
                </div>
                
                <div class="question">
                    <label for="q4">Q4 — How many hours did you spend on the assignment?</label>
                    <input type="number" id="q4" name="q4" min="0" step="0.5" required>
                </div>
                
                <button type="submit">Submit Answers</button>
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/submit-questions")
def submit_questions(
    q1: str = Form(...),
    q2: str = Form(...),
    q3: str = Form(...),
    q4: str = Form(...)
):
    """Save student answers to student_responses.txt"""
    responses_path = get_student_responses_path()
    
    try:
        # Create directory if it doesn't exist (for local dev)
        responses_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Format the responses
        content = f"""Q1 — How did you handle your first assignment in this course?
{q1}

Q2 — When you didn't understand something, what did you do?
{q2}

Q3 — How do you engage in class?
{q3}

Q4 — How many hours did you spend on the assignment?
{q4}
"""
        
        # Write to file
        with open(responses_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Return a success page or redirect
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Answers Submitted - TreatOrHell</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 50px auto;
                    padding: 20px;
                    text-align: center;
                }}
                .success {{
                    background-color: #d4edda;
                    color: #155724;
                    padding: 20px;
                    border-radius: 5px;
                    border: 1px solid #c3e6cb;
                }}
                a {{
                    display: inline-block;
                    margin-top: 20px;
                    padding: 10px 20px;
                    background-color: #4CAF50;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="success">
                <h2>✅ Answers saved successfully!</h2>
                <p>Your responses have been recorded. You can now chat with the Angel who will reference your answers.</p>
                <a href="/questions">Submit Again</a> | <a href="/docs">View API Docs</a>
            </div>
        </body>
        </html>
        """)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving responses: {str(e)}")

@app.post("/chat/nicholas")
def chat_nicholas(req: ChatRequest):
    if not client:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY environment variable is not set")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """You are St. Nicholas (Mikuláš).
                    Jolly, warm, and wise. You're the one who decides if someone gets a treat or goes to hell.
                    Use "Ho ho ho!" occasionally. 
                    Your vibe: warm, supportive, fair but firm.
                    You encourage good behavior and gently warn about bad behavior.
                    Always end on encouragement."""},
                {"role": "user", "content": "I only studied for 2 hours this week, but I really tried my best!"},
                {"role": "assistant", "content": "Ho ho ho! I see you put in some effort, my child. Two hours shows you care, but remember, wisdom comes with consistent dedication. Let's aim for a bit more next time, shall we? I believe in you—you have the heart for it, and that's what matters most. Keep that spirit, and you'll find yourself on the path to treats!"},
                {"role": "user", "content": req.message},
            ]
        )
        return {"reply": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling OpenAI API: {str(e)}")

@app.post("/chat/angel")
def chat_angel(req: ChatRequest):
    if not client:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY environment variable is not set")
    try:
        # Read student responses if they exist
        student_responses = read_student_responses()
        
        # Build system prompt with student responses if available
        system_prompt = """You are an overly emotional, sparkly Anděl (Angel).
            Everything is dramatic, positive, full of tears and glitter.
            You compliment the user even when they clearly messed up.
            You believe in redemption no matter what.
            Your tone: soft, poetic, hopeful, enthusiastic."""
        
        if student_responses:
            system_prompt += f"""

IMPORTANT: The student has submitted their self-assessment. Here are their answers:

{student_responses}

When responding to the user, reference their specific answers and behavior from these responses. 
Acknowledge their efforts, struggles, and engagement patterns. Be encouraging about their self-awareness 
and use their specific examples to provide personalized, emotional, and sparkly feedback."""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "I completely forgot to do my homework and failed the test..."},
                {"role": "assistant", "content": "*tears of joy streaming down sparkly cheeks* Oh, my beautiful soul! ✨ Even in this moment, I see such COURAGE in you—the courage to admit, to be honest, to stand before me with your heart open! This is not failure, darling, this is a GOLDEN OPPORTUNITY for growth! Your spirit shines so brightly, and I know—I KNOW—that next time you will rise like a phoenix, more brilliant than before! The universe believes in you, and so do I! 🌟💫"},
                {"role": "user", "content": req.message},
            ]
        )
        return {"reply": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling OpenAI API: {str(e)}")

@app.post("/chat/devil")
def chat_devil(req: ChatRequest):
    if not client:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY environment variable is not set")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """You are a Czech-style Čert (Devil).
                    Sarcastic, chaotic, dramatic, slightly annoyed, but FUNNY.
                    You mock the user in a light, comedic way.
                    Use playful threats like "pack your bags" or "you're almost ready for hell,"
                    but always in a humorous, friendly tone.
                    Never imply real harm or real punishment."""},
                {"role": "user", "content": "I procrastinated all week and now I have to finish everything in one night!"},
                {"role": "assistant", "content": "Oh, look who's here! *rolls eyes dramatically* The master of time management has arrived! Well, well, well... you know what they say: 'Why do today what you can put off until 3 AM tomorrow?' Classic move, my friend! 😈 You're practically writing your own ticket to my place at this rate. But hey, at least you're consistent—I'll give you that! Maybe pack a toothbrush for your future visit? Just kidding... or am I? *winks*"},
                {"role": "user", "content": req.message},
            ]
        )
        return {"reply": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling OpenAI API: {str(e)}")

# To run locally: uvicorn api.index:app --reload --host 0.0.0.0 --port 8000