import os
from flask import Flask, request, render_template_string
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)

# Google Drive API Setup
SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = 'credentials.json'
PARENT_FOLDER_ID = '1meA7NqTIcBbkT1ELUn586aiOXkP6WnyH'

def authenticate():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

# HTML Frontend UI for SJVNSPP
html_template = '''
<!doctype html>
<html>
<head><title>SJVNSPP - File Uploader</title></head>
<body style="font-family: Arial; margin: 50px; background-color: #f4f7f6;">
    <div style="max-width: 500px; background: white; padding: 30px; border-radius: 8px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1);">
        <h2>SJVNSPP - Direct Drive Uploader</h2>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file" required style="margin-bottom: 15px;"><br>
            <button type="submit" style="padding: 10px 20px; background: #007BFF; color: white; border: none; border-radius: 4px; cursor: pointer;">Upload to Drive</button>
        </form>
        <p style="margin-top: 15px; font-weight: bold; color: green;">{{ message }}</p>
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    message = ""
    if request.method == 'POST':
        if 'file' not in request.files:
            message = 'No file part'
        else:
            file = request.files['file']
            if file.filename == '':
                message = 'No selected file'
            else:
                file_path = os.path.join('/tmp', file.filename)
                file.save(file_path)
                
                try:
                    service = authenticate()
                    file_metadata = {
                        'name': file.filename,
                        'parents': [PARENT_FOLDER_ID]
                    }
                    media = MediaFileUpload(file_path, resumable=True)
                    uploaded_file = service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id'
                    ).execute()
                    message = f"File successfully uploaded! (ID: {uploaded_file.get('id')})"
                except Exception as e:
                    message = f"Upload failed: {str(e)}"
                finally:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        
    return render_template_string(html_template, message=message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)