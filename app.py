import os
import logging
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = app.logger
logger.setLevel(logging.DEBUG)

# Define default model
DEFAULT_MODEL = "gpt-4o"

def extract_relevant_keywords(job_description: str, model=DEFAULT_MODEL) -> str:
    prompt = (
        "You are a professional career advisor. Extract the most important technical skills, intrapersonal sklls, "
        "and qualifications from the following job description. "
        "Return the results as a comma-separated list.\n\n"
        f"Job Description:\n{job_description}\n\n"
    )

    logger.debug("Sending request to OpenAI for keyword extraction...")
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.3
    )
    result = response.choices[0].message.content.strip()
    logger.debug(f"Keywords extracted: {result}")
    return result

def extract_benefits(job_description: str, model=DEFAULT_MODEL) -> str:
    prompt = (
        "You are a professional career advisor.  Extract all the benefits listed for the following job description."
        "If compensation range is listed, please return that first.  Return all the results as a comma-separated list.\n\n"
        f"Job Description:\n{job_description}\n\n"
    )

    logger.debug("Sending request to OpenAI for benefit extraction...")
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.3
    )
    result = response.choices[0].message.content.strip()
    logger.debug(f"Benefits Extracted: {result}")
    return result

def suggest_resume_improvements(resume_text: str, job_description: str, model=DEFAULT_MODEL) -> str:
    prompt = (
        "You are a professional resume writer. You have been given a resume (in LaTeX) and a job description. "
        "Analyze the resume and identify how it can be improved and tailored to better match the job description. "
        "Do not rewrite the entire resume here, just list suggestions. "
        "Focus on skills, keywords, relevant experience, and how to emphasize the candidate's fit.\n\n"
        "Assume that the candidate has a strong background in many technologies that aren't necessarily mentioned in the original resume.\n\n"
        f"Job Description:\n{job_description}\n\n"
        f"Resume:\n{resume_text}\n\n"
        "List out suggestions in bullet points."
    )

    logger.debug("Sending request to OpenAI for resume improvements suggestions...")
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.3
    )
    result = response.choices[0].message.content.strip()
    logger.debug(f"Suggestions generated: {result}")
    return result

def generate_optimized_resume(resume_text: str, suggestions: str, model=DEFAULT_MODEL) -> str:
    prompt = (
        "You are a professional resume writer skilled in LaTeX formatting. "
        "You have a non-LaTeX-formatted resume and a set of improvement suggestions. "
        "Incorporate these suggestions into the resume and add LaTeX formatting and structure. "
        "Do not remove the original formatting commands, only update text where it makes sense. "
        "Make sure to incorporate relevant keywords, highlight experiences and skills that match the job description.\n\n"
        f"Suggestions:\n{suggestions}\n\n"
        f"Original Resume:\n{resume_text}\n\n"
        "Return the full updated resume in LaTeX."
    )

    logger.debug("Sending request to OpenAI for optimized resume generation...")
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000,
        temperature=0.3
    )
    result = response.choices[0].message.content.strip()
    logger.debug(f"Optimized resume generated.")
    return result

@app.route('/extract-keywords', methods=['POST'])
def api_extract_keywords():
    logger.debug("Received request at /extract-keywords endpoint")
    data = request.get_json()
    if not data:
        logger.debug("No JSON data provided.")
        return jsonify({"error": "No JSON data provided"}), 400

    job_description = data.get('job_description', '')
    logger.debug(f"Job description: {job_description}")
    if not job_description:
        logger.debug("No job description provided.")
        return jsonify({"error": "No job description provided"}), 400

    keywords = extract_relevant_keywords(job_description)
    return jsonify({"keywords": keywords})

@app.route('/extract-benefits', methods=['POST'])
def api_extract_benefits():
    logger.debug("Received request at /extract-benefits endpoint")
    data = request.get_json()
    if not data:
        logger.debug("No JSON data provided.")
        return jsonify({"error": "No JSON data provided"}), 400

    job_description = data.get('job_description', '')
    logger.debug(f"Job description: {job_description}")
    if not job_description:
        logger.debug("No job description provided.")
        return jsonify({"error": "No job description provided"}), 400

    benefits = extract_benefits(job_description)
    return jsonify({"keywords": benefits})

@app.route('/suggest-improvements', methods=['POST'])
def api_suggest_improvements():
    logger.debug("Received request at /suggest-improvements endpoint")
    data = request.get_json()
    if not data:
        logger.debug("No JSON data provided.")
        return jsonify({"error": "No JSON data provided"}), 400

    resume_text = data.get('resume_text', '')
    job_description = data.get('job_description', '')

    if not job_description:
        logger.debug("No job description provided.")
        return jsonify({"error": "No job description provided"}), 400
    if not resume_text:
        logger.debug("No resume text provided.")
        return jsonify({"error": "No resume text provided"}), 400

    suggestions = suggest_resume_improvements(resume_text, job_description)
    return jsonify({"suggestions": suggestions})

@app.route('/generate-optimized-resume', methods=['POST'])
def api_generate_optimized_resume():
    logger.debug("Received request at /generate-optimized-resume endpoint")
    data = request.get_json()
    if not data:
        logger.debug("No JSON data provided.")
        return jsonify({"error": "No JSON data provided"}), 400

    resume_text = data.get('resume_text', '')
    suggestions = data.get('suggestions', '')

    if not resume_text:
        logger.debug("No resume text provided.")
        return jsonify({"error": "No resume text provided"}), 400
    if not suggestions:
        logger.debug("No suggestions provided.")
        return jsonify({"error": "No suggestions provided"}), 400

    optimized_resume = generate_optimized_resume(resume_text, suggestions)
    return jsonify({"optimized_resume": optimized_resume})

if __name__ == "__main__":
    logger.debug("Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5001, use_reloader=True)