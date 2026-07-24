from flask import request, Flask, send_from_directory, render_template, redirect, url_for, session  
import mysql.connector
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
from xgboost import XGBClassifier
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import time
import warnings
warnings.filterwarnings('ignore')

# Fix for numpy compatibility
if not hasattr(np, 'int'):
    np.int = int
if not hasattr(np, 'float'):
    np.float = float
if not hasattr(np, 'bool'):
    np.bool = bool

app = Flask(__name__)

# MySQL connection setup
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Navya1711@",
    port=3307,#3306
    database='HeartDisease'
)
mycursor = mydb.cursor()

# MySQL query functions
def executionquery(query, values):
    mycursor.execute(query, values)
    mydb.commit()

def retrivequery1(query, values):
    mycursor.execute(query, values)
    return mycursor.fetchall()

def retrivequery2(query):
    mycursor.execute(query)
    return mycursor.fetchall()

# Load and prepare data
data = pd.read_csv('Cardiovascular_Disease_Dataset.csv')
data.drop("patientid", axis=1, inplace=True)

# Split X and y
X = data.drop("target", axis=1)
y = data["target"]

# Standardize numerical features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split into training/testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

# Train XGBoost model
xgb_clf = XGBClassifier(
    use_label_encoder=False, 
    eval_metric='logloss', 
    random_state=42,
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1
)
xgb_clf.fit(X_train, y_train)

# Feature names
feature_names = [
    'age', 'gender', 'chestpain', 'restingBP', 'serumcholestrol',
    'fastingbloodsugar', 'restingrelectro', 'maxheartrate',
    'exerciseangia', 'oldpeak', 'slope', 'noofmajorvessels'
]

# Routes for the web application
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about', methods=["GET", "POST"])
def about():
    return render_template('about.html')

@app.route('/home', methods=["GET", "POST"])
def home():
    return render_template('home.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form['email']
        password = request.form['password']
        confirmpassword = request.form['confirmpassword']
        
        if password == confirmpassword:
            query = "SELECT UPPER(email) FROM users"
            email_data = retrivequery2(query)
            email_data_list = []
            for i in email_data:
                email_data_list.append(i[0])
            
            if email.upper() not in email_data_list:
                query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
                values = (name, email, password)
                executionquery(query, values)
                return render_template('login.html', message="Successfully Registered!")
            
            return render_template('register.html', message="This email ID already exists!")
        
        return render_template('register.html', message="Confirm password does not match!")
    
    return render_template('register.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        
        query = "SELECT UPPER(email) FROM users"
        email_data = retrivequery2(query)
        email_data_list = []
        for i in email_data:
            email_data_list.append(i[0])

        if email.upper() in email_data_list:
            query = "SELECT UPPER(password) FROM users WHERE email = %s"
            values = (email,)
            password_data = retrivequery1(query, values)
            
            if password.upper() == password_data[0][0]:
                return redirect("/home")
            
            return render_template('login.html', message="Invalid Password!")
        
        return render_template('login.html', message="This email ID does not exist!")
    
    return render_template('login.html')

@app.route('/prediction', methods=["GET", "POST"])
def prediction():
    if request.method == 'POST':
        try:
            # Extract inputs
            age = float(request.form['age'])
            gender = float(request.form['gender'])
            chestpain = float(request.form['chestpain'])
            restingBP = float(request.form['restingBP'])
            serumcholestrol = float(request.form['serumcholestrol'])
            fastingbloodsugar = float(request.form['fastingbloodsugar'])
            restingrelectro = float(request.form['restingrelectro'])
            maxheartrate = float(request.form['maxheartrate'])
            exerciseangia = float(request.form['exerciseangia'])
            oldpeak = float(request.form['oldpeak'])
            slope = float(request.form['slope'])
            noofmajorvessels = float(request.form['noofmajorvessels'])

            # Validate input ranges
            if not (20 <= age <= 80):
                return render_template('prediction.html', 
                                     prediction="Error: Age must be between 20 and 80.")
            
            if gender not in [0, 1]:
                return render_template('prediction.html', 
                                     prediction="Error: Gender must be 0 (Female) or 1 (Male).")
            
            if chestpain not in [0, 1, 2, 3]:
                return render_template('prediction.html', 
                                     prediction="Error: Chest pain type must be 0, 1, 2, or 3.")
            
            if not (94 <= restingBP <= 200):
                return render_template('prediction.html', 
                                     prediction="Error: Resting BP must be between 94 and 200.")
            
            if not (0 <= serumcholestrol <= 602):
                return render_template('prediction.html', 
                                     prediction="Error: Serum cholesterol must be between 0 and 602.")
            
            if fastingbloodsugar not in [0, 1]:
                return render_template('prediction.html', 
                                     prediction="Error: Fasting blood sugar must be 0 or 1.")
            
            if restingrelectro not in [0, 1, 2]:
                return render_template('prediction.html', 
                                     prediction="Error: Resting ECG must be 0, 1, or 2.")
            
            if not (71 <= maxheartrate <= 202):
                return render_template('prediction.html', 
                                     prediction="Error: Max heart rate must be between 71 and 202.")
            
            if exerciseangia not in [0, 1]:
                return render_template('prediction.html', 
                                     prediction="Error: Exercise angina must be 0 or 1.")
            
            if not (0 <= oldpeak <= 6.2):
                return render_template('prediction.html', 
                                     prediction="Error: Oldpeak must be between 0 and 6.2.")
            
            if slope not in [0, 1, 2]:
                return render_template('prediction.html', 
                                     prediction="Error: Slope must be 0, 1, or 2.")
            
            if noofmajorvessels not in [0, 1, 2, 3]:
                return render_template('prediction.html', 
                                     prediction="Error: Number of major vessels must be 0, 1, 2, or 3.")

            # Create input data
            input_data = pd.DataFrame(
                [[age, gender, chestpain, restingBP, serumcholestrol,
                  fastingbloodsugar, restingrelectro, maxheartrate,
                  exerciseangia, oldpeak, slope, noofmajorvessels]],
                columns=feature_names
            )

            # Scale data
            input_data_scaled = scaler.transform(input_data)

            # Predict
            prediction_result = xgb_clf.predict(input_data_scaled)[0]
            prediction_proba = xgb_clf.predict_proba(input_data_scaled)[0]
            
            # Determine result
            if prediction_result == 0:
                predicted_class = '✅ Patient is NORMAL (No Heart Disease)'
                probability_score = prediction_proba[0] * 100
                result_color = 'success'
            else:
                predicted_class = '⚠️ Patient has HEART DISEASE'
                probability_score = prediction_proba[1] * 100
                result_color = 'danger'
            
            # Create feature importance visualization
            plt.figure(figsize=(12, 8))
            
            # Get feature importances
            importance_scores = xgb_clf.feature_importances_
            
            # Create DataFrame for sorting
            importance_df = pd.DataFrame({
                'Feature': feature_names,
                'Importance': importance_scores,
                'Value': input_data.iloc[0].values,
                'Scaled_Value': input_data_scaled[0]
            })
            
            # Sort by importance
            importance_df = importance_df.sort_values('Importance', ascending=True)
            
            # Create horizontal bar chart
            colors = []
            for val in importance_df['Scaled_Value']:
                if val > 1.0:
                    colors.append('#ff6b6b')  # Red for high positive
                elif val > 0:
                    colors.append('#ffa8a8')  # Light red
                elif val < -1.0:
                    colors.append('#4d96ff')  # Blue for high negative
                else:
                    colors.append('#a8c6ff')  # Light blue
            
            bars = plt.barh(importance_df['Feature'], importance_df['Importance'], color=colors)
            plt.xlabel('Importance Score', fontsize=12)
            plt.title('Feature Importance Analysis', fontsize=14, fontweight='bold')
            plt.grid(axis='x', alpha=0.3)
            
            # Add value labels on bars
            for i, (importance, value) in enumerate(zip(importance_df['Importance'], importance_df['Value'])):
                plt.text(importance + 0.001, i, f'{value:.1f}', va='center', fontsize=10)
            
            plt.tight_layout()
            
            # Save the plot
            uploads_dir = os.path.join('static', 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            
            filename = f"importance_{int(time.time())}.png"
            filepath = os.path.join(uploads_dir, filename)
            plt.savefig(filepath, bbox_inches='tight', dpi=100, facecolor='white')
            plt.close()

            image_path = f"uploads/{filename}"
            
            # Prepare detailed analysis for template
            top_features = []
            for idx, row in importance_df.iterrows():
                contribution = row['Scaled_Value'] * row['Importance']
                top_features.append({
                    'feature': row['Feature'],
                    'value': row['Value'],
                    'importance': round(row['Importance'], 4),
                    'contribution': round(contribution, 4),
                    'direction': 'Increases risk' if contribution > 0 else 'Decreases risk'
                })
            
            # Sort by absolute contribution for display
            top_features.sort(key=lambda x: abs(x['contribution']), reverse=True)
            
            # Risk factors analysis
            risk_factors = []
            protective_factors = []
            
            for feature in top_features:
                if feature['contribution'] > 0:
                    risk_factors.append(f"{feature['feature']} (contribution: {feature['contribution']:.4f})")
                else:
                    protective_factors.append(f"{feature['feature']} (contribution: {feature['contribution']:.4f})")

            return render_template('prediction.html', 
                                 prediction=predicted_class,
                                 probability=f"Confidence: {probability_score:.1f}%",
                                 shap_image=image_path,
                                 features=top_features[:6],  # Top 6 features
                                 risk_factors=risk_factors[:3],
                                 protective_factors=protective_factors[:3],
                                 result_color=result_color,
                                 show_results=True)

        except ValueError as ve:
            return render_template('prediction.html', 
                                 prediction=f"Input Error: {str(ve)}",
                                 show_results=False)
        
        except Exception as e:
            import traceback
            print(f"Error during prediction: {traceback.format_exc()}")
            return render_template('prediction.html', 
                                 prediction="System Error: Please try again later.",
                                 show_results=False)
    
    return render_template('prediction.html', show_results=False)

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    uploads_dir = os.path.join('static', 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    
    app.run(debug=True, port=5000)
    