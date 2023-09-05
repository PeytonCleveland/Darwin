import os
from dotenv import load_dotenv
import openai
import csv
import argparse

# Load environment variables from .env.local file
load_dotenv(dotenv_path=".env.local")

# Fetch the OpenAI API key from the environment variable
openai_api_key = os.environ.get('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in .env.local file or environment variables")

openai.api_key = openai_api_key

EQUAL_PROMPT="""Here are two Instructions to ChatGPT AI, do you think they are equal to each other, which meet the
following requirements:

1. They have same constraints and requirments.
2. They have same depth and breadth of the inquiry.
The First Prompt: {first}
The Second Prompt: {second}
Your Judgement (Just answer: Equal or Not Equal. No need to explain the reason.):"""

class Node:
    def __init__(self, prompt, response, is_refusal=False, parent=None):
        self.prompt = prompt
        self.response = response
        self.is_refusal = is_refusal
        self.children = []
        self.parent = parent

    def remove(self):
        if self.parent:
            self.parent.children.remove(self)
        self.parent = None
        self.children = []

    def depth_evolve(self):
        """Evolve node prompt by deepening, increasing reasoning, concretizing, adding constraints, or complicating input"""
        pass

    def breadth_evolve(self):
        pass

def should_prune(node, parent):
    """Evaluate the fitness of a node"""

    # Redundancy check
    if node.prompt.strip == parent.prompt.strip:
        return True

    # Prune if the node's prompt content is empty or just whitespace
    if not node.prompt.strip():
        return True
    
    prompt = EQUAL_PROMPT.format(first=node.prompt, second=parent.prompt)
    response = openai.Completion.create(engine="davinci", prompt=prompt, max_tokens=50)

    # Prune if the model deems them equal
    if response.choices[0].text.strip() == "Equal":
        return True
    
    return False

def load_forest_from_csv(filename):
    """Load the forest (list of root nodes) from a given CSV file."""
    forest = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            prompt_text = row[0]  # assuming the prompt is in the first column
            root_node = Node(Prompt(prompt_text))
            forest.append(root_node)
    return forest

def validate_csv_format(filename):
    """Check if the given CSV file is in the correct format."""
    
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        
        # 1. Validate header columns
        headers = reader.fieldnames
        required_columns = {'prompt', 'response', 'is_refusal'}
        
        if not required_columns.issubset(headers):
            print("Error: CSV is missing one or more required columns.")
            return False
        
        # 2. Validate 'is_refusal' data and check for empty values
        valid_is_refusal_values = {'True', 'False', '1', '0', 'Yes', 'No'}
        for row_num, row in enumerate(reader, 1):  # Starting the row_num from 1 for human-readable indexing
            # Check for empty values in required columns
            for column in required_columns:
                if not row[column].strip():  # This checks if the value is either empty or just whitespace
                    print(f"Error: Missing value in column '{column}' on row {row_num}.")
                    return False
            
            if row['is_refusal'] not in valid_is_refusal_values:
                print(f"Error: Invalid value '{row['is_refusal']}' in 'is_refusal' column for prompt '{row['prompt']}' on row {row_num}.")
                return False

    return True

def get_response(prompt_text):
    response = openai.Completion.create(engine="davinci", prompt=prompt_text, max_tokens=150)
    return response.choices[0].text.strip()

def evolve(node):
    # Use any of your evolution logic here.
    evolved_prompt_text = get_response(node.prompt.text)  # Simplified evolution for demonstration
    evolved_prompt = Prompt(evolved_prompt_text)
    evolved_node = Node(evolved_prompt, parent=node)
    node.children.append(evolved_node)
    return evolved_node

def print_tree(node, indent=""):
    print(indent + str(node.prompt))
    for child in node.children:
        print_tree(child, indent + "  ")

def main():
    parser = argparse.ArgumentParser(description='Evolve prompts using GPT-4 based on a CSV input.')
    parser.add_argument('csv_file', type=str, help='Path to the CSV file containing the prompts to evolve.')
    
    # Set default value for output_file to 'output.csv'
    parser.add_argument('output_file', type=str, nargs='?', default='output.csv', 
                        help='Path to the output file where results will be saved. Defaults to "output.csv".')
    
    parser.add_argument('--validate', action='store_true', help='Check if the CSV is in the correct format and then exit.')

    args = parser.parse_args()
    
    if args.validate:
        if validate_csv_format(args.csv_file):
            print("CSV format is valid.")
        else:
            print("CSV format is not valid. Please check the file.")
        return  # Exit after validation
    
    forest = load_forest_from_csv(args.csv_file)

if __name__ == "__main__":
    main()
