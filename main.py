import os

from app.repositories.ModelQnARepository import ModelQnARepository
from app.repositories.StudentAnswersRepository import StudentAnswersRepository
from app.repositories.OpenAPIClient import OpenAPIClient
from app.services.EvaluationService import EvaluationService


def main():
    rugby_model = ModelQnARepository('Rugby Football Club').get_model_qna()
    rugby_students = StudentAnswersRepository('Rugby Football Club').get_student_answers()
    client = OpenAPIClient(api_key=os.getenv('OPENAI_API_KEY'))
    evaluation_service = EvaluationService(client)
    evaluation_results = evaluation_service.evaluate(rugby_model, rugby_students)
    with open('data/Rugby Football Club/evaluation_results.json', 'w') as f:
        f.write(evaluation_results)


if __name__ == "__main__":
    main()