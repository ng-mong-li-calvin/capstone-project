import re, os
from pathlib import Path

""" Repository to parse and retrieve student answers from submission files. """


def student_answers_repository(folder_path) -> dict:
    """ Parses student submission files and retrieves their answers."""
    path = Path(folder_path + '/submissions')
    student_answers = {}
    for student_dir in os.listdir(path):
        student_path = path / student_dir
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

        student_answers[student_dir] = parsed_data

    # Returns a dictionary with student names as keys and list of their answers as values
    return student_answers