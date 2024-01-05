from flask import Flask, render_template, request

app = Flask(__name__)

# Initialize a variable to store the slider value
slider_value = 50

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/update_variable', methods=['POST'])
def update_variable():
    global slider_value
    data = request.get_json()
    slider_value = int(data['value'])
    print("Slider value updated to:", slider_value)
    return "Variable updated successfully!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)