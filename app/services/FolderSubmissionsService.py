from app.repositories.ModelQnARepository import ModelQnARepository
from app.repositories.StudentAnswersRepository import StudentAnswersRepository
from app.services.EvaluationService import EvaluationService


class FolderSubmissionsService:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.model = ModelQnARepository(self.folder_path).get_model_qna()
        self.students = StudentAnswersRepository(self.folder_path).get_student_answers()

    def evaluate_submissions(self, client):
        evaluation_service = EvaluationService(client)
        evaluation_results = evaluation_service.evaluate(self.model, self.students)
        with open(self.folder_path + '/evaluation_results.json', 'w') as f:
            f.write(evaluation_results)