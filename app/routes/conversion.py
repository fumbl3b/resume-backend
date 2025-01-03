import logging
from flask import Blueprint, jsonify, request

from app.services.error_service import generate_error
from app.services.latex_converter_2 import LatexConverter2


conversion_bp = Blueprint('conversion', __name__)
logger = logging.getLogger(__name__)

latex_converter = LatexConverter2()

@conversion_bp.route('/latex', methods=['POST'])
def convert_latex():
    logger.debug("Received request at /conversion/latex endpoint")
    data = request.get_json()

    if not data or 'latex_content' not in data:
        return generate_error(logger, "No LaTeX content provided")
    
    latex_content = data['latex_content']

    try:
        # convert to both formats
        tex_base64, pdf_base64 = latex_converter.compile_latex(latex_content)

        if not pdf_base64:
            return generate_error(
                logger,
                f"PDF generation failed \n tex_content: {tex_base64}"
            )

        return jsonify({
            "tex_content": tex_base64,
            "pdf_content": pdf_base64
        }), 200
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}")
        return generate_error(logger, f"{str(e)}"), 500