import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import os

# 1. Page Configuration
st.set_page_config(page_title="HR Management System", layout="wide")

# 2. Custom CSS for Blue & Green Theme with Shapes
st.markdown("""
<style>
    h1, h2, h3 {
        background: -webkit-linear-gradient(45deg, #0052cc, #00b359);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    div[data-testid="metric-container"] {
        background: linear-gradient(to right bottom, #ffffff, #e6f7ff);
        border: 2px solid #00b359;
        border-radius: 20px;
        padding: 15px;
        box-shadow: 3px 3px 15px rgba(0, 0, 0, 0.05);
    }
    
    section[data-testid="stSidebar"] {
        background-color: #f2fbfa;
        border-right: 3px solid #0052cc;
    }
    
    hr {
        border: 0;
        height: 2px;
        background-image: linear-gradient(to right, #0052cc, #00b359, #0052cc);
    }
</style>
""", unsafe_allow_html=True)

# 3. Data Loading Function
@st.cache_data
def load_data():
    return pd.read_csv("HR-Employee-Attrition.csv")

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}. Please ensure 'HR-Employee-Attrition_2.csv' is in the folder.")
    st.stop()

# 4. Sidebar Authentication
st.sidebar.title("Login Portal")
role = st.sidebar.selectbox("Select Your Role", ["Employee", "HR", "Admin"])
st.sidebar.divider()

# 5. Employee Dashboard
def show_employee_dashboard():
    st.title("Employee Portal")
    st.markdown("View your personal records, salary, and attendance details.")
    
    emp_ids = df['EmployeeNumber'].unique()
    
    st.sidebar.markdown("### User Selection")
    st.sidebar.markdown("**Choose Employee ID:**")
    selected_emp_id = st.sidebar.selectbox("Employee ID", emp_ids, label_visibility="collapsed")
    
    emp_data = df[df['EmployeeNumber'] == selected_emp_id].iloc[0]
    
    st.subheader(f"Welcome, Employee #{selected_emp_id}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Job Role", emp_data['JobRole'])
    col2.metric("Department", emp_data['Department'])
    col3.metric("Monthly Income", f"${emp_data['MonthlyIncome']:,}")
    
    st.divider()
    st.subheader("Personal Information")
    personal_info = emp_data[['Age', 'Gender', 'EducationField', 'YearsAtCompany', 'JobSatisfaction']]
    st.table(personal_info)

# 6. HR Dashboard
def show_hr_dashboard():
    st.title("HR Dashboard")
    st.markdown("Monitor departmental analytics and employee attrition.")
    
    st.sidebar.subheader("HR Data Filters")
    
    # Headings for HR Filters
    st.sidebar.markdown("**🏢 Filter by Department:**")
    dept = st.sidebar.multiselect("Department Filter", df['Department'].unique(), default=df['Department'].unique(), label_visibility="collapsed")
    
    filtered_df = df[df['Department'].isin(dept)]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Employees", len(filtered_df))
    col2.metric("Average Salary", f"${filtered_df['MonthlyIncome'].mean():,.0f}")
    
    if len(filtered_df) > 0:
        attr_rate = (len(filtered_df[filtered_df['Attrition'] == 'Yes']) / len(filtered_df)) * 100
    else:
        attr_rate = 0
    col3.metric("Attrition Rate", f"{attr_rate:.1f}%")
    
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        fig1 = px.histogram(filtered_df, x="JobRole", color="Attrition", barmode="group", 
                            color_discrete_sequence=['#00b359', '#0052cc'], title="Attrition Status by Role")
        fig1.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        fig2 = px.box(filtered_df, x="Department", y="MonthlyIncome", color="Department", title="Salary Distribution")
        fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True)

# 7. Admin Dashboard
def show_admin_dashboard():
    st.title("System Administrator Panel")
    
    # --- Dynamic Profile Picture Upload ---
    col_img, col_text = st.columns([1, 3])
    with col_img:
        st.info("Update Profile Picture")
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
        
        if uploaded_file is not None:
            img = Image.open(uploaded_file)
            st.image(img, caption="System Admin", use_container_width=True)
        else:
            image_path = "Profile.jpg"
            if os.path.exists(image_path):
                img = Image.open(image_path)
                st.image(img, caption="System Admin (Default)", use_container_width=True)
            else:
                st.warning("No image uploaded. Please upload a profile picture.")
            
    with col_text:
        st.markdown("### Welcome to the Master Control Room")
        st.markdown("You have full access to filter, analyze, and monitor all company data and employee records. Use the sidebar to apply master filters.")
    
    st.divider()
    
    # --- Admin Comprehensive Filters with Clear Headings ---
    st.sidebar.subheader("Master Data Filters")
    all_depts = df['Department'].unique()
    all_roles = df['JobRole'].unique()
    
    st.sidebar.markdown("**🏢 Filter by Department:**")
    selected_depts = st.sidebar.multiselect("Select Department", all_depts, default=all_depts, label_visibility="collapsed")
    
    st.sidebar.markdown("**💼 Filter by Job Role:**")
    selected_roles = st.sidebar.multiselect("Select Job Role", all_roles, default=all_roles, label_visibility="collapsed")
    
    admin_filtered_df = df[(df['Department'].isin(selected_depts)) & (df['JobRole'].isin(selected_roles))]
    
    # --- Admin Metrics ---
    t1, t2, t3, t4 = st.columns(4)
    t1.metric("Filtered Records", len(admin_filtered_df))
    t2.metric("Departments Active", admin_filtered_df['Department'].nunique())
    t3.metric("Job Roles Active", admin_filtered_df['JobRole'].nunique())
    t4.metric("Total Payroll", f"${admin_filtered_df['MonthlyIncome'].sum():,.0f}")
    
    st.divider()
    
    # --- Admin Advanced Analysis (Prettier Graphs) ---
    st.subheader("Deep Dive Analytics")
    ac1, ac2 = st.columns(2)
    
    with ac1:
        # Beautiful Donut Chart for Attrition
        attrition_counts = admin_filtered_df['Attrition'].value_counts().reset_index()
        attrition_counts.columns = ['Attrition', 'Count']
        fig_pie = px.pie(attrition_counts, names='Attrition', values='Count', 
                         title="Overall Attrition Ratio",
                         color_discrete_sequence=['#0052cc', '#00b359'],
                         hole=0.4)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with ac2:
        # Replaced Scatter Plot with a Clean Bar Chart
        avg_income = admin_filtered_df.groupby('JobRole')['MonthlyIncome'].mean().reset_index()
        fig_bar = px.bar(avg_income, x='JobRole', y='MonthlyIncome', 
                         color='JobRole', title="Average Monthly Income by Job Role")
        fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", 
                              xaxis_title="Job Role", yaxis_title="Avg Monthly Income ($)",
                              showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
        
    st.divider()
    st.subheader("Master Database View")
    st.dataframe(admin_filtered_df, use_container_width=True, height=350)

# 8. Route to specific dashboard based on role
if role == "Employee":
    show_employee_dashboard()
elif role == "HR":
    show_hr_dashboard()
elif role == "Admin":
    show_admin_dashboard()