from flask import Flask, request, redirect, url_for, render_template_string

app = Flask(__name__)

# 设置上传文件保存路径
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 创建文件上传表单
upload_form = '''
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <title>File Upload</title>
  </head>
  <body>
    <h1>Upload a File</h1>
    <form method="post" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="Upload">
    </form>
  </body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # 检查是否有文件被上传
        if 'file' not in request.files:
            return 'No file part'
        
        file = request.files['file']
        
        # 如果用户没有选择文件，浏览器提交空文件（没有文件名）
        if file.filename == '':
            return 'No selected file'
        
        # 分片读取文件并写入本地文件
        if file:
            filename = file.filename
            local_file_path = f"{app.config['UPLOAD_FOLDER']}/{filename}"
            
            with open(local_file_path, 'wb') as f:
                chunk_size = 1024
                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
            
            return 'File successfully uploaded and saved'
    
    return render_template_string(upload_form)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
