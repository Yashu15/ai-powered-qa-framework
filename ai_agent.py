"""Generate, run, and retry pytest unit tests for the sample app/main.py logic."""

import os
import re
import docker
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ------------------------------------------------------------------
# 1. Configuration & Setup
# ------------------------------------------------------------------
llm = ChatOllama(model="llama3", temperature=0.2)
docker_client = docker.from_env()

APP_CODE_PATH = "app/main.py"
DOCKER_IMAGE = "target-app:latest"
MAX_RETRIES = 3

# ------------------------------------------------------------------
# 2. Prompts
# ------------------------------------------------------------------
GENERATE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a Python QA Engineer. Generate ONLY executable Python code using pytest. Do NOT use markdown block ticks (``` or ```python). Do NOT add explanatory intro or outro text. Import application functions using: `from main import calculate_discount, format_user_name`."),
    ("user", "Write unit tests for the following application code using pytest:\n\n{code}")
])

HEAL_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a Python QA Engineer. Fix the failing pytest test suite based on the provided error output. Return ONLY valid, executable Python code without markdown code blocks or formatting. Import target functions using `from main import calculate_discount, format_user_name`."),
    ("user", "Failing Test Code:\n{test_code}\n\nExecution Log Output:\n{error_log}\n\nProvide corrected pytest code:")
])

# ------------------------------------------------------------------
# 3. Helper Functions
# ------------------------------------------------------------------
def clean_code_output(raw_text: str) -> str:
    """Strips markdown code blocks (```python ... ```) or conversational intro text."""
    pattern = r"```(?:python)?\s*(.*?)\s*```"
    match = re.search(pattern, raw_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Fallback to cleaning leading markdown backticks
    lines = raw_text.strip().split("\n")
    cleaned_lines = [line for line in lines if not line.strip().startswith("```")]
    return "\n".join(cleaned_lines).strip()

def read_source_code(file_path: str) -> str:
    with open(file_path, "r") as f:
        return f.read()

def run_tests_in_docker(test_code: str) -> tuple[bool, str]:
    test_file_path = "app/test_main.py"
    clean_code = clean_code_output(test_code)
    
    with open(test_file_path, "w") as f:
        f.write(clean_code)

    container = None
    try:
        # Create container manually to ensure log capture before auto-removal
        container = docker_client.containers.create(
        image=DOCKER_IMAGE,
        command="pytest -v test_main.py --html=report.html --self-contained-html",
        volumes={os.path.abspath("app"): {"bind": "/app", "mode": "rw"}},
        working_dir="/app"
    )
        container.start()
        result = container.wait()
        exit_code = result.get("StatusCode", 1)
        
        # Retrieve combined stdout and stderr logs
        logs = container.logs(stdout=True, stderr=True).decode("utf-8")
        
        if exit_code == 0:
            return True, logs
        else:
            return False, logs if logs.strip() else f"Pytest failed with exit status {exit_code}."

    except Exception as e:
        return False, str(e)
    finally:
        if container:
            try:
                container.remove(force=True)
            except Exception:
                pass
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

# ------------------------------------------------------------------
# 4. Main Execution Loop
# ------------------------------------------------------------------
def main():
    print("🤖 [AI AGENT] Reading application source code...")
    source_code = read_source_code(APP_CODE_PATH)

    print("🤖 [AI AGENT] Generating initial unit test suite via Ollama (llama3)...")
    generator_chain = GENERATE_PROMPT | llm | StrOutputParser()
    raw_generated_code = generator_chain.invoke({"code": source_code})
    test_code = clean_code_output(raw_generated_code)

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\n🐳 [DOCKER] Executing tests inside container (Attempt {attempt}/{MAX_RETRIES})...")
        passed, log = run_tests_in_docker(test_code)

        if passed:
            print("✅ [SUCCESS] All unit tests passed inside the container!\n")
            print(log)
            break
        else:
            print("❌ [FAILURE] Tests failed in container.")
            print(f"--- Traceback Summary ---\n{log[:500]}\n-------------------------")
            
            if attempt < MAX_RETRIES:
                print("🔄 [SELF-HEALING] Feeding traceback to LLM to repair test script...")
                healer_chain = HEAL_PROMPT | llm | StrOutputParser()
                raw_healed_code = healer_chain.invoke({"test_code": test_code, "error_log": log})
                test_code = clean_code_output(raw_healed_code)
            else:
                print("💥 [FAILED] Max retries reached.")

if __name__ == "__main__":
    main()