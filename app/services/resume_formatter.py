class ResumeFormatter:
    @staticmethod
    def format_resume(resume_text: str, suggestions: str) -> str:
        # Simple text formatting until LaTeX conversion is stable
        formatted_text = (
            f"RESUME\n"
            f"======\n\n"
            f"{resume_text}\n\n"
            f"IMPROVEMENTS APPLIED\n"
            f"===================\n\n"
            f"{suggestions}"
        )
        return formatted_text