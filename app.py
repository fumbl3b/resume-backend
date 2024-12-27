import os
import sys
import logging
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from openai import OpenAI
from version import __version__
from services.file_processor import FileProcessor
from services.latex_converter_2 import LatexConverter2

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://resume-updater-flax.vercel.app",
            "http://localhost:3000"  # For local development
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

app.config['VERSION'] = __version__

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = app.logger
logger.setLevel(logging.DEBUG)

DEFAULT_MODEL = "gpt-4o"

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize converter
latex_converter = LatexConverter2()

def generate_error(message, code=400):
    logger.debug(message)
    return jsonify({ "error": message }), code

def analyze_job_description(job_description, model=DEFAULT_MODEL):
    result = {}
    prompt_keywords = (
        "You are a professional career advisor. Extract the most important technical skills, intrapersonal sklls, "
        "and qualifications from the following job description. "
        "Return the results as a comma-separated list of only these keywords.  Do not include categories.\n\n"
        f"Job Description:\n{job_description}\n\n"
    )
    logger.debug("Sending request to OpenAI for keyword extraction...")
    response = client.chat.completions.create(model=model,
    messages=[{"role": "user", "content": prompt_keywords}],
    max_tokens=300,
    temperature=0.3)
    result['keywords'] = response.choices[0].message.content.strip()
    logger.debug(f"Keywords extracted: { result['keywords'] }")

    prompt_benefits = (
        "You are a professional career advisor.  Extract all the benefits listed for the following job description."
        "If compensation range is listed, please return that first.  Return all the results as a comma-separated list.\n\n"
        f"Job Description:\n{job_description}\n\n"
    )
    logger.debug("Sending request to OpenAI for benefit extraction...")
    response = client.chat.completions.create(model=model,
    messages=[{"role": "user", "content": prompt_benefits}],
    max_tokens=300,
    temperature=0.3)
    result['benefits'] = response.choices[0].message.content.strip()
    logger.debug(f"Benefits Extracted: {result}")

    return result

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

def optimize_resume(resume_text, suggestions, model=DEFAULT_MODEL):
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

@app.route('/version', methods=['POST'])
def get_version():
    return jsonify({
        "version": app.config['VERSION'],
        "status": "alpha",
        "api": "resume-backend"
    })

@app.route('/analyze-job', methods=['POST'])
def api_analyze_job():
    logger.debug("Received request at /analyze-job-description endpoint")
    data = request.get_json()
    if not data:
        return generate_error("No JSON data provided.")
    
    job_description = data.get('job_description', '')
    if not job_description:
        return generate_error("No job description provided.")
    logger.debug(f"Job description: {job_description}")

    analysis = analyze_job_description(job_description)
    
    return jsonify({ "keywords": analysis['keywords'], "benefits": analysis['benefits'] })


@app.route('/suggest-improvements', methods=['POST'])
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

@app.route('/extract-resume-text', methods=['POST'])
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

@app.route('/optimize-resume', methods=['POST'])
def api_generate_optimized_resume():
    logger.debug("Received request at /generate-optimized-resume endpoint")

    data = request.get_json()
    response_data = {}
    
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    resume_text = data.get('resume_text', '')
    suggestions = data.get('suggestions', '')

    if not resume_text or not suggestions:
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        latex_content = optimize_resume(resume_text, suggestions)
        response_data["raw_latex"] = latex_content
        logger.debug(f"LaTeX content generated successfully")
    except Exception as e:
        logger.error(f"Failed to generate LaTeX content: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
    return jsonify({'tex_content': latex_content})

    #TODO: implement parsing here
    # Step 2: Try PDF Conversion
    # try:
    #     tex_base64, pdf_base64 = LatexConverter.create_and_convert(latex_content)
    #     response_data.update({
    #         "tex_content": tex_base64,
    #         "pdf_content": pdf_base64
    #     })
    #     return jsonify(response_data), 200
    # except Exception as e:
    #     logger.error(f"PDF conversion failed: {str(e)}")
    #     response_data["error"] = f"PDF generation failed: {str(e)}"
    #     return jsonify(response_data), 206


@app.route('/convert-to-pdf', methods=['POST'])
def convert_to_pdf():
    # TODO: fix this
    pass

@app.route('/convert-latex', methods=['POST'])
def convert_latex():
    logger.debug("Received request at /convert-latex endpoint")
    data = request.get_json()
    
    if not data or 'latex_content' not in data:
        return jsonify({"error": "No LaTeX content provided"}), 400
        
    latex_content = data['latex_content']
    
    try:
        # Convert content to both formats
        tex_base64, pdf_base64 = latex_converter.compile_latex(latex_content)
        
        if not pdf_base64:
            return jsonify({
                "error": "PDF generation failed",
                "tex_content": tex_base64
            }), 206
            
        return jsonify({
            "tex_content": tex_base64,
            "pdf_content": pdf_base64
        }), 200
        
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port)