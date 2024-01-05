from flask import Flask, render_template, request

app = Flask(__name__)

# Initialize a dictionary to store slider values
slider_values = {}

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/update_variable', methods=['POST'])
def update_variable():
    global slider_values
    data = request.get_json()
    slider_id = data['id']
    slider_value = int(data['value'])
    slider_values[slider_id] = slider_value
    return "Variable updated successfully!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)