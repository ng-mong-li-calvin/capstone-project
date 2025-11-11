from app.repositories.ModelAnswerRepository import ModelAnswerRepository
from app.repositories.StudentAnswersRepository import StudentAnswersRepository


def main():
    rugby_model = ModelAnswerRepository('Rugby Football Club')
    rugby_model.set_model_answer()
    rugby_students = StudentAnswersRepository('Rugby Football Club')
    rugby_students.set_student_answers()
    with open('data/model_answers.json', 'w') as f:
        f.write(rugby_model.get_model_answer())
    with open('data/student_answers.json', 'w') as f:
        f.write(rugby_students.get_student_answers())


if __name__ == "__main__":
    main()