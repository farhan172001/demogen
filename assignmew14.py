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
API_URL = "https://openai-api-wrapper-urtjok3rza-wl.a.run.app/api/chat/completions/"
MODEL = "gpt-3.5-turbo"  # Using this model via the wrapper API
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
    def __init__(self, api_url: str, model: str = MODEL):
        self.api_url = api_url
        self.model = model
    
    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get embedding for text using API wrapper."""
        try:
            # For embeddings, we'll use a special wrapper endpoint
            # For this example, we'll simulate embeddings with random vectors
            # In a real implementation, you'd call the embedding API
            logger.info(f"Getting embedding for text: {text[:50]}...")
            
            # Simulate API call for embeddings
            # Return a normalized random vector of the correct dimension
            vector = np.random.random(EMBEDDING_DIMENSION)
            return vector / np.linalg.norm(vector)
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            return None
    
    def generate_code(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """Call the API with retry logic."""
        for attempt in range(MAX_RETRIES):
            try:
                headers = {"Content-Type": "application/json"}
                payload = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000,
                }
                
                logger.info(f"Calling API (attempt {attempt+1}/{MAX_RETRIES})...")
                response = requests.post(
                    self.api_url, 
                    headers=headers, 
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
        
        system_message = """You are an expert Python developer. Your task is to generate initial boilerplate code 
        based on the user's requirement and the provided code examples. Focus on incorporating the best patterns
        from the examples while meeting the specific needs in the requirement."""
        
        user_message = f"""Requirement: {requirement}

Here are some relevant code examples that might be helpful:

{snippets_text}

Please generate a Python implementation that fulfills the requirement, inspired by these examples.
Include appropriate imports, error handling, and comments.
"""

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
        system_message = """You are an expert Python developer specializing in code refactoring.
        Your task is to refactor the provided code to improve:
        1. Readability: Use clear variable names, add helpful comments, and improve documentation
        2. Efficiency: Optimize performance where possible
        3. Maintainability: Follow best practices and design patterns
        4. Error handling: Ensure robust error handling
        5. Testing: Add appropriate assertions or test suggestions
        
        Return only the refactored code without explanations."""
        
        user_message = f"""Original requirement: {requirement}

Here's the initial code that needs refactoring:

```python
{initial_code}
```

Please refactor this code to improve its quality while maintaining its functionality.
"""

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
            "content": """
import smtplib
from email.message import EmailMessage

def send_email(subject, body, to_email, from_email, smtp_server, port, username, password):
    """Send a simple email message."""
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    
    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
            return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
""",
            "description": "Basic email sending function",
            "tags": ["email", "smtp", "communication"]
        },
        {
            "content": """
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_html_email(subject, text_content, html_content, to_email, from_email, smtp_server, port, username, password):
    """Send an email with both plain text and HTML content."""
    msg = MIMEMultipart("alternative")
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    
    # Attach parts
    part1 = MIMEText(text_content, "plain")
    part2 = MIMEText(html_content, "html")
    msg.attach(part1)
    msg.attach(part2)
    
    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(username, password)
            server.sendmail(from_email, to_email, msg.as_string())
            return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
""",
            "description": "HTML email sending function",
            "tags": ["email", "html", "communication"]
        },
        {
            "content": """
import logging

def setup_logger(name, log_file, level=logging.INFO, format_str=None):
    """Set up a logger with file and console handlers."""
    if format_str is None:
        format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter(format_str))
    logger.addHandler(file_handler)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(format_str))
    logger.addHandler(console_handler)
    
    return logger
""",
            "description": "Logging setup function",
            "tags": ["logging", "utility"]
        },
        {
            "content": """
import requests
import time

def retry_request(url, max_retries=3, backoff_factor=0.5, **kwargs):
    """Make HTTP request with retry logic."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, **kwargs)
            response.raise_for_status()
            return response
        except (requests.exceptions.RequestException) as e:
            if attempt == max_retries - 1:
                raise
            
            wait_time = backoff_factor * (2 ** attempt)
            print(f"Request failed: {e}. Retrying in {wait_time:.2f} seconds...")
            time.sleep(wait_time)
""",
            "description": "HTTP request with retry logic",
            "tags": ["http", "retry", "networking"]
        },
        {
            "content": """
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

@dataclass
class User:
    name: str
    email: str
    age: int
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(asdict(self))
    
    @classmethod
    def from_json(cls, json_str: str) -> 'User':
        """Create from JSON string."""
        data = json.loads(json_str)
        return cls(**data)

@dataclass
class UserCollection:
    users: List[User]
    
    def save_to_file(self, filename: str) -> None:
        """Save users to a JSON file."""
        with open(filename, 'w') as f:
            json.dump([asdict(user) for user in self.users], f, indent=2)
    
    @classmethod
    def load_from_file(cls, filename: str) -> 'UserCollection':
        """Load users from a JSON file."""
        with open(filename, 'r') as f:
            data = json.load(f)
            users = [User(**user_data) for user_data in data]
            return cls(users)
""",
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