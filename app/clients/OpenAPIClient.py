from openai import OpenAI
from pydantic import ValidationError
import app.config.prompts as p
from app.models.schemas import EvaluationResponse

""" Implements a client for interacting with OpenAI's API to evaluate student answers
    against model answers using predefined prompts and configurations.
"""


# Predefined model configurations
MODEL_CONFIG = {
    'gpt-4o': {
        'model': "gpt-4o",
        'response_format': EvaluationResponse,
        'temperature': 0.0,
        'max_tokens': 150,
        'top_p': 1,
        'frequency_penalty': 0,
        'presence_penalty': 0,
        'system_prompt': [p.SYSTEM_PROMPT_EXAM_GRADER],
        'prompt_template': p.PROMPT_4o_TEMPLATE,
    },
    'gpt-4o-mini': {
        'model': "gpt-4o-mini",
        'response_format': EvaluationResponse,
        'temperature': 0.0,
        'max_tokens': 150,
        'top_p': 1,
        'frequency_penalty': 0,
        'presence_penalty': 0,
        'system_prompt': [p.SYSTEM_PROMPT_EXAM_GRADER],
        'prompt_template': p.PROMPT_4o_mini_TEMPLATE,
    },
    'gpt-3.5-turbo': {
        'model': "gpt-3.5-turbo",
        'response_format': { "type": "json_object" },
        'temperature': 0.0,
        'max_tokens': 150,
        'top_p': 1,
        'frequency_penalty': 0,
        'presence_penalty': 0,
        'system_prompt': [p.SYSTEM_PROMPT_EXAM_GRADER, p.SYSTEM_PROMPT_JSON],
        'prompt_template': p.PROMPT_35_turbo_TEMPLATE,
    }
}


class OpenAPIClient:
    """
    Client for interacting with OpenAI's API for evaluating student answers.
    Uses predefined model configurations and prompts.
    """
    def __init__(self, model, api_key: str):
        """ Initialize the OpenAPIClient with a specific model and API key."""
        if not api_key:
            raise ValueError("An API key is required to initialize the client.")
        self.config = MODEL_CONFIG.get(model)
        self._client = OpenAI(api_key=api_key)

    def set_api_key(self, api_key: str):
        """ Set or update the API key for the OpenAI client. """
        if not api_key:
            raise ValueError("API key cannot be empty.")
        self._client = OpenAI(api_key=api_key)

    def set_model(self, model):
        """ Set or update the model configuration for the client. """
        if model not in MODEL_CONFIG:
            raise ValueError(f"Model '{model}' is not supported.")
        self.config = MODEL_CONFIG.get(model)

    def get_model(self):
        """ Get the current model name. """
        return self.config.get('model')

    def get_config(self):
        """ Get the current configuration dictionary. """
        return self.config

    def evaluate(self, question, model, student) -> EvaluationResponse:
        """
        Evaluate a student's answer against the model answer for a given question.
        Args:
            question (str): The question text.
            model (str): The model answer text.
            student (str): The student's answer text.
        Returns:
            EvaluationResponse: The evaluation result containing grade and explanation.
        """
        messages = []
        for sys_message in self.config.get('system_prompt', []):
            messages.append({"role": "system", "content": sys_message})
        user_prompt = self.config.get('prompt_template').format(
            question=question, model=model, student=student)
        messages.append({"role": "user", "content": user_prompt})

        call_kwargs = {k: v for k, v in self.config.items()
                       if (k != 'system_prompt') and (k != 'prompt_template')}

        response = self._client.chat.completions.parse(
            messages=messages,
            **call_kwargs,
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

    def evaluation_review(self, question, model, student, evaluation) -> str:
        """
        Review a previous evaluation of a student's answer.
        Args:
            question (str): The question text.
            model (str): The model answer text.
            student (str): The student's answer text.
            evaluation (dict): The previous evaluation containing 'grade' and 'explanation'.
        Returns:
            str: The review response from the model.
        """
        grade = evaluation.get('grade', '')
        explanation = evaluation.get('explanation', '')
        review_prompt = f"""
            The student answer was graded as '{grade}' with the explanation: {explanation}.
            Review this evaluation based on the question, model answer, and student answer provided below.

            Question: {question}

            Model answer: {model}

            Student answer: {student}

            Is the evaluation accurate? Provide a brief justification.
        """

        messages = []
        for sys_message in self.config.get('system_prompt', []):
            messages.append({"role": "system", "content": sys_message})
        messages.append({"role": "user", "content": review_prompt})

        call_kwargs = {k: v for k, v in self.config.items()
                       if (k != 'system_prompt')
                       and (k != 'prompt_template')
                       and (k != 'response_format')}

        response = self._client.chat.completions.parse(
            messages=messages,
            **call_kwargs,
        )

        try:
            content = response.choices[0].message.content
        except Exception:
            content = ""

        return content