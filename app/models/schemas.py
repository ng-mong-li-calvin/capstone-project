from pydantic import BaseModel, Field

""" Pydantic schema for the evaluation response from the OpenAI API. """


class EvaluationResponse(BaseModel):
    grade: str = Field(..., description="The evaluation result, either 'Pass' or 'Fail'.")
    explanation: str = Field(..., description="A brief explanation for the evaluation result, no more than 20 words.")