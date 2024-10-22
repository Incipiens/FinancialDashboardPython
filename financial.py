from flask import Flask, request, render_template
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if not file:
        return "No file uploaded!", 400

    df = pd.read_csv(file)
    
    # Convert 'Date' column to datetime format for better handling
    df['Date'] = pd.to_datetime(df['Date'])

    # Group by Category and sum the Amount for each category
    category_summary = df.groupby('Category')['Amount'].sum().reset_index()

    # Calculate monthly income and expenses
    df['Month'] = df['Date'].dt.to_period('M')
    
    # Convert 'Month' (Period) to string so it's JSON serializable and show Month names only
    df['Month'] = df['Date'].dt.strftime('%B')

    # Ensure months are ordered properly (January, February, etc.)
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                'July', 'August', 'September', 'October', 'November', 'December']
    df['Month'] = pd.Categorical(df['Month'], categories=month_order, ordered=True)

    # Group by month and summarize income, expenses, and net
    monthly_summary = df.groupby('Month').agg({'Amount': ['sum', lambda x: x[x > 0].sum(), lambda x: x[x < 0].sum()]}).reset_index()
    monthly_summary.columns = ['Month', 'Net', 'Income', 'Expenses']

    # Create graphs
    fig_income_expense = px.bar(monthly_summary, x='Month', y=['Income', 'Expenses'], barmode='group', title='Monthly Income and Expenses')

    # Ensure expenses only (Amount < 0) for the expense breakdown pie chart
    # Also, exclude the 'Savings' category from the expense breakdown and convert amounts to positive for the pie chart
    expense_data = category_summary[(category_summary['Amount'] < 0) & (category_summary['Category'] != 'Savings')].copy()
    expense_data['Amount'] = expense_data['Amount'].abs()  # Convert negative values to positive

    # Create expense pie chart if there's any valid data
    if not expense_data.empty:
        fig_category_expenses = px.pie(expense_data, values='Amount', names='Category', title='Expenses by Category')
    else:
        fig_category_expenses = "No expense data available."

    # Total income and total expenses summary
    total_income = df[df['Amount'] > 0]['Amount'].sum()
    total_expenses = df[df['Amount'] < 0]['Amount'].sum()

    # Calculate total savings as the difference between total income and total expenses
    total_savings = total_income - abs(total_expenses)
    
    # Calculate savings as a percentage of income
    savings_percentage = (total_savings / total_income) * 100

    # Create a summary figure with key metrics
    fig_summary = go.Figure()
    fig_summary.add_trace(go.Indicator(
        mode="number",
        value=total_income,
        title={"text": "Total Income (€)"},
        domain={'row': 0, 'column': 0},
        number={'valueformat': '.0f'}  # Full num, no abbrev
    ))
    fig_summary.add_trace(go.Indicator(
        mode="number",
        value=abs(total_expenses),
        title={"text": "Total Expenses (€)"},
        domain={'row': 0, 'column': 1},
        number={'valueformat': '.0f'}  
    ))
    fig_summary.add_trace(go.Indicator(
        mode="number",
        value=total_savings,
        title={"text": "Total Savings (€)"},
        domain={'row': 0, 'column': 2},
        number={'valueformat': '.0f'}  
    ))
    fig_summary.update_layout(grid={'rows': 1, 'columns': 3}, title='Summary')

    # Render the dashboard in the template and pass the graphs through
    return render_template(
        'index.html',
        fig_summary=fig_summary.to_html(),
        fig_income_expense=fig_income_expense.to_html(),
        fig_category_expenses=fig_category_expenses if isinstance(fig_category_expenses, str) else fig_category_expenses.to_html(),
        savings_percentage=savings_percentage
    )

if __name__ == '__main__':
    app.run(debug=True)