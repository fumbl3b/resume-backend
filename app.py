from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/suggestions', methods=['POST'])
def generate_suggestions():
    job_description = request.json.get('jobDescription')
    resume = request.files.get('resume')

    if not job_description or not resume:
        return jsonify({'error': 'Job description and resume are required'}), 400

    #TODO: Process the job description and resume to generate suggestions

    return jsonify({'message': 'Resume suggestions generated successfully.'}), 200


if __name__ == '__main__':
    app.run(port=5000, debug=True)