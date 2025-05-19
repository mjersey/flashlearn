import requests

# Set your Hugging Face API Key here
HF_API_KEY = "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"

# The Hugging Face API URL for the model you want to use
HF_API_URL = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"


# Function to make an API call to Hugging Face
def query_hugging_face(question, context):
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}"
    }

    data = {
        "inputs": {
            "question": question,
            "context": context
        }
    }

    response = requests.post(HF_API_URL, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()  # Returns the model's response (typically in the form of a dictionary)
    else:
        print(f"Error: {response.status_code}")
        return None


# Example function to create flashcards from the response
def create_flashcards_from_text(question, context):
    response_data = query_hugging_face(question, context)

    if response_data:
        # Extract the answer from the response
        answer = response_data[0]['answer']

        print(f"Flashcard Question: {question}")
        print(f"Flashcard Answer: {answer}")
        # You can then use these details to create a flashcard in your UI or system
    else:
        print("No data returned. Please check the API response.")


# Example usage
context = """
The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France. 
It was designed by the engineer Gustave Eiffel and was completed in 1889.
"""
question = "Who designed the Eiffel Tower?"

create_flashcards_from_text(question, context)
