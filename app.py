import streamlit as st
import pickle
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# Load the model and scaler
@st.cache_resource
def load_model():
    try:
        with open('model.pkl', 'rb') as f:
            model = pickle.load(f)
        with open('scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        return model, scaler
    except FileNotFoundError:
        st.error("Model files not found. Please ensure 'model.pkl' and 'scaler.pkl' are in the same directory.")
        st.stop()

model, scaler = load_model()

# Set page configuration
st.set_page_config(
    page_title="Diabetes Risk Predictor",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .risk-high {
        background: linear-gradient(135deg, #ff6b6b, #ee5a24);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    
    .risk-low {
        background: linear-gradient(135deg, #51cf66, #40c057);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    
    .info-box {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .sidebar-info {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🩺 Diabetes Risk Predictor</h1>
    <p>Advanced AI-powered health assessment tool</p>
</div>
""", unsafe_allow_html=True)

# Sidebar with information
with st.sidebar:
    st.markdown("### 📋 About This Tool")
    st.markdown("""
    <div class="sidebar-info">
    This AI-powered tool uses machine learning to assess your diabetes risk based on key health indicators.
    
    <b>Important:</b> This is a screening tool only and should not replace professional medical advice.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Health Parameter Guidelines")
    
    with st.expander("📈 Normal Ranges"):
        st.markdown("""
        - **Glucose**: 70-100 mg/dL (fasting)
        - **Blood Pressure**: <120/80 mmHg
        - **BMI**: 18.5-24.9 (normal weight)
        - **Insulin**: 2.6-24.9 μIU/mL
        """)
    
    with st.expander("⚠️ Risk Factors"):
        st.markdown("""
        - Age over 45
        - Family history of diabetes
        - Overweight (BMI ≥25)
        - Physical inactivity
        - High blood pressure
        """)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📝 Enter Your Health Parameters")
    
    # Create input form with better organization
    with st.form("diabetes_prediction_form"):
        # Organize inputs in columns
        input_col1, input_col2 = st.columns(2)
        
        with input_col1:
            pregnancies = st.number_input(
                "Number of Pregnancies",
                min_value=0,
                max_value=20,
                step=1,
                help="Number of times pregnant"
            )
            
            glucose = st.number_input(
                "Glucose Level (mg/dL)",
                min_value=0,
                max_value=300,
                value=120,
                help="Plasma glucose concentration"
            )
            
            bp = st.number_input(
                "Blood Pressure (mmHg)",
                min_value=0,
                max_value=200,
                value=80,
                help="Diastolic blood pressure"
            )
            
            skin_thickness = st.number_input(
                "Skin Thickness (mm)",
                min_value=0,
                max_value=100,
                value=20,
                help="Triceps skin fold thickness"
            )
        
        with input_col2:
            insulin = st.number_input(
                "Insulin Level (μIU/mL)",
                min_value=0,
                max_value=500,
                value=80,
                help="2-Hour serum insulin"
            )
            
            bmi = st.number_input(
                "BMI (Body Mass Index)",
                min_value=10.0,
                max_value=60.0,
                value=25.0,
                format="%.1f",
                help="Body mass index (weight in kg/(height in m)^2)"
            )
            
            dpf = st.number_input(
                "Diabetes Pedigree Function",
                min_value=0.0,
                max_value=3.0,
                value=0.5,
                format="%.3f",
                help="Diabetes pedigree function"
            )
            
            age = st.number_input(
                "Age (years)",
                min_value=18,
                max_value=120,
                value=30,
                step=1,
                help="Age in years"
            )
        
        # Predict button
        submitted = st.form_submit_button("🔍 Analyze Diabetes Risk")
        
        if submitted:
            # Prepare the data with proper feature names
            feature_names = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 
                           'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
            
            input_data = pd.DataFrame([[pregnancies, glucose, bp, skin_thickness, insulin, bmi, dpf, age]], 
                                    columns=feature_names)
            
            # Transform the data
            input_scaled = scaler.transform(input_data)
            
            # Prediction with error handling
            try:
                prediction = model.predict(input_scaled)[0]
                prediction_proba = model.predict_proba(input_scaled)[0]
                
                # Display results
                st.markdown("---")
                st.markdown("### 📊 Analysis Results")
                
                if prediction == 1:
                    risk_percentage = prediction_proba[1] * 100
                    st.markdown(f"""
                    <div class="risk-high">
                        ⚠️ HIGH RISK DETECTED<br>
                        Risk Level: {risk_percentage:.1f}%<br>
                        Recommendation: Please consult a healthcare professional
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    risk_percentage = prediction_proba[0] * 100
                    st.markdown(f"""
                    <div class="risk-low">
                        ✅ LOW RISK DETECTED<br>
                        Safety Level: {risk_percentage:.1f}%<br>
                        Recommendation: Maintain healthy lifestyle
                    </div>
                    """, unsafe_allow_html=True)
                
                # Risk visualization
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = prediction_proba[1] * 100,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Diabetes Risk Level (%)"},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "#667eea"},
                        'steps': [
                            {'range': [0, 30], 'color': "#51cf66"},
                            {'range': [30, 70], 'color': "#ffd43b"},
                            {'range': [70, 100], 'color': "#ff6b6b"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 50
                        }
                    }
                ))
                
                fig.update_layout(
                    height=300,
                    margin=dict(l=20, r=20, t=40, b=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Additional insights
                st.markdown("### 📋 Your Health Parameter Analysis")
                
                # Create comparison chart
                user_values = [pregnancies, glucose, bp, skin_thickness, insulin, bmi, dpf, age]
                normal_ranges = [2, 100, 80, 20, 80, 23, 0.5, 35]  # Approximate normal values
                
                comparison_df = pd.DataFrame({
                    'Parameter': ['Pregnancies', 'Glucose', 'Blood Pressure', 'Skin Thickness', 
                                'Insulin', 'BMI', 'Diabetes Pedigree', 'Age'],
                    'Your Value': user_values,
                    'Reference': normal_ranges
                })
                
                # Create bar chart for comparison
                fig_comparison = px.bar(
                    comparison_df, 
                    x='Parameter', 
                    y=['Your Value', 'Reference'],
                    title='Your Values vs Reference Values',
                    barmode='group',
                    color_discrete_map={'Your Value': '#667eea', 'Reference': '#51cf66'}
                )
                
                fig_comparison.update_layout(
                    height=400,
                    xaxis_tickangle=-45,
                    margin=dict(l=20, r=20, t=40, b=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                
                st.plotly_chart(fig_comparison, use_container_width=True)
                
            except Exception as e:
                st.error(f"An error occurred during prediction: {str(e)}")
                st.info("Please check your input values and try again.")

with col2:
    st.markdown("### 📈 Health Insights")
    
    # BMI Calculator and Status
    if 'bmi' in locals():
        st.markdown("#### BMI Status")
        if bmi < 18.5:
            bmi_status = "Underweight"
            bmi_color = "#74c0fc"
        elif bmi < 25:
            bmi_status = "Normal"
            bmi_color = "#51cf66"
        elif bmi < 30:
            bmi_status = "Overweight"
            bmi_color = "#ffd43b"
        else:
            bmi_status = "Obese"
            bmi_color = "#ff6b6b"
        
        st.markdown(f"""
        <div style="background: {bmi_color}; color: white; padding: 1rem; border-radius: 10px; text-align: center; margin: 1rem 0;">
            <b>BMI: {bmi:.1f}</b><br>
            Status: {bmi_status}
        </div>
        """, unsafe_allow_html=True)
    
    # Health tips
    st.markdown("#### 💡 Health Tips")
    st.markdown("""
    <div class="info-box">
    <b>Prevention Tips:</b><br>
    • Maintain healthy weight<br>
    • Exercise regularly (30 min/day)<br>
    • Eat balanced diet<br>
    • Monitor blood sugar<br>
    • Stay hydrated<br>
    • Get adequate sleep
    </div>
    """, unsafe_allow_html=True)
    
    # Warning message
    st.markdown("#### ⚠️ Medical Disclaimer")
    st.markdown("""
    <div class="info-box">
    <b>Important:</b> This tool is for educational purposes only. 
    Always consult with healthcare professionals for medical advice, 
    diagnosis, or treatment.
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; margin-top: 2rem;">
    <p>🔬 Powered by Machine Learning | 💻 Built with Streamlit</p>
    <p><small>For educational and screening purposes only</small></p>
</div>
""", unsafe_allow_html=True)