import logging
from flask import Blueprint, jsonify, request
from app.config import DEFAULT_MODEL
from app.services.error_service import generate_error
from app.extensions import client
from app.res.prompt_stubs import gen_benefits, gen_keywords

analysis_bp = Blueprint('analysis', __name__)
logger = logging.getLogger(__name__)

def analyze_job_description(job_description, model=DEFAULT_MODEL):
    result = {}
    # TODO check redundancies between keywords/benefits
    logger.debug("Sending request to OpenAI for keyword extraction...")
    response = client.chat.completions.create(model=model,
    messages=[{"role": "user", "content": gen_keywords(job_description)}],
    max_tokens=300,
    temperature=0.3)
    result['keywords'] = response.choices[0].message.content.strip()
    logger.debug(f"Keywords extracted: { result['keywords'] }")
    logger.debug("Sending request to OpenAI for benefit extraction...")
    response = client.chat.completions.create(model=model,
    messages=[{"role": "user", "content": gen_benefits(job_description)}],
    max_tokens=300,
    temperature=0.3)
    result['benefits'] = response.choices[0].message.content.strip()
    logger.debug(f"Benefits Extracted: {result}")

    return result

@analysis_bp.route('/job', methods=['POST'])
def api_analyze_job():
    logger.debug("Received request at /job endpoint")
    data = request.get_json()
    if not data:
        return generate_error(logger, "No JSON data provided.")
    
    job_description = data.get('job_description', '')
    if not job_description:
        return generate_error(logger, "No job description provided.")
    logger.debug(f"Job description: {job_description}")

    analysis = analyze_job_description(job_description)
    
    return jsonify({ "keywords": analysis['keywords'], "benefits": analysis['benefits'] })