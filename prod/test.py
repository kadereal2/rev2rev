
import os
import pandas as pd
import tensorflow as tf
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from tensorflow.keras.preprocessing.text import tokenizer_from_json
import json

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

import openai 
from prod.openai_topic_modeling2 import run_analysis 
from dotenv import load_dotenv

app = FastAPI()

# Allowing all middleware is optional, but good practice for dev purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.state.model  = tf.keras.models.load_model('prod/RNNGRUDropout_model.h5')


with open('prod/tokenizer_dropout.json', 'r', encoding='utf-8') as f:
      tokenizer_json = json.load(f)

tokenizer = tokenizer_from_json(tokenizer_json)

# Define a root `/` endpoint
@app.get('/')
def index():
    return {'ok': "API works"}


@app.post("/analyze3")
def analyze(file: UploadFile = File(...)):
    
    df = pd.read_csv(file.file)

    if 'content' in df.columns:       
        X = df["content"]
        # How is my pipeline do I have to process my X -> yes
        MAX_SEQ_LEN = 256

        sequences = tokenizer.texts_to_sequences(X)
        Xtp = pad_sequences(sequences, maxlen=MAX_SEQ_LEN)

        # Prdecit the sentiment analysis
        model_sent = app.state.model
        assert model_sent is not None
        y_pred = model_sent.predict(Xtp) 
        df["sentiment_score"] = np.argmax(y_pred, axis=1) + 1

        # Aggregate sentiment distribution
        sentiment_summary = {
            "1-star": round((len(df[df["sentiment_score"] == 1]) / len(df)) * 100, 2),
            "2-star": round((len(df[df["sentiment_score"] == 2]) / len(df)) * 100, 2),
            "3-star": round((len(df[df["sentiment_score"] == 3]) / len(df)) * 100, 2),
            "4-star": round((len(df[df["sentiment_score"] == 4]) / len(df)) * 100, 2),            
            "5-star": round((len(df[df["sentiment_score"] == 5]) / len(df)) * 100, 2)
        }
        df["at"] = pd.to_datetime(df["at"])
        time_period = f"{df['at'].min().date()} to {df['at'].max().date()}"
        
        df_grouped = df.groupby([df["at"],"sentiment_score"])
        
        df["date"] = df["at"].dt.date
        df_grouped = df.groupby(["date", "sentiment_score"]).size().reset_index(name="count")
        df_grouped.sort_values("date", ascending=False)
        
        #TOPIC MODELING
        
        reviews = df['content'].tolist()
            # Check if there are any reviews to analyze
        if not reviews:
            return {"error": "No reviews found in the CSV file."}
            
        # Perform topic modeling on all reviews
        results = run_analysis(reviews)

        response_data = {
            "sentiment_analysis": sentiment_summary,
            "total_reviews": len(df),
            "average_rating": round(df["sentiment_score"].mean(), 1),            
            "median_rating": int(df["sentiment_score"].median()) ,
            "time_period": time_period ,
            "all_data" : df[["at","sentiment_score","content"]].to_dict(orient="records"),
            "groupued" : df_grouped.to_dict(orient="records"),
            "topic_modeling" : results 
        }

        response_data = {key: value.item() if isinstance(value, (np.int64, np.float64)) else value for key, value in response_data.items()}
        return response_data
    return {"error": "missing 'content' column!"}    