import os
import subprocess
from flask import Flask, render_template_string, request, send_file

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp/iso_chd_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>From ISO To CHD By Alanabrelek</title>
    <style>
        body {
            background-color: #0B0F19;
            color: #00FF66;
            font-family: 'Courier New', monospace;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .card {
            background-color: #1F2937;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 0 20px rgba(0, 255, 102, 0.2);
            width: 100%;
            max-width: 400px;
            text-align: center;
        }
        h1 {
            font-size: 22px;
            margin-bottom: 5px;
        }
        .subtitle {
            font-size: 12px;
            color: #9CA3AF;
            margin-bottom: 25px;
        }
        input[type="file"] {
            display: none;
        }
        .file-upload-btn {
            background-color: #0B0F19;
            color: #00FF66;
            border: 2px dashed #00FF66;
            padding: 12px;
            display: block;
            border-radius: 6px;
            cursor: pointer;
            margin-bottom: 20px;
            transition: 0.3s;
        }
        .file-upload-btn:hover {
            background-color: #00FF66;
            color: #0B0F19;
        }
        button[type="submit"] {
            background-color: #00FF66;
            color: #0B0F19;
            border: none;
            padding: 12px 20px;
            font-weight: bold;
            border-radius: 6px;
            cursor: pointer;
            width: 100%;
            font-family: 'Courier New', monospace;
        }
        button[type="submit"]:hover {
            opacity: 0.9;
        }
        .log-box {
            margin-top: 20px;
            background: #0B0F19;
            padding: 10px;
            text-align: left;
            font-size: 11px;
            color: #EF4444;
            border-radius: 4px;
            word-break: break-all;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>From ISO To CHD</h1>
        <div class="subtitle">By Alanabrelek</div>
        
        <form method="POST" enctype="multipart/form-data">
            <label class="file-upload-btn">
                Wybierz plik ISO
                <input type="file" name="file" accept=".iso" required onchange="updateFileName(this)">
            </label>
            <div id="file-name" style="font-size: 11px; color: #9CA3AF; margin-bottom: 15px;">Nie wybrano pliku</div>
            <button type="submit">KONWERTUJ NA CHD</button>
        </form>

        {% if error %}
        <div class="log-box">BŁĄD: {{ error }}</div>
        {% endif %}
    </div>

    <script>
        function updateFileName(input) {
            const fileNameBox = document.getElementById('file-name');
            if (input.files && input.files[0]) {
                fileNameBox.textContent = "Wybrano: " + input.files[0].name;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            return render_template_string(HTML_TEMPLATE, error="Nie wybrano pliku!")
        
        if not file.filename.lower().endswith('.iso'):
            return render_template_string(HTML_TEMPLATE, error="To nie jest plik ISO!")

        iso_path = os.path.join(UPLOAD_FOLDER, file.filename)
        chd_filename = os.path.splitext(file.filename)[0] + ".chd"
        chd_path = os.path.join(UPLOAD_FOLDER, chd_filename)
        
        file.save(iso_path)

        try:
            cmd = ["chdman", "createcd", "-i", iso_path, "-o", chd_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                return render_template_string(HTML_TEMPLATE, error=f"Błąd chdman: {result.stderr}")
            
            return send_file(chd_path, as_attachment=True)
            
        except Exception as e:
            return render_template_string(HTML_TEMPLATE, error=str(e))
        finally:
            if os.path.exists(iso_path):
                os.remove(iso_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
  
