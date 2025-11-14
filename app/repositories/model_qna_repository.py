from pathlib import Path
import json, re

""" Repository to parse and retrieve model Q&A from answer files. """


def model_qna_repository(folder_path) -> list:
    """ Parses model answer file and retrieves question and answer pairs. """
    path = Path(folder_path)
    model_answer_file_path = next(path.rglob('*.txt'))  # Get the txt file path
    with open(model_answer_file_path, 'r') as f:
        text_content = f.read()
    parsed_data = []

    # Split the content into blocks by two or more newlines
    # and filter out empty strings
    blocks = [block.strip() for block in re.split(r'\n\n+', text_content) if block.strip()]

    # Assuming the first block might be introductory text, we'll try to find
    # the first block that starts with a question number pattern.
    question_answer_blocks = []
    found_first_question = False
    for block in blocks:
        # Check for both 'N)' and 'N.' formats
        if re.match(r'^\d+[).]', block):
            found_first_question = True
        if found_first_question:
            question_answer_blocks.append(block)

    for block in question_answer_blocks:
        # Find the first newline to separate question from answer
        first_newline_index = block.find('\n')
        if first_newline_index == -1:
            # If no newline, assume the whole block is the question (unlikely for answers)
            question_line = block
            answer_text = ""
        else:
            question_line = block[:first_newline_index]
            answer_text = block[first_newline_index + 1:].strip()

        # Use regex to extract question_id and question_text from the question_line
        # Modified regex to accept both 'N)' and 'N.' formats
        match = re.match(r'^(\d+)[).](.*)', question_line)
        if match:
            question_id = int(match.group(1))
            question_text = match.group(2).strip()

            parsed_data.append({
                "question_id": question_id,
                "question_text": question_text,
                "answer_text": answer_text
            })

    # Returns a list of dictionaries with question_id, question_text, and answer_text
    return parsed_data