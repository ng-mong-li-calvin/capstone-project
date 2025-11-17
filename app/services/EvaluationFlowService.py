from app.repositories.model_qna_repository import model_qna_repository
from app.repositories.student_answers_repository import student_answers_repository
from app.services.evaluation_service import evaluate_all_students, evaluate_all_evaluations
from app.services.folder_write_service import write_json

""" Implements the evaluation flow service to manage the end-to-end process of"""


class EvaluationFlowService:
    """ Service to manage the flow of evaluation from data retrieval to export."""
    def __init__(self):
        self.modelqna = None
        self.studentanswers = None
        self.evaluation = []

    def retrieve_data(self, path) -> None:
        """ Retrieve model Q&A and student answers from the specified path."""
        self.modelqna = model_qna_repository(path)
        self.studentanswers = student_answers_repository(path)

    def evaluate_data(self, client) -> list:
        """ Evaluate student answers against model answers using the provided client."""
        self.evaluation = evaluate_all_students(
            client,
            self.modelqna,
            self.studentanswers
        )
        return self.evaluation

    def evaluate_evaluations(self, client) -> list:
        """ Re-evaluate the previous evaluations for consistency or further analysis."""
        self.evaluation = evaluate_all_evaluations(client, self.evaluation)
        return self.evaluation

    def export_data(self, name=None, path=None) -> None:
        """ Export the evaluation results to a JSON file."""
        args = {}
        if name:
            args['name'] = name
        if path:
            args['save_path'] = path
        write_json(self.evaluation, **args)



