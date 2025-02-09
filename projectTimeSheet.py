import subprocess
subprocess.check_call(["pip", "install", "plotly"])

import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Project-wise Monthly Timesheet Dashboard")

uploaded_file = st.file_uploader("Upload Timesheet Excel", type=["xlsx"])

if uploaded_file:
    # Read all sheets to get project names
    xls = pd.ExcelFile(uploaded_file)
    project_names = xls.sheet_names
    
    # Sidebar project selection
    selected_project = st.sidebar.selectbox("Select Project", project_names)
    
    # Read the selected worksheet
    df = pd.read_excel(uploaded_file, sheet_name=selected_project)
    
    # Get the first column name (which should be the month column)
    month_column = df.columns[0]
    
    # Clean and prepare data
    # Fill NaN values in the month column with previous valid value (forward fill)
    df[month_column] = df[month_column].fillna(method='ffill')
    
    # Remove completely empty rows
    df = df.dropna(how='all')
    
    # Get unique months for selection (excluding NaN)
    months = df[month_column].dropna().unique().tolist()
    
    if months:
        # Sidebar month selection
        selected_month = st.sidebar.selectbox("Select Month", months)
        
        # Filter data for selected month
        monthly_data = df[df[month_column] == selected_month].copy()
        
        # Get employee and hours columns (should be second and third columns)
        employee_column = df.columns[1]
        hours_column = df.columns[2]
        
        # Remove the Month column from display and drop any remaining NaN rows
        display_data = monthly_data[[employee_column, hours_column]].dropna()
        
        # Display the data
        st.subheader(f"Working Hours for {selected_project} - {selected_month}")
        st.dataframe(display_data, hide_index=True)
        
        # Calculate and display total hours
        total_hours = display_data[hours_column].sum()
        st.metric("Total Hours", f"{total_hours:.2f}")
        
        # Create bar chart using plotly
        if not display_data.empty:
            fig = px.bar(
                display_data,
                x=employee_column,
                y=hours_column,
                title=f'Hours Worked - {selected_project} - {selected_month}',
                height=500
            )
            
            # Customize the layout
            fig.update_layout(
                xaxis_tickangle=-45,
                xaxis_title="Employee",
                yaxis_title="Hours",
                showlegend=False,
                margin=dict(b=100)  # Add bottom margin for rotated labels
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Download button for filtered data
        csv = display_data.to_csv(index=False)
        st.download_button(
            label="Download Data as CSV",
            data=csv,
            file_name=f'{selected_project}_{selected_month}_timesheet.csv',
            mime='text/csv'
        )
    else:
        st.error("No valid month data found in the selected worksheet")
else:
    st.info("Please upload an Excel file to view the dashboard")
