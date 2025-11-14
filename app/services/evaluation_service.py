import json
from dotenv import load_dotenv
from app.models.schemas import EvaluationResponse

""" Service module to evaluate student answers against model answers"""


load_dotenv()


def evaluate_all_students(client, model_qna: list, student_answers: dict) -> list:
    """ Evaluate all student answers against the question and model answer. """
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
            model_answer_entry = next(
                (item for item in model_qna if item['question_id'] == question_id),
                None ) # Default if not found
            if model_answer_entry:
                question_text = model_answer_entry['question_text']
                model_answer = model_answer_entry['answer_text']
                evaluation_response: EvaluationResponse = client.evaluate(
                    question_text,
                    model_answer,
                    student_answer
                )
                student_result["evaluations"].append({
                    "question_id": question_id,
                    "question_text": question_text,
                    "model_answer": model_answer,
                    "student_answer": student_answer,
                    "evaluation": {
                        "grade": evaluation_response.grade,
                        "explanation": evaluation_response.explanation
                    }
                })
        results.append(student_result)

    """
    Return the evaluation results as a JSON serializable list.
    Format:
    [ { "student": "student_name",
        "evaluations": [ {
            "question_id": N,
            "question_text": "...",
            "model_answer": "...",
            "student_answer": "...",
            "evaluation":
                { "grade": "...", "explanation": "..." }
            }, ...
        ]
    }, ... ]
    """

    return results


def evaluate_all_evaluations(client, json_serializable) -> list:
    """ Re-evaluate all previous evaluations for further analysis or consistency checks. """
    for student in json_serializable:
        for question in student.get("evaluations", []):
            question_text = question.get("question_text", "")
            model_answer = question.get("model_answer", "")
            student_answer = question.get("student_answer", "")
            evaluation = question.get("evaluation", {})
            response = client.evaluation_review(
                question_text,
                model_answer,
                student_answer,
                question
            )
            evaluation["review"] = response
    return json_serializable