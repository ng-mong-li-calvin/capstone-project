from google import genai
from google.genai import types
from pydantic import ValidationError

from app.models.schemas import EvaluationResponse

""" Implements a client for interacting with Google's Gemini API to evaluate student answers"""


class GeminiClient:
    """ Client for interacting with Google's Gemini API for evaluating student answers."""
    def __init__(self, api_key: str):
        """ Initialize the GeminiClient with an API key."""
        if not api_key:
            raise ValueError("An API key is required to initialize the client.")
        self._api_key = api_key
        self.client = genai.Client(api_key=self._api_key)

    def set_api_key(self, api_key: str):
        """ Set or update the API key for the GeminiClient."""
        if not api_key:
            raise ValueError("API key cannot be empty.")
        self._api_key = api_key
        self.client = genai.Client(api_key=self._api_key)

    def evaluate(self, question, model, student):
        """ Evaluate a student answer against the question and model answer."""
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