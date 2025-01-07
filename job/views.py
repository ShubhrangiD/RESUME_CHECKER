import json
import requests
import pdfplumber
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm

# API URL for the local model
url = "http://localhost:11434/api/generate"

# Headers for the API request
headers = {
    'Content-Type': 'application/json',
}

# To maintain the conversation history
conversation_history = []
job_description_text = ""
resumes_text = []

def extract_text_from_pdf(file):
    """Extracts text from a PDF file using pdfplumber."""
    text = ""
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print("Error extracting text from PDF:", e)
        return ""
    return text

def process_job_description(file):
    """Processes job description from a file, either PDF or text."""
    global job_description_text
    if file.name.endswith('.pdf'):
        job_description_text = extract_text_from_pdf(file)
    else:
        try:
            job_description_text = file.read().decode('utf-8')
        except UnicodeDecodeError:
            job_description_text = file.read().decode('ISO-8859-1')
    return "Job description uploaded successfully!"

def process_resumes(files):
    """Processes resumes from given files."""
    global resumes_text
    resumes_text = []
    for file in files:
        if file.name.endswith('.pdf'):
            resumes_text.append(extract_text_from_pdf(file))
        else:
            try:
                resumes_text.append(file.read().decode('utf-8'))
            except UnicodeDecodeError:
                resumes_text.append(file.read().decode('ISO-8859-1'))
    return f"{len(resumes_text)} resumes uploaded successfully!"

def generate_response(prompt, job_desc_file, resumes_files):
    """Generates a response based on the provided prompt, job description, and resumes."""
    global job_description_text, resumes_text

    if job_desc_file:
        process_job_description(job_desc_file)
    if resumes_files:
        process_resumes(resumes_files)

    conversation_history.append(f"Question: {prompt}")

    full_prompt = (
        f"Job Description:\n{job_description_text}\n\n"
        f"Resumes:\n" + "\n".join(resumes_text) +
        f"\n\nConversation:\n" + "\n".join(conversation_history)
    )

    data = {
        "model": "llama3.2",
        "stream": False,
        "prompt": full_prompt,
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            response_text = response.json()
            actual_response = response_text.get("response", "No response found.")
            conversation_history.append(f"Response: {actual_response}")
            return actual_response
        else:
            error_message = f"Error: {response.status_code}, {response.text}"
            print(error_message)
            return "Error: Unable to get response from the model."
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        return "Request failed. Please check the server and try again."

@login_required
def job_query_view(request):
    """Handles the job query view logic."""
    response = None  # Default to None if there's no response yet

    if request.method == 'POST':
        prompt = request.POST.get('prompt')
        job_desc_file = request.FILES.get('job_desc_file')
        resumes_files = request.FILES.getlist('resumes_files')

        response = generate_response(prompt, job_desc_file, resumes_files)

    # Render the job query page with the response in context
    return render(request, 'job/job_query.html', {'response': response})

def home(request):
    """Renders the home page."""
    return render(request, 'job/home.html')

def login_view(request):
    """Handles login logic."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('job_query')  # Redirect to job_query page after login
        else:
            return render(request, 'job/login.html', {'error': 'Invalid credentials'})
    return render(request, 'job/login.html')


def logout_view(request):
    """Handles user logout."""
    logout(request)
    return redirect('login')  # Redirect to login page after logout

def register_view(request):
    """Handles user registration."""
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    return render(request, 'job/register.html', {'form': form})
