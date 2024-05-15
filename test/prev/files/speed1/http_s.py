from flask import Flask, request, jsonify
import time

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    start_time = time.time()

    file_size = int(request.headers['Content-Length'])
    print(f"Receiving file of size {file_size} bytes")

    file_data = request.data

    # with open("received_file", "wb") as file:
    #     file.write(file_data)

    end_time = time.time()
    print(f"Received file in {end_time - start_time} seconds")

    return jsonify({"message": "File received successfully"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
