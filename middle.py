from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
from runner import WordleSolver  # Your existing WordleSolver class

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store solver instances
solvers: Dict[str, WordleSolver] = {}

class GuessRequest(BaseModel):
    session_id: str
    word_length: int

class FeedbackRequest(BaseModel):
    session_id: str
    guess: str
    feedback: List[str]

@app.post("/initialize")
async def initialize_solver(request: GuessRequest):
    try:
        solver = WordleSolver(request.word_length)
        solver.preSetup()
        
        # Load initial entropy data
        with open(f"database/{request.word_length}Letter/initialEntropy.csv", "r") as file:
            next(file)  # Skip header
            entropy_data = {row.split(',')[0]: float(row.split(',')[1]) 
                          for row in file.readlines()}
        
        # Get top 10 words by entropy for visualization
        top_words = sorted(entropy_data.items(), key=lambda x: x[1], reverse=True)[:10]
        
        solvers[request.session_id] = solver
        
        return {
            "status": "success",
            "total_words": len(solver.possibleWords),
            "probabilities": [{"word": word, "probability": entropy} for word, entropy in top_words]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/get_suggestion")
async def get_suggestion(request: GuessRequest):
    try:
        solver = solvers.get(request.session_id)
        if not solver:
            raise HTTPException(status_code=404, detail="Session not found")
            
        # Get current entropy data for remaining words
        entropy_data = {word: solver.computeEntropy(word) for word in solver.possibleWords}
        best_guess = solver.getBestGuess(entropy_data)
        
        # Get top 10 words by entropy for visualization
        top_words = sorted(entropy_data.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "suggestion": best_guess,
            "remaining_words": len(solver.possibleWords),
            "probabilities": [{"word": word, "probability": entropy} for word, entropy in top_words]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/submit_feedback")
async def submit_feedback(request: FeedbackRequest):
    try:
        solver = solvers.get(request.session_id)
        if not solver:
            raise HTTPException(status_code=404, detail="Session not found")
            
        # Process feedback
        feedback_tuple = tuple(request.feedback)
        solver.filterWords(feedback_tuple, request.guess)
        solver.used_guesses.add(request.guess)
        
        # Get updated entropy data
        entropy_data = {word: solver.computeEntropy(word) for word in solver.possibleWords}
        top_words = sorted(entropy_data.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "remaining_words": len(solver.possibleWords),
            "probabilities": [{"word": word, "probability": entropy} for word, entropy in top_words]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))