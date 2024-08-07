import google.generativeai as genai
 
def generate_response(question):
    prompts , greet  = get_prompts()
    genai.configure(api_key="AIzaSyA4wedlllm0xX9r7ERgbGQjQhM1Q3cIk6Y")

    if question.lower() in ["hello", "hi", "who are you"]:
        text = get_gemini_response(greet, question)
    else:
        text = get_gemini_response(prompts, question)
    return text

# function  to load google gemini model and takes prompt as input 
def get_prompts():
    with open('prompts.txt', 'r') as file:
        prompts = file.read().strip()
    with open('prompt_greeting.txt', 'r') as file_greet:
        greet = file_greet.read().strip()
    return prompts,greet

def get_gemini_response(question,prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt,question])
    return response.text
