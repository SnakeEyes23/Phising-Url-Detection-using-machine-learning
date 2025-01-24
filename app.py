from flask import Flask, request, jsonify, render_template, send_file
import joblib
import re
import os

app = Flask(__name__)

rf_model = joblib.load('random_forest_model.pkl')
lr_model = joblib.load('logistic_regression_model.pkl')
vectorizer = joblib.load('vectorizer.pkl')

def preprocess_url(url):
    url = url.lower()
    url = re.sub(r'https?://', '', url)
    url = re.sub(r'www\.', '', url)
    url = re.sub(r'[^a-zA-Z0-9]', ' ', url)
    return url

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        url = request.form['url']
        
        processed_url = preprocess_url(url)
        features = vectorizer.transform([processed_url]).toarray()
        
        rf_prediction = rf_model.predict(features)[0]
        lr_prediction = lr_model.predict(features)[0]
        
        # Final prediction
        prediction = "Phishing" if rf_prediction == 1 or lr_prediction == 1 else "Legitimate"
        
        # Generate a report
        report_content = f"URL: {url}\nPrediction: {prediction}"
        report_filename = "url_analysis_report.txt"
        with open(report_filename, 'w') as file:
            file.write(report_content)
        
        return jsonify({
            "url": url,
            "prediction": prediction,
            "report_filename": report_filename
        })
    
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/download/<filename>')
def download_report(filename):
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
