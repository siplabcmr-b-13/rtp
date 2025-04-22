from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Calorie Calculator</title>
  <style>
    /* Global Reset & Box Sizing */
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    /* Full-screen gradient background with centered container */
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #74ebd5, #acb6e5);
      height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
    }

    /* Container styling with card look and slide-in animation */
    .container {
      background: #fff;
      width: 400px;
      padding: 2rem;
      border-radius: 15px;
      box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
      animation: slideIn 1s ease-out;
    }

    @keyframes slideIn {
      0% {
        opacity: 0;
        transform: translateY(50px);
      }
      100% {
        opacity: 1;
        transform: translateY(0);
      }
    }

    h1 {
      text-align: center;
      margin-bottom: 1.5rem;
      font-size: 2em;
      color: #333;
    }

    /* Form Styling */
    form {
      display: flex;
      flex-direction: column;
    }

    label {
      margin: 0.5rem 0 0.2rem;
      font-weight: bold;
      color: #555;
    }

    input, select {
      padding: 0.75rem;
      margin-bottom: 1rem;
      border: 2px solid #ddd;
      border-radius: 8px;
      font-size: 1em;
      transition: border-color 0.3s, transform 0.3s;
    }

    input:focus, select:focus {
      outline: none;
      border-color: #74ebd5;
      transform: scale(1.02);
    }

    /* Remove spinner arrows in Chrome, Safari, Edge, Opera */
    input[type=number]::-webkit-outer-spin-button,
    input[type=number]::-webkit-inner-spin-button {
      -webkit-appearance: none;
      margin: 0;
    }

    /* Remove spinner arrows in Firefox */
    input[type=number] {
      -moz-appearance: textfield;
    }

    /* Button Styling with Gradient and Animations */
    button {
      padding: 0.75rem;
      font-size: 1em;
      background: linear-gradient(45deg, #74ebd5, #acb6e5);
      color: #fff;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      transition: transform 0.2s, box-shadow 0.2s;
      position: relative;
      overflow: hidden;
    }

    button:hover {
      transform: scale(1.05);
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }

    button:active {
      transform: scale(0.98);
    }

    /* Result Display with Fade-In */
    #result {
      margin-top: 1.5rem;
      font-size: 1.2em;
      text-align: center;
      opacity: 0;
      animation: fadeIn 1s forwards;
      animation-delay: 0.5s;
    }

    @keyframes fadeIn {
      to {
        opacity: 1;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Calorie Calculator</h1>
    <form id="calorieForm">
      <label for="age">Age (years):</label>
      <input type="number" id="age" name="age" required>
      
      <label for="weight">Weight (kg):</label>
      <input type="number" id="weight" name="weight" required>
      
      <label for="height">Height (cm):</label>
      <input type="number" id="height" name="height" required>
      
      <label for="gender">Gender:</label>
      <select id="gender" name="gender" required>
        <option value="male">Male</option>
        <option value="female">Female</option>
      </select>
      
      <label for="activity">Activity Level:</label>
      <select id="activity" name="activity" required>
        <option value="sedentary">Sedentary</option>
        <option value="lightly active">Lightly Active</option>
        <option value="moderately active">Moderately Active</option>
        <option value="very active">Very Active</option>
        <option value="extra active">Extra Active</option>
      </select>
      
      <button type="submit">Calculate Calories</button>
    </form>
    <div id="result"></div>
  </div>
  <script>
    document.getElementById('calorieForm').addEventListener('submit', function(e) {
      e.preventDefault();
      
      const age = document.getElementById('age').value;
      const weight = document.getElementById('weight').value;
      const height = document.getElementById('height').value;
      const gender = document.getElementById('gender').value;
      const activity = document.getElementById('activity').value;
      
      fetch('/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ age, weight, height, gender, activity })
      })
      .then(response => response.json())
      .then(data => {
        document.getElementById('result').innerText = 'Daily Calorie Requirement: ' + data.calories + ' calories';
      })
      .catch(error => console.error('Error:', error));
    });
  </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html)

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    age = float(data.get('age', 0))
    weight = float(data.get('weight', 0))
    height = float(data.get('height', 0))
    gender = data.get('gender', 'male').lower()
    activity_level = data.get('activity', 'sedentary').lower()

    # Calculate BMR using the Mifflin-St Jeor Equation
    if gender == 'male':
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

    # Activity factors:
    activity_factors = {
        'sedentary': 1.2,
        'lightly active': 1.375,
        'moderately active': 1.55,
        'very active': 1.725,
        'extra active': 1.9
    }
    factor = activity_factors.get(activity_level, 1.2)
    calories = bmr * factor

    return jsonify({'calories': round(calories, 2)})

if __name__ == '__main__':
    app.run(debug=True)
