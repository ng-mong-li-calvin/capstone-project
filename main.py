import os
from dotenv import load_dotenv
from app.clients.OpenAPIClient import OpenAPIClient
from app.services.EvaluationFlowService import EvaluationFlowService

load_dotenv()


def main():
    print('OPENAI_API_KEY loaded:', bool(os.getenv('OPENAI_API_KEY')))
    client = OpenAPIClient(model='gpt-4o-mini', api_key=os.getenv('OPENAI_API_KEY'))
    eval_flow_service = EvaluationFlowService()
    eval_flow_service.get_data(path='./data/Rugby Football Club')
    eval_flow_service.evaluate_data(client)
    client.set_model('gpt-4o')
    eval_flow_service.evaluate_evaluations(client)
    eval_flow_service.export_data()


if __name__ == "__main__":
    main()