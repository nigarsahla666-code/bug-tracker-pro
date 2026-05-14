from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# Ye list me sare bugs store honge
bugs_list = []
bug_id_counter = 1

@app.route('/')
def home():
    return render_template('index.html', bugs=bugs_list)

@app.route('/submit', methods=['POST'])
def submit():
    global bug_id_counter
    title = request.form['title']
    desc = request.form['description']
    
    # Naya bug list me add kar diya
    bugs_list.append({
        'id': bug_id_counter,
        'title': title,
        'description': desc,
        'status': 'Pending'  # Default status
    })
    bug_id_counter += 1
    
    return redirect('/')  # Wapas home page pe bhej do
@app.route('/delete/<int:bug_id>')
def delete_bug(bug_id):
    global bugs_list
    bugs_list = [bug for bug in bugs_list if bug['id'] != bug_id]
    return redirect('/')

@app.route('/status/<int:bug_id>/<new_status>')
def update_status(bug_id, new_status):
    for bug in bugs_list:
        if bug['id'] == bug_id:
            bug['status'] = new_status
            break
    return redirect('/')
@app.route('/edit/<int:bug_id>')
def edit_bug(bug_id):
    bug_to_edit = None
    for bug in bugs_list:
        if bug['id'] == bug_id:
            bug_to_edit = bug
            break
    return render_template('edit.html', bug=bug_to_edit)

@app.route('/update/<int:bug_id>', methods=['POST'])
def update_bug(bug_id):
    for bug in bugs_list:
        if bug['id'] == bug_id:
            bug['title'] = request.form['title']
            bug['description'] = request.form['description']
            break
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)