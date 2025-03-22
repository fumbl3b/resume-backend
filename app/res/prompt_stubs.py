# TODO: flesh out

def gen_keywords(job_description):
    keywords = f"""
    You are a professional career advisor.  Extract the most important technical skills, intrapersonal skills, and
    qualifications from the following job description.  Return the results as a comma-separated list of only these keywords.  
    Do not include categories.\n\n
    Job Description:\n{job_description}\n
    """
    return keywords

def gen_benefits(job_description):
    benefits = f"""
    You are a professional career advisor.  Extract all the benefits listed for the following job description.  If 
    compensation range is listed, please return that first.  Return all the results as a comma-separated list.\n\n
    Job Description: {job_description}
    """
    return benefits