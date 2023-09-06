import os
from dotenv import load_dotenv
import openai
import csv
import argparse
from tqdm import tqdm
from prompts import EQUAL_PROMPT, SYSTEM_PROMPTS, DEPTH_EVOLUTION_PROMPTS, DIFFICULTY_PROMPT, BREADTH_EVOLUTION_PROMPT

# Load environment variables from .env.local file
load_dotenv()

# Fetch the OpenAI API key from the environment variable
openai_api_key = os.environ.get('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in .env.local file or environment variables")

openai.api_key = openai_api_key

class Node:
    def __init__(self, system_prompt, user_prompt, assistant_response, is_refusal=False, parent=None):
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.assistant_response = assistant_response
        self.is_refusal = is_refusal
        self.children = []
        self.parent = parent

def should_prune(evolved_prompt, parent):
    """Evaluate the fitness of a potential child node based on its evolved prompt"""

    # Redundancy check
    if evolved_prompt.strip() == parent.user_prompt.strip():
        return True

    # Prune if the evolved prompt content is empty or just whitespace
    if not evolved_prompt.strip():
        return True
    
    comparison_prompt = EQUAL_PROMPT.format(first=evolved_prompt, second=parent.user_prompt)
    response = get_response(comparison_prompt)

    # Prune if the model deems them equal
    if response.strip() == "Equal":
        return True
    
    return False

def load_forest_from_csv(filename):
    """Load the forest (list of root nodes) from a given CSV file."""
    forest = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        
        # Skip the header row
        next(reader, None)
        
        for row in reader:
            is_refusal = row[0]
            system_prompt = row[1]
            user_prompt = row[2]
            assistant_response = row[3]
            root_node = Node(system_prompt, user_prompt, assistant_response, is_refusal)
            forest.append(root_node)

    print("Loaded " + str(len(forest)) + " rows from " + filename)
    return forest

def validate_csv_format(filename):
    """Check if the given CSV file is in the correct format."""
    
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        
        # 1. Validate header columns
        headers = reader.fieldnames
        required_columns = {'User', 'Assistant', 'Refusal'}
        
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
            
            if row['Refusal'] not in valid_is_refusal_values:
                print(f"Error: Invalid value '{row['refusal']}' in 'refusal' column for prompt '{row['prompt']}' on row {row_num}.")
                return False

    return True

def get_response(prompt_text):
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt_text}], temperature=0.8)
    return response.choices[0].message.content

def evolve(node):
    """Evolve the current node, return node to add as a new root node"""

    # Evolve node using depth evolution prompts
    for prompt_template in DEPTH_EVOLUTION_PROMPTS:
        prompt_text = prompt_template.format(prompt=node.user_prompt)
        response_text = get_response(prompt_text)  # Assuming you have a function `get_response` that talks to OpenAI API
        
        # Check if the evolved prompt should be pruned
        if not should_prune(response_text, node):
            # If not pruned, then create a new child node and add to the tree
            new_node = Node(system_prompt=node.system_prompt, user_prompt=response_text, assistant_response="", parent=node)
            node.children.append(new_node)

    # Evolve node using breadth evolution prompt
    prompt_text = BREADTH_EVOLUTION_PROMPT.format(prompt=node.user_prompt)
    response_text = get_response(prompt_text)
    
    # Check if the evolved prompt should be pruned
    if not should_prune(response_text, node):
        # If not pruned, then create a new child node and add to the tree
        new_node = Node(system_prompt=node.system_prompt, user_prompt=response_text, assistant_response="", parent=node)
        return new_node
    

def get_leaf_nodes(node):
    """Recursively get all leaf nodes."""
    if not node.children:
        return [node]
    leaves = []
    for child in node.children:
        leaves.extend(get_leaf_nodes(child))
    return leaves

def print_tree(node, indent=""):
    print(indent + str(node.user_prompt))
    for child in node.children:
        print_tree(child, indent + "  ")

def forest_stats(forest):
    """
    Calculate and return the number of trees and total nodes in the forest.
    """
    trees = len(forest)  # Each root node in the forest is a tree.
    
    def count_nodes(node):
        """
        Recursively count the number of nodes in the subtree rooted at node.
        """
        total = 1  # Include the current node.
        for child in node.children:
            total += count_nodes(child)
        return total
    
    nodes = sum(count_nodes(root) for root in forest)

    return trees, nodes

def main():
    parser = argparse.ArgumentParser(description='Evolve prompts using GPT-4 based on a CSV input.')
    parser.add_argument('csv_file', type=str, help='Path to the CSV file containing the prompts to evolve.')
    
    # Set default value for output_file to 'output.csv'
    parser.add_argument('output_file', type=str, nargs='?', default='output.csv', 
                        help='Path to the output file where results will be saved. Defaults to "output.csv".')
    
    # Option to validate the input csv and exit
    parser.add_argument('--validate', action='store_true', help='Check if the CSV is in the correct format and then exit.')

    # Optional argument for the number of epochs, defaults to 4
    parser.add_argument('--epochs', type=int, default=4, help='Number of epochs to evolve the leaf nodes. Defaults to 4.')


    args = parser.parse_args()
    
    if args.validate:
        if validate_csv_format(args.csv_file):
            print("CSV format is valid.")
        else:
            print("CSV format is not valid. Please check the file.")
        return  # Exit after validation
    
    forest = load_forest_from_csv(args.csv_file)

    print("Evolving prompts from " + args.csv_file + " for " + str(args.epochs) + " epochs.")

    # Evolving for the specified number of epochs
    for epoch in range(args.epochs):
        print('Evolving epoch #' + str(epoch + 1))
        all_leaf_nodes = []
        for root in forest:
            all_leaf_nodes.extend(get_leaf_nodes(root))
        
        leaves_added = 0
        root_nodes_added = 0
        
        # Use tqdm to wrap around the leaf nodes iteration
        for leaf in tqdm(all_leaf_nodes, desc=f"Epoch {epoch+1} Progress", ncols=100):
            new_root = evolve(leaf)
            if new_root:
                forest.append(new_root)
                root_nodes_added += 1
            leaves_added += len(leaf.children)
        
        # Print stats of the current forest and the added leaves and root nodes
        trees, nodes = forest_stats(forest)
        print(f"\nTotal Trees in Forest: {trees}, Total Nodes in Forest: {nodes}")
        print(f"Leaves Added in Epoch {epoch+1}: {leaves_added}")
        print(f"Root Nodes Added in Epoch {epoch+1}: {root_nodes_added}")



if __name__ == "__main__":
    main()
