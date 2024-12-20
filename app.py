import os
import logging
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from openai import OpenAI
from version import __version__
from services.file_processor import FileProcessor
from services.latex_converter import LatexConverter
import base64

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
app.config['VERSION'] = __version__
CORS(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = app.logger
logger.setLevel(logging.DEBUG)

# Define default model
DEFAULT_MODEL = "gpt-4o"

# Add max file size config
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def extract_relevant_keywords(job_description: str, model=DEFAULT_MODEL) -> str:
    prompt = (
        "You are a professional career advisor. Extract the most important technical skills, intrapersonal sklls, "
        "and qualifications from the following job description. "
        "Return the results as a comma-separated list of only these keywords.  Do not include categories.\n\n"
        f"Job Description:\n{job_description}\n\n"
    )

    logger.debug("Sending request to OpenAI for keyword extraction...")
    response = client.chat.completions.create(model=model,
    messages=[{"role": "user", "content": prompt}],
    max_tokens=300,
    temperature=0.3)
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
    response = client.chat.completions.create(model=model,
    messages=[{"role": "user", "content": prompt}],
    max_tokens=300,
    temperature=0.3)
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
    response = client.chat.completions.create(model=model,
    messages=[{"role": "user", "content": prompt}],
    max_tokens=1000,
    temperature=0.3)
    result = response.choices[0].message.content.strip()
    logger.debug(f"Suggestions generated: {result}")
    return result

def generate_optimized_resume(resume_text: str, suggestions: str, model=DEFAULT_MODEL) -> str:
    messages = [
        {"role": "system", "content": "You are a LaTeX resume formatter. Respond only with valid LaTeX code. Do not include any other text or explanations."},
        {"role": "user", "content": (
            "Convert this resume into LaTeX format, incorporating the suggested improvements. "
            "Include all necessary LaTeX commands and structure. "
            "Return ONLY the LaTeX code with no additional text.\n\n"
            f"SUGGESTIONS:\n{suggestions}\n\n"
            f"RESUME:\n{resume_text}"
        )}
    ]

    logger.debug("Sending request to OpenAI for optimized resume generation...")
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=4000,
        temperature=0.1  # Lower temperature for more consistent output
    )
    return response.choices[0].message.content.strip()

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

    try:
        # Generate LaTeX content
        latex_content = generate_optimized_resume(resume_text, suggestions)
        
        # Convert and get both files
        tex_base64, pdf_base64 = LatexConverter.create_and_convert(latex_content)
        
        return jsonify({
            "tex_content": tex_base64,
            "pdf_content": pdf_base64
        })
    except Exception as e:
        logger.error(f"Error generating resume: {str(e)}")
        return jsonify({"error": "Error generating resume"}), 500

@app.route('/extract-resume-text', methods=['POST'])
def extract_resume_text():
    logger.debug("Received file upload request")
    
    # Check content type
    if not request.content_type or 'multipart/form-data' not in request.content_type:
        logger.error(f"Invalid content type: {request.content_type}")
        return jsonify({"error": "Invalid content type"}), 415

    if 'file' not in request.files:
        logger.error("No file in request")
        return jsonify({"error": "No file provided"}), 400
        
    file = request.files['file']
    if file.filename == '':
        logger.error("Empty filename")
        return jsonify({"error": "No file selected"}), 400
        
    logger.debug(f"Processing file: {file.filename}")
    
    # Validate file type
    allowed_extensions = {'pdf', 'doc', 'docx', 'tex'}
    if not file.filename.lower().endswith(tuple(f'.{ext}' for ext in allowed_extensions)):
        logger.error(f"Invalid file type: {file.filename}")
        return jsonify({"error": "Invalid file type"}), 415
        
    try:
        text = FileProcessor.extract_text(file.stream, file.filename)
        logger.debug(f"Successfully extracted text from {file.filename}")
        return jsonify({"text": text})
    except ValueError as e:
        logger.error(f"Value error processing file: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return jsonify({"error": "Error processing file"}), 500

@app.route('/convert-to-pdf', methods=['POST'])
def convert_to_pdf():
    logger.debug("Received LaTeX conversion request")
    
    data = request.get_json()
    if not data or 'tex_content' not in data:
        logger.error("No LaTeX content provided")
        return jsonify({"error": "No LaTeX content provided"}), 400
        
    try:
        pdf_path = LatexConverter.tex_to_pdf(data['tex_content'])
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='resume.pdf'
        )
    except Exception as e:
        logger.error(f"Error converting LaTeX to PDF: {str(e)}")
        return jsonify({"error": "Error converting to PDF"}), 500

@app.route('/version', methods=['GET'])
def get_version():
    return jsonify({
        "version": app.config['VERSION'],
        "status": "alpha",
        "api": "resume-backend"
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port)