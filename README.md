# Resume Optimization Backend

This project provides a Flask-based backend service that uses the OpenAI API to:
1. Extract relevant keywords from a job description.
2. Suggest improvements to a candidate's resume to better align with the job description.
3. Generate an optimized LaTeX-formatted resume incorporating suggested improvements.

## Features

- **Extract Relevant Keywords:** Given a job description, the service returns the most critical keywords, skills, and qualifications.
- **Suggest Resume Improvements:** Suggests how to improve and tailor a resume to match a specific job description.
- **Generate Optimized Resume:** Produces an updated LaTeX resume with the suggested improvements incorporated.

## Prerequisites

- Python 3.8+  
- An OpenAI API key

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/fumbl3b/resume-backend.git
   cd resume-backend

2. **Create and Activate a Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    *(On Windows: venv\Scripts\activate)*
3. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up Environmental Variables:**
    Create an *.env* file in the project root:
    ```bash
    echo "OPENAI_API_KEY=**********" > .env
    ```
    Replace * with your personal key.

## Usage

1. **Run the Flask Server Locally:**
    ```bash
    flask run
    ```
    By default, this will run the server at http://127.0.0.1:5000.

2. **Endpoints:**
    - POST /extract-keywords
    
    *Request Body:*
    ```json
    {
        "job_description": "Your job description here"
    }
    ```

    - POST /suggest-improvements

    *Request Body:*

    ```json
    {
        "resume_text": "Raw resume text here",
        "job_description": "Job description here"
    }
    ```

    - POST /generate-optimized-resume

    *Request Body:*
    ```json
    {
        "resume_text": "Raw resume text here",
        "suggestions": "Suggestions from the improvements step"
    }
    ```


    
