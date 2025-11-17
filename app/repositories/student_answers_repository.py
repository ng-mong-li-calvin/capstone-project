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

        # The single regex pattern
        # Breakdown:
        # 1. (\d+)\. : Match and capture the question ID (Group 1).
        # 2. \s* : Match any whitespace after the ID.
        # 3. ([\s\S]*?) : Match and capture the unified Question and Answer (Group 2).
        # 4. (?=\n\n\d+\.|\Z) : Positive lookahead to ensure the match ends before the next question or at the end of the string.
        pattern = re.compile(r'(\d+)\.\s*([\s\S]*?)(?=\n\n\d+\.|\Z)\s*', re.MULTILINE)

        matches = pattern.findall(text_content)
        for match in matches:
            question_id = match[0]
            student_answer_full = match[1].strip()
            # Strips out the question if it's included (before ?/n)
            ans_qn = re.search(r'^.*?\?\s+/n(.*)', student_answer, re.DOTALL)
            if ans_qn:
                 return True, match.group(1)
                
            entry = {
                "question_id": int(question_id),
                "student_answer": student_answer_full
            }
            parsed_data.append(entry)

        student_answers[student_dir] = parsed_data

    # Returns a dictionary with student names as keys and list of their answers as values
    return student_answers
