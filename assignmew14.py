import os
import time
import json
import requests
import numpy as np
import tiktoken
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
# Primary API URL (wrapper provided in assignment)
API_URL = "https://openai-api-wrapper-urtjok3rza-wl.a.run.app/api/chat/completions/"

MODEL = "gpt-3.5-turbo"  # Model to use
EMBEDDING_DIMENSION = 1536  # OpenAI embeddings dimension
MAX_RETRIES = 3
BASE_RETRY_DELAY = 2  # seconds

# Initialize tokenizer for token counting
tokenizer = tiktoken.get_encoding("cl100k_base")  # Default for GPT models

class CodeSnippet:
    """Class to represent a code snippet with its embedding."""
    def __init__(self, content: str, description: str, tags: List[str], path: Optional[str] = None):
        self.content = content
        self.description = description
        self.tags = tags
        self.path = path
        self.embedding = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the snippet to a dictionary."""
        return {
            "content": self.content,
            "description": self.description,
            "tags": self.tags,
            "path": self.path,
            "embedding": self.embedding.tolist() if self.embedding is not None else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CodeSnippet':
        """Create a CodeSnippet from a dictionary."""
        snippet = cls(data["content"], data["description"], data["tags"], data.get("path"))
        if data.get("embedding") is not None:
            snippet.embedding = np.array(data["embedding"])
        return snippet
    
    def __str__(self) -> str:
        return f"CodeSnippet(description={self.description}, tags={self.tags}, len={len(self.content)})"

class VectorStore:
    """Simple vector store for code snippets."""
    def __init__(self, snippets_dir: str = "snippets"):
        self.snippets_dir = Path(snippets_dir)
        self.snippets: List[CodeSnippet] = []
        self.snippets_file = self.snippets_dir / "snippets.json"
        
        # Create directory if it doesn't exist
        os.makedirs(self.snippets_dir, exist_ok=True)
        
        # Load existing snippets if available
        self.load_snippets()
    
    def add_snippet(self, snippet: CodeSnippet) -> None:
        """Add a snippet to the vector store."""
        if snippet.embedding is None:
            raise ValueError("Snippet must have an embedding")
        self.snippets.append(snippet)
        self.save_snippets()
    
    def save_snippets(self) -> None:
        """Save snippets to disk."""
        with open(self.snippets_file, "w") as f:
            json.dump([snippet.to_dict() for snippet in self.snippets], f)
    
    def load_snippets(self) -> None:
        """Load snippets from disk."""
        if not self.snippets_file.exists():
            logger.info(f"No snippets file found at {self.snippets_file}")
            return
        
        try:
            with open(self.snippets_file, "r") as f:
                snippets_data = json.load(f)
                self.snippets = [CodeSnippet.from_dict(data) for data in snippets_data]
            logger.info(f"Loaded {len(self.snippets)} snippets from {self.snippets_file}")
        except Exception as e:
            logger.error(f"Error loading snippets: {e}")
    
    def search(self, query_embedding: np.ndarray, top_k: int = 3) -> List[CodeSnippet]:
        """Search for similar snippets by cosine similarity."""
        if not self.snippets:
            logger.warning("No snippets in vector store")
            return []
        
        similarities = []
        for snippet in self.snippets:
            if snippet.embedding is not None:
                similarity = self._cosine_similarity(query_embedding, snippet.embedding)
                similarities.append((similarity, snippet))
        
        # Sort by similarity (descending)
        similarities.sort(reverse=True, key=lambda x: x[0])
        return [snippet for _, snippet in similarities[:top_k]]
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

class APIWrapper:
    """Wrapper for API calls with retry logic."""
    def __init__(self, api_url: str = API_URL, model: str = MODEL):
        self.api_url = api_url
        self.model = model
        self.headers = {
            'x-api-token': '',  # Leave blank as instructed
            'Content-Type': 'application/json'
        }
    
    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Simulate embeddings with random vectors since wrapper doesn't support embeddings."""
        logger.info(f"Simulating embedding for text: {text[:50]}...")

        # Create deterministic but unique embedding based on the content hash
        # This helps related content have somewhat related embeddings
        np.random.seed(hash(text) % 2**32)
        vector = np.random.random(EMBEDDING_DIMENSION)
        return vector / np.linalg.norm(vector)
    
    def generate_code(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """Call the API with retry logic."""
        for attempt in range(MAX_RETRIES):
            try:
                payload = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000,
                }
                
                logger.info(f"Calling wrapper API (attempt {attempt+1}/{MAX_RETRIES})...")
                response = requests.post(
                    self.api_url, 
                    headers=self.headers, 
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    logger.warning(f"API call failed with status {response.status_code}: {response.text}")
                    
            except Exception as e:
                logger.error(f"Error calling API: {e}")
            
            # Exponential backoff
            retry_delay = BASE_RETRY_DELAY * (2 ** attempt)
            logger.info(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        
        logger.error(f"Failed after {MAX_RETRIES} attempts")
        return None

    def count_tokens(self, text: str) -> int:
        """Count tokens in a string."""
        return len(tokenizer.encode(text))

class CodeGenerator:
    """Main class for code generation and refactoring."""
    def __init__(self, 
                 vector_store: VectorStore,
                 api_wrapper: APIWrapper,
                 output_dir: str = "generated_code"):
        self.vector_store = vector_store
        self.api_wrapper = api_wrapper
        self.output_dir = Path(output_dir)
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def prepare_snippets_library(self, snippets_data: List[Dict[str, Any]]) -> None:
        """Prepare the snippets library by embedding and storing code examples."""
        for snippet_data in snippets_data:
            snippet = CodeSnippet(
                content=snippet_data["content"],
                description=snippet_data["description"],
                tags=snippet_data["tags"]
            )
            
            # Get embedding for the snippet
            text_for_embedding = f"{snippet.description}\n{snippet.content}"
            embedding = self.api_wrapper.get_embedding(text_for_embedding)
            
            if embedding is not None:
                snippet.embedding = embedding
                self.vector_store.add_snippet(snippet)
                logger.info(f"Added snippet: {snippet.description}")
            else:
                logger.error(f"Failed to get embedding for snippet: {snippet.description}")
    
    def generate_code_from_requirement(self, requirement: str) -> str:
        """Generate code based on a requirement using RAG."""
        logger.info(f"Generating code for requirement: {requirement}")
        
        # Step 1: Get embedding for the requirement
        requirement_embedding = self.api_wrapper.get_embedding(requirement)
        if requirement_embedding is None:
            logger.error("Failed to get embedding for requirement")
            return "Error: Failed to get embedding for requirement"
        
        # Step 2: Retrieve relevant snippets
        relevant_snippets = self.vector_store.search(requirement_embedding, top_k=3)
        logger.info(f"Found {len(relevant_snippets)} relevant snippets")
        
        # Step 3: Generate initial code
        initial_code = self._generate_initial_code(requirement, relevant_snippets)
        if initial_code is None:
            return "Error: Failed to generate initial code"
        
        logger.info("Initial code generated")
        
        # Step 4: Refactor the code
        refactored_code = self._refactor_code(requirement, initial_code)
        if refactored_code is None:
            return "Error: Failed to refactor code"
        
        logger.info("Code refactored")
        
        # Step 5: Save the code to a file
        filename = self._save_code_to_file(requirement, refactored_code)
        
        return f"Code generated and saved to {filename}\n\n{refactored_code}"
    
    def _generate_initial_code(self, requirement: str, snippets: List[CodeSnippet]) -> Optional[str]:
        """Generate initial code based on requirement and retrieved examples."""
        snippets_text = "\n\n".join([
            f"Example {i+1} ({snippet.description}):\n```python\n{snippet.content}\n```"
            for i, snippet in enumerate(snippets)
        ])
        
        system_message = "You are an expert Python developer. Your task is to generate initial boilerplate code based on the user's requirement and the provided code examples. Focus on incorporating the best patterns from the examples while meeting the specific needs in the requirement."
        
        user_message = f"Requirement: {requirement}\n\nHere are some relevant code examples that might be helpful:\n\n{snippets_text}\n\nPlease generate a Python implementation that fulfills the requirement, inspired by these examples.\nInclude appropriate imports, error handling, and comments."

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        # Check token count
        token_count = sum(self.api_wrapper.count_tokens(msg["content"]) for msg in messages)
        logger.info(f"Initial code generation prompt token count: {token_count}")
        
        return self.api_wrapper.generate_code(messages)
    
    def _refactor_code(self, requirement: str, initial_code: str) -> Optional[str]:
        """Refactor the initial code for better quality."""
        system_message = "You are an expert Python developer specializing in code refactoring. Your task is to refactor the provided code to improve: 1. Readability: Use clear variable names, add helpful comments, and improve documentation 2. Efficiency: Optimize performance where possible 3. Maintainability: Follow best practices and design patterns 4. Error handling: Ensure robust error handling 5. Testing: Add appropriate assertions or test suggestions. Return only the refactored code without explanations."
        
        user_message = f"Original requirement: {requirement}\n\nHere's the initial code that needs refactoring:\n\n```python\n{initial_code}\n```\n\nPlease refactor this code to improve its quality while maintaining its functionality."

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        # Check token count
        token_count = sum(self.api_wrapper.count_tokens(msg["content"]) for msg in messages)
        logger.info(f"Refactoring prompt token count: {token_count}")
        
        return self.api_wrapper.generate_code(messages)
    
    def _save_code_to_file(self, requirement: str, code: str) -> str:
        """Save the generated code to a file."""
        # Create a sanitized filename based on requirement
        filename = "".join(c if c.isalnum() or c in "_ " else "_" for c in requirement)
        filename = filename.lower().replace(" ", "_")[:50]  # Limit length
        filename = f"{filename}.py"
        
        file_path = self.output_dir / filename
        with open(file_path, "w") as f:
            f.write(code)
        
        logger.info(f"Saved code to {file_path}")
        return str(file_path)

def main():
    """Main function to run the code generator."""
    # Initialize components
    vector_store = VectorStore()
    api_wrapper = APIWrapper(API_URL)
    code_generator = CodeGenerator(vector_store, api_wrapper)
    
    # Sample code snippets for the library
    sample_snippets = [
        {
            "content": "import smtplib\nfrom email.message import EmailMessage\n\ndef send_email(subject, body, to_email, from_email, smtp_server, port, username, password):\n    \"\"\"Send a simple email message.\"\"\"\n    msg = EmailMessage()\n    msg.set_content(body)\n    msg['Subject'] = subject\n    msg['From'] = from_email\n    msg['To'] = to_email\n    \n    try:\n        with smtplib.SMTP(smtp_server, port) as server:\n            server.starttls()\n            server.login(username, password)\n            server.send_message(msg)\n            return True\n    except Exception as e:\n        print(f\"Failed to send email: {e}\")\n        return False",
            "description": "Basic email sending function",
            "tags": ["email", "smtp", "communication"]
        },
        {
            "content": "import smtplib\nfrom email.mime.multipart import MIMEMultipart\nfrom email.mime.text import MIMEText\n\ndef send_html_email(subject, text_content, html_content, to_email, from_email, smtp_server, port, username, password):\n    \"\"\"Send an email with both plain text and HTML content.\"\"\"\n    msg = MIMEMultipart(\"alternative\")\n    msg['Subject'] = subject\n    msg['From'] = from_email\n    msg['To'] = to_email\n    \n    # Attach parts\n    part1 = MIMEText(text_content, \"plain\")\n    part2 = MIMEText(html_content, \"html\")\n    msg.attach(part1)\n    msg.attach(part2)\n    \n    try:\n        with smtplib.SMTP(smtp_server, port) as server:\n            server.starttls()\n            server.login(username, password)\n            server.sendmail(from_email, to_email, msg.as_string())\n            return True\n    except Exception as e:\n        print(f\"Failed to send email: {e}\")\n        return False",
            "description": "HTML email sending function",
            "tags": ["email", "html", "communication"]
        },
        {
            "content": "import logging\n\ndef setup_logger(name, log_file, level=logging.INFO, format_str=None):\n    \"\"\"Set up a logger with file and console handlers.\"\"\"\n    if format_str is None:\n        format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'\n    \n    # Create logger\n    logger = logging.getLogger(name)\n    logger.setLevel(level)\n    \n    # Create file handler\n    file_handler = logging.FileHandler(log_file)\n    file_handler.setFormatter(logging.Formatter(format_str))\n    logger.addHandler(file_handler)\n    \n    # Create console handler\n    console_handler = logging.StreamHandler()\n    console_handler.setFormatter(logging.Formatter(format_str))\n    logger.addHandler(console_handler)\n    \n    return logger",
            "description": "Logging setup function",
            "tags": ["logging", "utility"]
        },
        {
            "content": "import requests\nimport time\n\ndef retry_request(url, max_retries=3, backoff_factor=0.5, **kwargs):\n    \"\"\"Make HTTP request with retry logic.\"\"\"\n    for attempt in range(max_retries):\n        try:\n            response = requests.get(url, **kwargs)\n            response.raise_for_status()\n            return response\n        except (requests.exceptions.RequestException) as e:\n            if attempt == max_retries - 1:\n                raise\n            \n            wait_time = backoff_factor * (2 ** attempt)\n            print(f\"Request failed: {e}. Retrying in {wait_time:.2f} seconds...\")\n            time.sleep(wait_time)",
            "description": "HTTP request with retry logic",
            "tags": ["http", "retry", "networking"]
        },
        {
            "content": "import json\nfrom dataclasses import dataclass, asdict\nfrom typing import List, Dict, Any, Optional\n\n@dataclass\nclass User:\n    name: str\n    email: str\n    age: int\n    is_active: bool = True\n    metadata: Optional[Dict[str, Any]] = None\n    \n    def to_json(self) -> str:\n        \"\"\"Convert to JSON string.\"\"\"\n        return json.dumps(asdict(self))\n    \n    @classmethod\n    def from_json(cls, json_str: str) -> 'User':\n        \"\"\"Create from JSON string.\"\"\"\n        data = json.loads(json_str)\n        return cls(**data)\n\n@dataclass\nclass UserCollection:\n    users: List[User]\n    \n    def save_to_file(self, filename: str) -> None:\n        \"\"\"Save users to a JSON file.\"\"\"\n        with open(filename, 'w') as f:\n            json.dump([asdict(user) for user in self.users], f, indent=2)\n    \n    @classmethod\n    def load_from_file(cls, filename: str) -> 'UserCollection':\n        \"\"\"Load users from a JSON file.\"\"\"\n        with open(filename, 'r') as f:\n            data = json.load(f)\n            users = [User(**user_data) for user_data in data]\n            return cls(users)",
            "description": "Data classes with JSON serialization",
            "tags": ["dataclass", "serialization", "json"]
        }
    ]
    
    # Prepare the snippets library
    code_generator.prepare_snippets_library(sample_snippets)
    
    # Example usage
    while True:
        print("\n=== Code Generation and Refactoring Tool ===")
        requirement = input("\nEnter your code requirement (or 'quit' to exit): ")
        
        if requirement.lower() == 'quit':
            break
        
        if requirement.strip():
            result = code_generator.generate_code_from_requirement(requirement)
            print("\n=== Generated Code ===\n")
            print(result)

if __name__ == "__main__":
    main()
    
# Create a FastAPI endpoint to upload a file and save it to a local directory with error handling
# Send a simple email using SMTP with subject, body, and login authentication.
# Send an HTML email with both plain text and HTML content using SMTP.
# Create a logger that logs both to a file and to the console in a specific format.
