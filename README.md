📊 Luminant BI: Automated Business Intelligence Tool
Luminant BI is an intelligent data analytics dashboard designed to transform raw CSV data into actionable insights instantly. Built with Streamlit and Python, this tool automates the Exploratory Data Analysis (EDA) process, generates natural language insights, and provides professional PDF reports for stakeholders.

🚀 Key Features
Secure Authentication: Integrated with Firebase for secure User Login and Sign-Up, including a "Remember Me" session persistence.

Automated EDA: One-click analysis of dataset dimensions, data types, missing values, and statistical summaries.

Rule-Based NLG Insights: Automatically detects patterns and correlations (Strong/Moderate) and describes them using Natural Language Generation (NLG) logic.

Interactive Visualizations: Dynamic histograms, box plots, and scatter plots powered by Plotly and Seaborn.

Professional PDF Reporting: Generates a structured PDF report containing dataset metrics, automated insights, and visual distributions.

Data Cleaning: Built-in tools to handle duplicate records and missing value imputation (Mean, Median, Mode).

🛠️ Tech Stack
Frontend/App Framework: Streamlit

Data Processing: Pandas, NumPy

Visualization: Plotly Express, Seaborn, Matplotlib

PDF Generation: ReportLab

Authentication: Google Identity Toolkit API (Firebase)

📂 Project Structure
Plaintext
├── app.py              # Main Streamlit application code
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
⚙️ Installation & Setup
Clone the Repository:

git clone https://github.com/devgulati23/Luminant-BI.git
cd Luminant-BI

Bash
pip install -r requirements.txt
Run the Application:

Bash
streamlit run app.py
📊 Sample Output: PDF Report
The tool generates a multi-page PDF report:

Page 1: Dataset Overview Table & Correlation Insights.

Page 2: Data Distributions & Relationships.

Page 3: Heatmap Feature Correlation Matrix.

👩‍💻 Developed By

Dev Gulati, BCA Student (2023-2026) 

Mehak , BCA Student (2023-2026)

Daksh Gulati , BCA Student (2023-2026)

Don Bosco Institute of Technology, Okhla

(Guru Gobind Singh Indraprastha University)
