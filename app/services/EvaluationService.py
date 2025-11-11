import json
from dotenv import load_dotenv
from app.core.schemas import EvaluationResponse


load_dotenv()


class EvaluationService:

    def __init__(self, client):
        self.client = client

    def evaluate(self, model_qna, student_answers) -> str:
        model_qna = json.loads(model_qna)
        student_answers = json.loads(student_answers)
        results = []
        for student, answers in student_answers.items():
            student_result = {
                "student": student,
                "evaluations": []
            }
            for answer in answers:
                question_id = answer['question_id']
                student_answer = answer['student_answer']
                # Find the corresponding model answer
                model_answer_entry = next((item for item in model_qna if item["question_id"] == question_id), None)
                if model_answer_entry:
                    question_text = model_answer_entry['question_text']
                    model_answer = model_answer_entry['answer_text']
                    evaluation_response: EvaluationResponse = self.client.evaluate(
                        question_text,
                        model_answer,
                        student_answer
                    )
                    student_result["evaluations"].append({
                        "question_id": question_id,
                        "model_answer": model_answer,
                        "student_answer": student_answer,
                        "evaluation": {
                            "grade": evaluation_response.grade,
                            "explanation": evaluation_response.explanation
                        }
                    })
            results.append(student_result)

        return json.dumps(results, indent=4)
