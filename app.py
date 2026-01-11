from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML = '''
<h2>Login to the System</h2>
<form method="post">
    <input name="username" placeholder="Username" required><br><br>
    <input name="password" type="password" placeholder="Password" required><br><br>
    <button type="submit">Login</button>
</form>
'''

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'pass123':
            return '<h2>Login successful! Welcome to the dashboard.</h2>'
        else:
            return '<h2 style="color:red;">Invalid credentials. Please try again.</h2>' + HTML
    return HTML

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)