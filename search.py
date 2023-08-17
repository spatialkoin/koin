import os
import pickle
import re

class DocumentIndex:
    def __init__(self, index_file_path):
        self.index_file_path = index_file_path
        self.index = {}

        if os.path.exists(self.index_file_path):
            with open(self.index_file_path, 'rb') as index_file:
                self.index = pickle.load(index_file)

    def search_by_string(self, search_string):
        matching_files = [file_name for file_name, data in self.index.items() if self._string_in_file(search_string, data['content'])]
        return matching_files

    def _string_in_file(self, search_string, model_content):
        escaped_search_string = re.escape(search_string)
        pattern = re.compile(escaped_search_string, re.IGNORECASE)
        match = re.search(pattern, model_content)
        return match is not None

# Initialize the DocumentIndex with the existing index data
index = DocumentIndex('document_index.pkl')

model_directory = '../models'  # Replace with the actual directory path for models

search_string = "hello"  # Replace this with the string you want to search for

# Search within example_models
for filename, data in index.index.items():
    model_name = data.get('model_name', '')
    if model_name == 'example_model':
        content = data.get('content', '')
        if re.search(search_string, content, re.IGNORECASE):
            print(f"Matching content found in file: {filename}")

print("Model search within example_models completed.")
