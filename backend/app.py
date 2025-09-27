from flask import Flask, render_template_string, request, redirect, url_for, flash, session
import os
from auth import login_required, login_page, logout

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this in production

PROJECTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'projects')

# Serve static assets (CSS, JS, images) for live preview
@app.route('/assets/<path:filename>')
def serve_assets(filename):
    assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
    file_path = os.path.join(assets_dir, filename)
    if not os.path.isfile(file_path):
        return "File not found", 404
    # Guess MIME type for proper serving
    import mimetypes
    mime_type, _ = mimetypes.guess_type(file_path)
    with open(file_path, 'rb') as f:
        return f.read(), 200, {'Content-Type': mime_type or 'application/octet-stream'}
from flask import Flask, render_template_string, request, redirect, url_for, flash, session
import os
from auth import login_required, login_page, logout

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this in production

PROJECTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'projects')

@app.route('/')
@login_required
def index():
    files = [f for f in os.listdir(PROJECTS_DIR) if f.endswith('.html')]
    return render_template_string('''
        <h2>Edit Project Pages</h2>
        <ul>
        {% for file in files %}
            <li><a href="{{ url_for('edit_page', filename=file) }}">{{ file }}</a></li>
        {% endfor %}
        </ul>
            <p><a href="{{ url_for('logout_view') }}">Logout</a></p>
    ''', files=files)

@app.route('/edit/<filename>', methods=['GET', 'POST'])
@login_required
def edit_page(filename):
        file_path = os.path.join(PROJECTS_DIR, filename)
        if request.method == 'POST':
                new_content = request.form.get('content', '')
                with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                flash('Page updated!')
                return redirect(url_for('edit_page', filename=filename))
        with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        return render_template_string('''
            <h2>Editing {{ filename }}</h2>
            <div>
                <h3>Live Preview</h3>
                <iframe id="previewFrame" src="/projects/{{ filename }}" width="100%" height="400" style="border:1px solid #ccc;"></iframe>
            </div>
            <form id="editForm" method="post">
                <textarea name="content" rows="25" cols="100">{{ content }}</textarea><br>
                <button type="submit">Save</button>
            </form>
            <p><a href="{{ url_for('index') }}">Back to list</a></p>
            <p><a href="{{ url_for('logout_view') }}">Logout</a></p>
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    <ul>
                    {% for message in messages %}
                        <li>{{ message }}</li>
                    {% endfor %}
                    </ul>
                {% endif %}
            {% endwith %}
            <script>
                document.getElementById('editForm').addEventListener('submit', function(e) {
                    e.preventDefault();
                    var form = e.target;
                    var data = new FormData(form);
                    fetch(form.action || window.location.pathname, {
                        method: 'POST',
                        body: data
                    }).then(function(response) {
                        if (response.redirected) {
                            window.location.href = response.url;
                        } else {
                            document.getElementById('previewFrame').contentWindow.location.reload();
                        }
                    });
                });
            </script>
        ''', filename=filename, content=content)

@app.route('/login', methods=['GET', 'POST'])
def login():
    return login_page()

@app.route('/logout')
def logout_view():
    return logout()


# Serve project HTML files for live preview
@app.route('/projects/<path:filename>')
@login_required
def serve_project_file(filename):
    file_path = os.path.join(PROJECTS_DIR, filename)
    if not os.path.isfile(file_path):
        return "File not found", 404
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

if __name__ == '__main__':
    app.run(debug=True, port=5050)
