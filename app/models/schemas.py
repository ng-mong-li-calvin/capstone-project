from pydantic import BaseModel, Field


class EvaluationResponse(BaseModel):
    grade: str = Field(..., description="The evaluation result, either 'Pass' or 'Fail'.")
    explanation: str = Field(..., description="A brief explanation for the evaluation result, no more than 20 words.")