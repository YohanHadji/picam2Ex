from flask import Flask, render_template, request

app = Flask(__name__)

# Initialize a dictionary to store input values
input_values = {}

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/update_variable', methods=['POST'])
def update_variable():
    global input_values
    data = request.get_json()
    input_id = data['id']
    input_value = int(data['value'])

    # Check if the value has changed
    if input_values.get(input_id) != input_value:
        print(f"Value for {input_id} changed to {input_value}")

    # Update the input_values dictionary
    input_values[input_id] = input_value

    return "Variable updated successfully!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)