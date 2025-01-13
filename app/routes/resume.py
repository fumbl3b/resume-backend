import logging
from app.services.file_processor import FileProcessor
from app.services.error_service import generate_error
from flask import Blueprint, jsonify, request
from app.config import DEFAULT_MODEL
from app.extensions import client

resume_bp = Blueprint('resume', __name__)
logger = logging.getLogger(__name__)


def suggest_improvements(resume_text, job_description, model=DEFAULT_MODEL):
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
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.3
    )
    result = response.choices[0].message.content.strip()
    logger.debug(f"Suggestions generated: {result}")
    return result

def apply_improvements(resume_text, suggestions, model=DEFAULT_MODEL):
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
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000,
        temperature=0.1  # Lower temperature for more consistent output
    )
    return response.choices[0].message.content.strip()

@resume_bp.route('/extract-text', methods=['POST'])
def api_extract_resume_text():
    logger.debug("Received file upload request")
    
    # Check content type
    if not request.content_type or 'multipart/form-data' not in request.content_type:
        logger.error(f"Invalid content type: {request.content_type}")
        return jsonify({"error": "Invalid content type"}), 415

    if 'file' not in request.files:
        return generate_error("No file in request")
        
    file = request.files['file']
    if file.filename == '':
        return generate_error("Empty filename")
        
    logger.debug(f"Processing file: {file.filename}")
    
    # Validate file type
    allowed_extensions = {'pdf', 'doc', 'docx', 'tex'}
    if not file.filename.lower().endswith(tuple(f'.{ext}' for ext in allowed_extensions)):
        return generate_error("Invalid file type", 415)
        
    try:
        text = FileProcessor.extract_text(file.stream, file.filename)
        logger.debug(f"Successfully extracted text from {file.filename}")
        return jsonify({"text": text})
    except ValueError as e:
        return generate_error(f"Value error proccesing file: {str(e)}")
    except Exception as e:
        return generate_error(f"Error processing file: {str(e)}", 500)

@resume_bp.route('/suggest-improvements', methods=['POST'])
def api_suggest_improvements():
    logger.debug("Received request at /suggest-improvements endpoint")
    data = request.get_json()
    if not data:
        return generate_error("No JSON data provided.")
    
    resume_text = data.get('resume_text', '')
    job_description = data.get('job_description', '')

    if not job_description:
        return generate_error("No job description provided.")
    if not resume_text:
        return generate_error("No resume text provided.")
    
    suggestions = suggest_improvements(resume_text, job_description)
    return jsonify({"suggestions": suggestions})

@resume_bp.route('/apply-improvements', methods=['POST'])
def api_apply_improvements():
    logger.debug("Received request at /apply-improvements endpoint")
    data = request.get_json()
    response_data = {}
    
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    resume_text = data.get('resume_text', '')
    suggestions = data.get('suggestions', '')

    if not resume_text or not suggestions:
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        latex_content = apply_improvements(resume_text, suggestions)
        response_data["raw_latex"] = latex_content
        logger.debug(f"LaTeX content generated successfully")
    except Exception as e:
        logger.error(f"Failed to generate LaTeX content: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
    return jsonify({'tex_content': latex_content})