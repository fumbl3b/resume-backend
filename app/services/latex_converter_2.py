import os
import tempfile
import subprocess
import logging
import base64
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class LatexConverter2:
    def __init__(self):
        self.temp_dir = None
        self.validate_latex_installation()
    
    @staticmethod
    def validate_latex_installation() -> None:
        """Check if pdflatex is installed and accessible"""
        try:
            subprocess.run(['pdflatex', '--version'], 
                         capture_output=True, 
                         check=True)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            raise RuntimeError("pdflatex not found. Please install TeX Live.") from e

    def compile_latex(self, content: str) -> Tuple[str, Optional[str]]:
        """Compile LaTeX content to PDF and return both as base64"""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.temp_dir = temp_dir
            tex_path = os.path.join(temp_dir, 'resume.tex')
            pdf_path = os.path.join(temp_dir, 'resume.pdf')
            
            # Write content to file
            with open(tex_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            try:
                # Run pdflatex twice for references
                for _ in range(2):
                    result = subprocess.run(
                        ['pdflatex', '-interaction=nonstopmode', tex_path],
                        cwd=temp_dir,
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    logger.debug(f"LaTeX compilation output:\n{result.stdout}")
                
                # Read results
                with open(tex_path, 'rb') as tf:
                    tex_content = base64.b64encode(tf.read()).decode('utf-8')
                
                if os.path.exists(pdf_path):
                    with open(pdf_path, 'rb') as pf:
                        pdf_content = base64.b64encode(pf.read()).decode('utf-8')
                    return tex_content, pdf_content
                else:
                    raise FileNotFoundError("PDF file not generated")
                    
            except subprocess.CalledProcessError as e:
                logger.error(f"LaTeX Error: {e.stdout}\n{e.stderr}")
                return tex_content, None