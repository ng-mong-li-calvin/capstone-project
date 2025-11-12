from openai import OpenAI
from pydantic import ValidationError

from app.core.schemas import EvaluationResponse


class OpenAPIClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("An API key is required to initialize the client.")
        self._api_key = api_key
        self.client = OpenAI(api_key=self._api_key)

    def set_api_key(self, api_key: str):
        if not api_key:
            raise ValueError("API key cannot be empty.")
        self._api_key = api_key
        self.client = OpenAI(api_key=self._api_key)

    def evaluate(self, question, model, student):
        prompt = f"""
            Based on the question and model answer, grade the student answer as binary 'Pass/Fail' and give a simple explanation no more than 20 words.

            Question: {question}

            Model answer: {model}

            Student answer: {student}
            """

        response = self.client.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert exam grader."},
                {"role": "user", "content": prompt}
            ],
            response_format=EvaluationResponse,
            temperature=0.0,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

        # Safely get the model output content
        try:
            content = response.choices[0].message.content
        except Exception:
            content = ""

        try:
            evaluation_response = EvaluationResponse.model_validate_json(content)
            return evaluation_response
        except ValidationError as e:
            raise ValueError(f"Failed to parse evaluation response: {e}")
        except Exception as e:
            raise ValueError(f"An unexpected error occurred while parsing the response: {e}")