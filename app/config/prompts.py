""" Prompts for exam grading tasks."""


SYSTEM_PROMPT_EXAM_GRADER = "You are an expert exam grader."

SYSTEM_PROMPT_JSON = "Your response must be a valid JSON object with 'grade' and 'explanation' fields."

PROMPT_4o_TEMPLATE = """
            Based on the question and model answer, grade the student answer as binary 'Pass/Fail' and give a simple explanation no more than 20 words.

            Question: {question}

            Model answer: {model}

            Student answer: {student}
            """

PROMPT_4o_mini_TEMPLATE = """
            Based on the question and model answer, grade the student answer as binary 'Pass/Fail' and give a simple explanation no more than 20 words.
            Score based solely on factual accuracy and disregard format.
            Example: If the model answer is RFC 792 and the student answer is RFC 0792, the grade is 'Pass'.

            Question: {question}

            Model answer: {model}

            Student answer: {student}
            """

PROMPT_35_turbo_TEMPLATE = """
            Based on the question and model answer, grade the student answer as binary 'Pass/Fail' and give a simple explanation no more than 20 words. 

            Question: {question}

            Model answer: {model}

            Student answer: {student}
            """