from flask import Flask, jsonify, request
from pymongo import MongoClient
from transformers import BertTokenizer, BertForSequenceClassification
import torch

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb+srv://pallavik15092004:miniproject@cluster0.l1wif.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")  # replace with your MongoDB URI
db = client["test"]
print("Connected to MongoDB")
user_interactions = db["userinteractions"]
search_history = db["searchhistories"]
user_recommendations = db["user_recommendations"]  # This will store user recommendations

# Load pre-trained BERT model
model_name = "bert-base-uncased"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name)

# Helper function to retrieve user interaction and search history
def get_user_data(user_id):
    # Fetch user interaction and search history from MongoDB
    interactions = list(user_interactions.find({"user_id": user_id}))
    searches = list(search_history.find({"user_id": user_id}))
    print( interactions, searches)

# Preprocess data for BERT (combining product names and search queries)
def preprocess_data(interactions, searches):
    input_text = ""
    for interaction in interactions:
        input_text += interaction["product_name"] + " "  # Add the product names
    for search in searches:
        input_text += search["search_query"] + " "  # Add the search queries
    return input_text

# Function to get product recommendations from BERT
def get_recommendations(input_text):
    # Tokenize input text and make it suitable for BERT
    inputs = tokenizer(input_text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    
    with torch.no_grad():
        outputs = model(**inputs)  # Get model output (logits)
    
    predictions = outputs.logits  # Extract logits
    return predictions

# Function to process logits and map them to actual product recommendations
def process_recommendations(predictions):
    # Assuming the logits correspond to product scores, here we convert them
    # You can refine this logic to map predictions to actual products
    product_scores = predictions.softmax(dim=1)  # Apply softmax to get probabilities
    scores = product_scores.squeeze(0).tolist()  # Convert tensor to list
    return scores

# Function to store recommendations in MongoDB
def store_recommendations(user_id, recommended_products):
    # Store or update recommendations in MongoDB
    user_recommendations.update_one(
        {"user_id": user_id},
        {"$set": {"recommended_products": recommended_products}},
        upsert=True  # Insert the document if it doesn't exist
    )

# API endpoint for getting and processing recommendations
@app.route("/recommendations/<user_id>", methods=["GET"])
def recommendations(user_id):
    # Fetch user interaction and search data
    interactions, searches = get_user_data(user_id)
    
    if not interactions and not searches:
        return jsonify({"error": "No interactions or search history found for user."}), 404
    
    # Preprocess data to combine interactions and searches
    input_text = preprocess_data(interactions, searches)
    
    # Get recommendations from the BERT model
    predictions = get_recommendations(input_text)
    
    # Process the logits to get product recommendations
    scores = process_recommendations(predictions)
    
    # Map scores to actual product recommendations (you should adjust based on your product data)
    recommended_products = [{"product_id": str(i), "score": score} for i, score in enumerate(scores)]
    
    # Store the recommendations in MongoDB
    store_recommendations(user_id, recommended_products)
    
    # Return the recommendations as a response
    return jsonify({"user_id": user_id, "recommended_products": recommended_products})

# Handle 404 errors for undefined routes
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Route not found"}), 404

# Handle favicon.ico requests
@app.route('/favicon.ico')
def favicon():
    return '', 204  # No content for favicon

if __name__ == "__main__":
    app.run(debug=True)
