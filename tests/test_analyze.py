
def test_analyze_job_no_data(client):
    # Test empty request with content-type header
    response = client.post('/analyze/job', 
                         headers={'Content-Type': 'application/json'})
    assert response.status_code == 400
    assert b'Bad Request' in response.data  # Check for HTML error page content

def test_analyze_job_no_description(client):
    response = client.post('/analyze/job', 
                         headers={'Content-Type': 'application/json'},
                         json={})
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == "No JSON data provided."