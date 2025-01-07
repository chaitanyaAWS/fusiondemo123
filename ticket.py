from dash import Dash, html, dcc, Input, Output, State
import mysql.connector
from mysql.connector import Error
import os

# Initialize the Dash app
app = Dash(__name__)

# Get list of employees from the database
def get_employees():
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'software')
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name FROM employees")
        employees = cursor.fetchall()
        cursor.close()
        conn.close()
        return [{'label': emp['name'], 'value': emp['name']} for emp in employees]
    except Error as e:
        return []

# Define the layout of the dashboard
app.layout = html.Div([
    html.H1("VI TAC Employee Ticket Dashboard"),
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='employee-dropdown',
                options=get_employees(),
                placeholder='Select an Employee'
            ),
        ]),
        html.Div([
            dcc.Textarea(
                id='ticket-description',
                placeholder='Ticket Description',
                style={'width': '100%'}
            ),
        ]),
        html.Div([
            dcc.Dropdown(
                id='status-dropdown',
                options=[
                    {'label': 'Open', 'value': 'Open'},
                    {'label': 'In Progress', 'value': 'In Progress'},
                    {'label': 'Closed', 'value': 'Closed'}
                ],
                value='Open'
            ),
        ]),
        html.Button('Submit', id='submit-button', n_clicks=0),
        html.Div(id='output-message')
    ])
])

# Callback to handle form submission and save data to MySQL
@app.callback(
    Output('output-message', 'children'),
    Input('submit-button', 'n_clicks'),
    State('employee-dropdown', 'value'),
    State('ticket-description', 'value'),
    State('status-dropdown', 'value')
)
def update_output(n_clicks, employee_name, ticket_description, status):
    if n_clicks > 0:
        if not employee_name or not ticket_description:
            return "Please provide both employee name and ticket description."

        # Construct table name based on employee name
        table_name = f'tickets_{employee_name.replace(" ", "_")}'
        
        try:
            # Connect to MySQL database
            conn = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),
                database=os.getenv('DB_NAME', 'software')
            )
            cursor = conn.cursor()

            # Insert data into the specific employee's tickets table
            cursor.execute(f'''
                INSERT INTO {table_name} (ticket_description, status)
                VALUES (%s, %s)
            ''', (ticket_description, status))

            conn.commit()
            return f"Ticket submitted successfully for {employee_name}."
        except Error as e:
            return f"An error occurred: {e}"
        finally:
            if conn.is_connected():
                conn.close()
    return ""

if __name__ == '__main__':
    app.run_server(debug=True)
