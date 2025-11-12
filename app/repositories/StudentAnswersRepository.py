import re, json, os
from pathlib import Path


class StudentAnswersRepository:

    def __init__(self, folder_path):
        self.path = Path(folder_path + '/submissions')
        self.student_answers = {}
        for student_dir in os.listdir(self.path):
            student_path = self.path / student_dir
            submission_file_path = student_path / 'submission.txt'
            with open(submission_file_path, encoding='utf-8') as file:
                text_content = file.read()
            parsed_data = []

            lines = [line.strip() for line in text_content.split('\n') if line.strip()]

            for line in lines:
                match = re.match(r'^(\d+)\.(.*)', line)  # Matches 'N. Answer Text'
                if match:
                    question_id = int(match.group(1))
                    student_answer = match.group(2).strip()

                    parsed_data.append({
                        "question_id": question_id,
                        "student_answer": student_answer
                    })

            self.student_answers[student_dir] = parsed_data

    def get_student_answers(self):
        return json.dumps(self.student_answers, indent=4)