import os
import pickle
import re
import koin
import time


document_index = '../document_index.pkl'
while True:
    # Sample index data structure
    sample_index_data = {
        # Add more files if needed
    }

    # Save the sample index data to a file
    with open(document_index, 'wb') as index_file:
        pickle.dump(sample_index_data, index_file)

    print("Sample index data saved to 'document_index.pkl'.")

    # Example model (replace this with your actual model instance)
    example_model = {'model_data': 'example model data'}

    index = koin.DocumentIndex(document_index, '../models')


    with open(document_index, 'rb') as index_file:
        index_data = pickle.load(index_file)
    print(index_data)


    text_files_directory = '../files'  # Replace this with the actual directory path
    model_name = 'example_model'  # Replace this with a meaningful model name

    for filename in os.listdir(text_files_directory):
        if filename.endswith('.txt'):
            file_path = os.path.join(text_files_directory, filename)
            with open(file_path, 'r') as file:
                file_content = file.read()

            index.add_document(model_name, filename, example_model, file_content)

    time.sleep(2)
