import os
from dotenv import load_dotenv
from app.clients.OpenAPIClient import OpenAPIClient
from app.services.EvaluationFlowService import EvaluationFlowService

load_dotenv()


def main():
    print('OPENAI_API_KEY loaded:', bool(os.getenv('OPENAI_API_KEY')))
    client = OpenAPIClient(model='gpt-4o', api_key=os.getenv('OPENAI_API_KEY'))
    eval_flow_service = EvaluationFlowService()
    eval_flow_service.retrieve_data(path='./data/Rugby Football Club')
    eval_flow_service.evaluate_data(client)
    eval_flow_service.export_data()


if __name__ == "__main__":
    main()