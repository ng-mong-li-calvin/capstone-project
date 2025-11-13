import fitz  # PyMuPDF
from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from app.repositories.ModelQnARepository import ModelQnARepository
from dotenv import load_dotenv
from langchain_classic.chains import create_retrieval_chain



def find_pdf_in_folder(folder_path: str, recursive: bool = True):
    path = Path(folder_path)

    if not path.exists():
        raise FileNotFoundError(f"Folder '{folder_path}' does not exist.")

    # Choose search method
    pattern = '**/*.pdf' if recursive else '*.pdf'
    pdf_files = list(path.glob(pattern) if not recursive else path.rglob('*.pdf'))

    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in '{folder_path}'")

    # Return first PDF path
    return pdf_files[0]

topic = 'Solar System'
folder_path = 'C:/Users/Tay Wen Kai/PycharmProjects/capstone-project/data/Solar System'
#replace path with correct path directory
pdf_path = find_pdf_in_folder(f'C:/Users/Tay Wen Kai/PycharmProjects/capstone-project/data/{topic}')
# ========== 2. Extract Text from PDFs ==========
def extract_text_from_pdf_folder(folder_path: str) -> str:
    """Extracts all text from PDF files in a folder and returns concatenated text."""
    pdf_paths = list(Path(folder_path).rglob("*.pdf"))
    if not pdf_paths:
        raise FileNotFoundError(f"No PDF files found in {folder_path}")

    all_text = ""
    for pdf_file in pdf_paths:
        doc = fitz.open(pdf_file)
        for page in doc:
            all_text += page.get_text()
        all_text += "\n\n"  # separate PDFs
    return all_text

context_text = extract_text_from_pdf_folder(folder_path)


splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
chunks = [Document(page_content=t) for t in splitter.split_text(context_text)]

# Create embedding model
embeddings = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')

# Build FAISS vector store from the document chunks
vectorstore = FAISS.from_documents(chunks, embeddings)

# Create a retriever for querying later
retriever = vectorstore.as_retriever(search_kwargs={'k': 4})

questions_json = ModelQnARepository(folder_path).get_model_qna()
print(questions_json)

load_dotenv()
# ========== INITIALIZE MODEL ==========
from pydantic import BaseModel
from openai import OpenAI
import json

# Initialize OpenAI client
client = OpenAI()
# Define the structured output schema
class QuestionAnswer(BaseModel):
    question_id: int
    question_text: str
    answer_text: str
    source_info: str = "Not Found"  # default if no source found

# ========== RUN FOR EACH QUESTION ==========
answers = []
for q in json.loads(questions_json):
    question_id = q["question_id"]
    question_text = q["question_text"]

    # Retrieve relevant context for this specific question
    retrieved_docs = retriever.invoke(question_text)  # returns Document[]

    formatted_context = "\n\n".join([d.page_content for d in retrieved_docs])

    # Prepare single-question JSON input
    single_question_json = json.dumps([q], indent=2)
    prompt = f"""
    Context:
    {formatted_context}

    Question:
    {single_question_json}

    Answer in JSON format with fields:
    - question_id
    - question_text
    - answer_text (if not found, write "Not found in context")
    - source_info (page number, section, or "Not Found")
    """
    # Call OpenAI chat with structured output parsing
    completion = client.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are an expert extraction specialist. Answer ONLY in JSON format."},
            {"role": "user", "content": prompt}
        ],
        response_format=QuestionAnswer,
    )
    # Extract the parsed result
    answer_obj = completion.choices[0].message.parsed
    answers.append(answer_obj.dict())

# ========== PRINT STRUCTURED OUTPUT ==========
# Convert final answers list to JSON
final_json = json.dumps(answers, indent=4, ensure_ascii=False)
# print(final_json)
#
# with open((folder_path+"/solutions.txt"), "w") as file:
#     file.write(final_json)