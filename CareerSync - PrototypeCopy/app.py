from flask import Flask, render_template, request
from pypdf import PdfReader
import time
import os
import json
import hashlib
from ai_resume_parser import analyze_resume_with_groq
from jobspy import scrape_jobs
import pandas as pd

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
        # pdf_text = extract_text_from_pdf(filepath)
        
        # return render_template("extracted_text.html", filename=filename, pdf_text=pdf_text, resume_data=resume_data)
        
    else:
        return "<h1> No file uploaded </h1>"
    
    #---- FOR GEMINI CODE-------------------
    
    # --- START NEW CODE (Job Search + Analytics) ---

    # 1. Get search terms from the parsed resume JSON
    target_title = resume_data.get('target_title', '') # Get 'Business Analyst' or 'Web Developer'
    skills_list = resume_data.get('skills', [])[:5]  # Get top 5 skills
    
    search_term = f"{target_title} {' '.join(skills_list)}"
    print(f"INFO: Searching jobspy with term: {search_term}")

    # 2. Call jobspy API
    # (Using 'linkedin' for speed; 'indeed' is also good. Using Philippines as location)
    jobs_df = scrape_jobs(
        site_name=['linkedin'],
        search_term=search_term,
        location='Philippines',
        results_limit=15,
        linkedin_fetch_description=True # REQUIRED for analytics
    )

    jobs_html = "" # Initialize

    # 3. Handle no results
    if jobs_df is None or jobs_df.empty:
        print("INFO: No jobs found by jobspy.")
        jobs_html = "<p>No matching jobs found. Try a different resume.</p>"
    else:
        # 4. Convert DataFrame to HTML table (This is your UI!)
        # We select only the most important columns for the prototype
        columns_to_show = ['title', 'company', 'location', 'job_url']
        
        # Ensure all required columns exist, adding them as empty if they don't
        for col in columns_to_show:
            if col not in jobs_df.columns:
                jobs_df[col] = "N/A"

        # Make the job_url clickable
        jobs_df['job_url'] = jobs_df['job_url'].apply(lambda x: f'<a href="{x}" target="_blank">Apply</a>')
        
        jobs_html = jobs_df[columns_to_show].to_html(
            escape=False,  # This allows the <a> tags to render as links
            index=False, 
            classes="table table-striped", # Adds bootstrap styling
            justify="left"
        )

    # --- START DATA ANALYTICS CODE ---
    
    print("INFO: Starting data analytics...")
    skill_analytics = {}
    
    # Only run analytics if jobs were found AND we have the description column
    if jobs_df is not None and not jobs_df.empty and 'description' in jobs_df.columns:
        
        # 1. Get user skills from the JSON
        user_skills = resume_data.get('skills', [])
        
        # 2. Combine all job descriptions into one big lowercase text block
        all_descriptions = " ".join(jobs_df['description'].dropna().astype(str)).lower()

        # 3. Count matches
        for skill in user_skills:
            # Check for the skill as a whole word to avoid "js" matching "projects"
            count = all_descriptions.count(skill.lower())
            if count > 0:
                skill_analytics[skill] = count

        # 4. Sort the dictionary by count (most frequent first)
        skill_analytics = dict(sorted(skill_analytics.items(), 
                                      key=lambda item: item[1], 
                                      reverse=True))
        print(f"INFO: Analytics complete: {skill_analytics}")

    # 6. Render the new results page
    return render_template("job_results.html", 
                           user_name=resume_data.get('name', 'User'),
                           jobs_table=jobs_html,
                           analytics_data=skill_analytics) 
    
    # --- END NEW CODE ---
    # ----- END GEMINI CODE---------------


# For debugging
if __name__ == '__main__':
    app.run(debug=True)
    