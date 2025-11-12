import os

from app.repositories.GeminiClient import GeminiClient
from app.repositories.OpenAPIClient import OpenAPIClient
from app.services.FolderSubmissionsService import FolderSubmissionsService


def main():
    rugby_submissions = FolderSubmissionsService('./data/Rugby Football Club')
    client = GeminiClient(api_key=os.getenv('GOOGLE_API_KEY'))
    # client = OpenAPIClient(api_key=os.getenv('OPENAI_API_KEY'))
    rugby_submissions.evaluate_submissions(client)


if __name__ == "__main__":
    main()