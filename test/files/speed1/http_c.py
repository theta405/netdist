import requests
import time

def client(file_path):
    url = 'http://mini.lan:5000/upload'
    files = {'file': open(file_path, 'rb')}
    start_time = time.time()
    response = requests.post(url, files=files)
    end_time = time.time()

    print(f"Server response: {response.json()['message']}")
    print(f"File transfer completed in {end_time - start_time} seconds")

def main():
    import sys

    if len(sys.argv) != 2:
        print("Usage: python script.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    client(file_path)

if __name__ == "__main__":
    main()
