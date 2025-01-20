from flask import Flask, jsonify, request
from scrape_twitter import scrape_twitter  
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Twitter Trends Scraper is running!"

@app.route("/run-script", methods=["POST"])  
def run_script():
    print("Inside run_script function...")
    try:
        result = scrape_twitter() 
        return jsonify(result)  
    except Exception as e:
        print(f"Error during script execution: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)  
