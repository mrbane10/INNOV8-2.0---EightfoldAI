prompt_for_resume_summary = """
You are an experienced Human Resources (HR) professional. Your task is to summarize the following Resume into the specified categories by providing simple descriptions for each label.

Categories to summarize:
1. Resume Summary: Provide a brief overview of the candidate's experience and skills.
2. Objective: Describe the candidate's career goals and the type of role they are seeking.
3. Experience: List the candidate's work experience, including job titles, companies, and key responsibilities.
4. Accomplishments: Highlight any notable achievements or awards the candidate has received.
5. Education: Include the candidate's educational background, such as degrees and institutions attended.
6. Projects: Mention any significant projects the candidate has worked on, including technologies used and outcomes.
7. Skills: List the candidate's technical skills and proficiencies.

Below is an example of how to format the summary:

---

Example:

1. Resume Summary: John Doe is a software engineer with 6 years of experience specializing in full-stack development, with strong expertise in JavaScript, React, and Node.js. He has worked at Google and Microsoft, delivering scalable web applications.

2. Objective: Seeking a senior software engineering role to lead development teams and build scalable web applications.

3. Experience: John has worked at Google from 2020 to present as a Senior Software Engineer, leading web application development using React and Node.js. Previously, he was a Software Engineer at Microsoft from 2016 to 2020, focusing on cloud services with Azure and Python.

4. Accomplishments: Increased website performance at Google by 35 percent. Received the Employee of the Year award at Microsoft in 2018.

5. Education: Bachelor of Science in Computer Science from MIT, graduated in 2015.

6. Projects: Developed an e-commerce platform using React and AWS in 2021. Created a real-time chat application using Node.js and WebSocket in 2020.

7. Skills: Proficient in React, Node.js, Python, AWS, Azure, and JavaScript.

---

Now, please apply this format to the following resume. For any category that doesn't have enough details, respond with "None."

Resume:  
{resume_text}
"""

prompt_for_grading_recommendation_letter = """
You are an expert HR professional with years of experience in evaluating resumes and recommendation letters. Analyze the **resume summary** of the candidate, **recommendation letter**, and **resume summary of the recommender** to assess how well the letter supports the candidate. Score the **recommendation letter** out of 10 based on the following key factors:

### Key Factors:
1. **Alignment**: How well does the recommendation letter match the candidate’s skills, qualifications, and career goals from the resume summary?
2. **Support**: Does the letter provide specific examples and strong endorsements for the candidate?
3. **Technical Relevance**: Does the letter use relevant technical terms that match the candidate's field, avoiding vague praise?
4. **Recommender Credibility**: Based on the recommender's resume, how credible is their endorsement of the candidate?

### Scoring Guidelines:
- **0-3**: Weak alignment, vague support, low technical relevance, or low credibility.
- **4-6**: Moderate alignment and support, some technical relevance, and moderate credibility.
- **7-10**: Strong alignment, strong support with technical terms, high credibility.

Provide only a number between **0 and 10** as the final score.

---

**Resume Summary of the Candidate**:  
{resume_candidate}

**Recommendation Letter**:  
{recommendation_letter}

**Resume Summary of the Recommender**:  
{resume_recommender}
"""

prompt_for_resume_score_based_on_recommendation = """
You are an expert HR professional with years of experience in evaluating resumes and recommendation letters. Analyze the provided **experience** of the candidate and the **recommendation letters** to assess how well the **resume** is supported by the letters. Assume the letters are genuine and accurate. Your task is to score the **resume** out of 10 based on its alignment with the recommendation letters and to penalize exaggerated wording in either the **resume** or the **recommendation letters**. This score will help evaluate the resume’s strength and check for potential inconsistencies, exaggerations, or unsupported claims.

### Key Factors:
1. **Relevance**: Do the candidate's skills, qualifications, and experiences in the **resume** align with what is endorsed in the **recommendation letters**?
2. **Compatibility**: Do the candidate’s career objectives and roles in the **resume** match the traits and skills emphasized in the **recommendation letters**?
3. **Consistency**: Are there any inconsistencies between the **resume** and the **recommendation letters**? Inconsistencies may indicate exaggerations or misrepresentation.
4. **Exaggeration**: Are there exaggerated or overly vague claims in either the **resume** or **recommendation letters** (e.g., “incredible skills,” “unparalleled success”)? Exaggerations should be penalized, lowering the score.

### Scoring Guidelines:
- **0**: Poor support from the letters, with little to no alignment, more than 3 inconsistencies, and/or excessive exaggeration.
- **1-3**: Weak alignment with limited support and up to 3 inconsistencies or exaggerated claims.
- **4-6**: Moderate alignment with some support, but up to 2 minor discrepancies or slight exaggerations.
- **7-9**: Strong support, with high alignment and at most 1 minor discrepancy or minimal exaggeration.
- **10**: Perfect alignment, with complete support, no inconsistencies, and no exaggerated claims.

### Important Considerations:
- Focus on how well the letters reflect and reinforce the key points in the resume.
- Penalize exaggerated or vague language in either the **resume** or **recommendation letters**.
- Any inconsistencies between the **resume** and **recommendation letters** should lower the score.
  
Provide ONLY and ONLY a number between **0 and 10** as the final answer. DONOT provide addiiotnal information or explanation for your answer/decision.

---

**Resume of the Candidate**:  
{resume_candidate}

**Recommendation Letters**:  
{recommendation_letters}

"""

prompt_for_suspicious_wording = """
You are an expert HR professional skilled in detecting inconsistencies in resumes. Your task is to analyze the provided **resume summary** for suspicious wording or implausible claims, such as unrealistic career progression, inflated job titles, or improbable achievements.

### Key Factors:
1. **Unrealistic Job Titles**: Does the candidate claim to hold a high position (e.g., CEO) at a young age or early in their career without reasonable progression?
2. **Improbable Career Progression**: Is the candidate’s career progression unusually fast for their industry or experience level?
3. **Exaggerated Achievements**: Are the candidate’s achievements exaggerated or improbable given their experience?
4. **Vague Descriptions**: Does the resume use vague or non-specific language to describe accomplishments that seem exaggerated?

### Scoring Guidelines:
- **0**: More than 3 suspicious claims or exaggerated achievements.
- **1-3**: Up to 3 suspicious elements that don’t align with the candidate’s likely experience.
- **4-6**: Some questionable claims (up to 2), but nothing severe.
- **7-9**: Mostly credible, with only minor details (at most 1) that might raise slight suspicion.
- **10**: Entirely credible, with no suspicious claims or unrealistic career progression.

### Example:

**Resume Summary**:  
John Doe is a 24-year-old CEO of a rapidly growing tech company. After completing his bachelor's degree at age 21, he became CTO of a software company, leading a team of 50 engineers. In two years, he was promoted to CEO, managing over 200 staff and several multi-million-dollar projects.

**Score**: 2

Now, apply the same analysis to the following resume summary. Provide **only a number between 0 and 10** indicating the score.

**Resume Summary**:  
{resume_text}

"""

prompt_for_extracting_company_data = """
You are an expert in extracting structured data from resume summaries. Your task is to carefully analyze the provided **resume summary** of the candidate and return a structured list of dictionaries containing information about the companies the candidate has worked with, including the start and end years of employment.

### Instructions:
1. Extract the **company names** that the candidate has worked with from the resume summary.
2. For each company, extract the **start year** of employment.
3. If available, extract the **end year** of employment. If the candidate is currently employed at the company or if the end year is not mentioned, return an empty string for the **end_year**.
4. Return the information in the form of a list of dictionaries where each dictionary has the following keys:
   - `company`: The name of the company. if the company name is not mentioned for a role, use "Unknown Company".
   - `start_year`: The year the candidate started working at the company.
   - `end_year`: The year the candidate stopped working at the company, or an empty string if it is an ongoing role.

### Format of the Output:
The output should ONLY be a Python-style list of dictionaries, like this:
```python
[
  {"company": "Company A", "start_year": "2018", "end_year": "2021"},
  {"company": "Company B", "start_year": "2021", "end_year": ""}
]
```

### Resume Summary:
{resume_text}
"""

prompt_for_extracting_company_data = """
You are an expert in extracting structured data from resume summaries. Your task is to carefully analyze the provided **resume summary** of the candidate and return a structured list of dictionaries containing information about the companies the candidate has worked with, including the start and end years of employment.

### Instructions:
1. Extract the **company names** that the candidate has worked with from the resume summary.
2. For each company, extract the **start year** of employment.
3. If available, extract the **end year** of employment. If the candidate is currently employed at the company or if the end year is not mentioned, return an empty string for the **end_year**.
4. Return the information in the form of a list of dictionaries where each dictionary has the following keys:
   - `company`: The name of the company. If the company name is not mentioned or vague term like "Company name" is used, use "Unknown Company".
   - `start_year`: The year the candidate started working at the company.
   - `end_year`: The year the candidate stopped working at the company, or an empty string if it is an ongoing role.
### Resume Summary:
{resume_summary}

The output should ONLY contain the list of dictionaries with the keys mentioned above. Donot provide any other information.
"""