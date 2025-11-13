from google import genai
from google.genai import types
from pydantic import ValidationError

from app.models.schemas import EvaluationResponse


class GeminiClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("An API key is required to initialize the client.")
        self._api_key = api_key
        self.client = genai.Client(api_key=self._api_key)

    def set_api_key(self, api_key: str):
        if not api_key:
            raise ValueError("API key cannot be empty.")
        self._api_key = api_key
        self.client = genai.Client(api_key=self._api_key)

    def evaluate(self, question, model, student):
        prompt = f"""
            Based on the question and model answer, grade the student answer as binary 'Pass/Fail' and give a simple explanation no more than 20 words.

            Question: {question}

            Model answer: {model}

            Student answer: {student}
            """

        config = types.GenerateContentConfig(
            system_instruction="You are an expert exam grader.",
            temperature=0.0,
            max_output_tokens=150
        )

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config
        )

        # Safely get the model output content
        try:
            content = response.text
        except Exception:
            content = ""

        try:
            evaluation_response = EvaluationResponse.model_validate(content)
            return evaluation_response
        except ValidationError as e:
            raise ValueError(f"Failed to parse evaluation response: {e}")
        except Exception as e:
            raise ValueError(f"An unexpected error occurred while parsing the response: {e}")