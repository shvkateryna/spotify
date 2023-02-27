from flask import Flask, render_template, request
from map_music import map_creator
app = Flask(__name__)

@app.route('/', methods = ['POST', 'GET'])

def hello():
    return render_template('search.html')

@app.route('/result', methods = ['POST', 'GET'])
def result():
    output = request.form.get('name')
    if request.method == 'POST':
        map_creator(output)
    return render_template('map2.html')

if __name__ == '__main__':
    app.run(debug=True)
