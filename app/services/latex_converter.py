import os
import tempfile
import subprocess
import logging
import base64

logger = logging.getLogger(__name__)

class LatexConverter:
    @staticmethod
    def validate_latex(content: str) -> bool:
        required_elements = [
            r'\documentclass',
            r'\begin{document}',
            r'\end{document}'
        ]
        return all(element in content for element in required_elements)

    @staticmethod
    def create_and_convert(latex_content: str) -> tuple[str, str]:
        logger.debug("Starting LaTeX conversion...")
        logger.debug(f"Raw LaTeX content:\n{latex_content}")
        
        if not LatexConverter.validate_latex(latex_content):
            raise ValueError("Invalid LaTeX structure: Missing required elements")

        with tempfile.TemporaryDirectory() as temp_dir:
            tex_file = os.path.join(temp_dir, 'resume.tex')
            with open(tex_file, 'w') as f:
                f.write(latex_content)
            
            try:
                process = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', '-file-line-error', tex_file],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                log_file = os.path.join(temp_dir, 'resume.log')
                if os.path.exists(log_file):
                    with open(log_file, 'r') as f:
                        log_content = f.read()
                        logger.debug(f"LaTeX compilation log:\n{log_content}")
                
                pdf_file = os.path.join(temp_dir, 'resume.pdf')
                if not os.path.exists(pdf_file):
                    raise Exception(f"PDF generation failed. LaTeX output:\n{process.stdout}\n{process.stderr}")
                
                with open(tex_file, 'rb') as tf, open(pdf_file, 'rb') as pf:
                    tex_base64 = base64.b64encode(tf.read()).decode('utf-8')
                    pdf_base64 = base64.b64encode(pf.read()).decode('utf-8')
                
                return tex_base64, pdf_base64
                
            except subprocess.CalledProcessError as e:
                error_output = f"STDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
                logger.error(f"LaTeX compilation failed:\n{error_output}")
                raise Exception(f"LaTeX compilation error: {error_output}")