from flask import Flask, render_template, request
from pypdf import PdfReader
import time
import os
import json
import hashlib
from ai_resume_parser import analyze_resume_with_groq
#Official flask shiz
app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
JSON_CACHE_FOLDER = 'json_cache'
ALLOWED_EXTENSION = {'pdf'}



#Home page
@app.route("/")
def home():
    return render_template("upload.html")    


""" Check if the file extension is in ALLOWED_EXTENSION"""
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSION


""" For extracting text in pdf. """
def extract_text_from_pdf(filepath):
    reader = PdfReader(filepath)
    pdf_text = ""
    for page in reader.pages:
        page_text = page.extract_text(extraction_mode="layout")
        if page_text:
            pdf_text += page_text
    
    return pdf_text
    

""" For file uploading and saving to folder /uploads. """
@app.route("/file_upload", methods=['POST'])
def file_upload():
    file = request.files['myfile']
    
    if file and allowed_file(file.filename):
        
        """For unique naming of resume file"""
        file_content = file.read()
        file.seek(0)
        file_hash = hashlib.sha256(file_content).hexdigest()
        _, ext = os.path.splitext(file.filename)
        filename = f"{file_hash}{ext.lower()}" 
        
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        #return f"<h1> {file.filename} uploaded to {UPLOAD_FOLDER}!</h1>"
        #return render_template("file_msg.html", folder=UPLOAD_FOLDER, filename=file.filename)
        
        """ JSON process converting"""
        json_filename = filename.replace('.pdf', '.json')
        json_filepath = os.path.join(JSON_CACHE_FOLDER, json_filename)
        resume_data = {}
        
        if os.path.exists(json_filepath):
            # Cache HIT: The file exists! Load the pre-parsed data.
            print("INFO: Loaded data from JSON cache. SKIPPING GROQ API CALL.")
            with open(json_filepath, 'r') as f:
                resume_data = json.load(f)
        else:
            # Cache MISS: The file does NOT exist. We must call Groq.
            print("INFO: JSON cache miss. Analyzing with Groq...")
            
            # Extract text (must be done if we miss the cache)
            pdf_text = extract_text_from_pdf(filepath) 
            
            # Analyze with Groq (this is the expensive/slow step)
            resume_data = analyze_resume_with_groq(pdf_text)
            
            # We only cache it if the API call was successful (no 'error' key)
            if "error" not in resume_data:
                with open(json_filepath, 'w') as f:
                    # json.dump converts the Python dictionary into a JSON string and writes it to the file
                    json.dump(resume_data, f, indent=2)
                print(f"INFO: Successfully saved new JSON cache file: {json_filename}")
        
        
        # For extracting text in pdf
        pdf_text = extract_text_from_pdf(filepath)
        
        return render_template("extracted_text.html", filename=filename, pdf_text=pdf_text, resume_data=resume_data)
        
    else:
        return "<h1> No file uploaded </h1>"


# For debugging
if __name__ == '__main__':
    app.run(debug=True)
    