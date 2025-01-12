import time

from views import generate_xlsx

def download_and_time_xlsx():
    start_time = time.time()
    file_path = generate_xlsx()
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    if file_path:
        print(f"File downloaded successfully: {file_path}")
        print(f"Time taken: {elapsed_time:.2f} seconds")
    else:
        print("Failed to download the file.")
    
    return file_path, elapsed_time


if __name__ == "__main__":
    download_and_time_xlsx()
