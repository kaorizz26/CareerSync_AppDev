import requests
import json
import os

# Your own groq api key...
GROQ_API_KEY = ""  

def analyze_resume_with_groq(extracted_text):
    
    # For the prompting in AI
    prompt = f"""Extract job-search information from this resume into JSON.

Return ONLY this JSON structure:
{{
  "name": "",
  "email": "",
  "target_title": "",
  "total_years_experience": 0,
  "skills": [],
  "work_history": [
    {{
      "company": "",
      "title": "",
      "start_date": "",
      "end_date": ""
    }}
  ],
  "education": {{
    "degree": "",
    "institution": ""
  }}
}}

Rules:
- target_title: The job position they want or currently have
- total_years_experience: Calculate total years from all jobs
- skills: List ALL technical skills mentioned
- start_date/end_date: Use "YYYY-MM" or "Present"

Resume:
{extracted_text}"""
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",  # Super fast!
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a resume parser. Return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.1
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            return json.loads(content)
        else:
            return {"error": f"Groq API error: {response.status_code}"}

    except requests.exceptions.ConnectionError:
        return {"error": "No internet connection"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON from AI"}
    except Exception as e:
        return {"error": str(e)}


# For backward compatibility, keep same function name
def analyze_resume_with_ollama(extracted_text):
    return analyze_resume_with_groq(extracted_text)