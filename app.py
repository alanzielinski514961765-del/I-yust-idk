import os
import subprocess
import traceback
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
            max-width: 450px;
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
        .log-box {
            margin-top: 20px;
            background: #0B0F19;
            padding: 10px;
            text-align: left;
            font-size: 10px;
            color: #EF4444;
            border-radius: 4px;
            word-break: break-all;
            white-space: pre-wrap;
            max-height: 150px;
            overflow-y: auto;
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
        <div class="log-box">{{ error }}</div>
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
        iso_path = None
        chd_path = None
        try:
            file = request.files.get('file')
            if not file or file.filename == '':
                return render_template_string(HTML_TEMPLATE, error="BŁĄD: Nie wybrano pliku!")
            
            iso_path = os.path.join(UPLOAD_FOLDER, file.filename)
            chd_filename = os.path.splitext(file.filename)[0] + ".chd"
            chd_path = os.path.join(UPLOAD_FOLDER, chd_filename)
            
            # Bezpieczny zapis pliku w kawałkach, żeby nie wywalić pamięci serwera
            file.save(iso_path)

            # Uruchomienie konwersji chdman
            cmd = ["chdman", "createcd", "-i", iso_path, "-o", chd_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                error_msg = f"CHDMAN ERROR (Kod {result.returncode}):\n{result.stderr}\n{result.stdout}"
                return render_template_string(HTML_TEMPLATE, error=error_msg)
            
            if not os.path.exists(chd_path):
                return render_template_string(HTML_TEMPLATE, error="BŁĄD: Plik CHD nie został utworzony.")
            
            return send_file(chd_path, as_attachment=True)
            
        except Exception as e:
            full_error = traceback.format_exc()
            return render_template_string(HTML_TEMPLATE, error=f"PYTHON EXCEPTION:\n{full_error}")
        finally:
            # Czyszczenie pliku ISO po wszystkim
            if iso_path and os.path.exists(iso_path):
                try:
                    os.remove(iso_path)
                except:
                    pass
                
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    
