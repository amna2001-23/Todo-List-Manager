import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Initialize session state for users and tasks
if 'users' not in st.session_state:
    st.session_state['users'] = {}
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None

# Function to add a new user
def add_user(username, password):
    st.session_state['users'][username] = {
        'password': password,
        'tasks': pd.DataFrame(columns=['Task', 'Description', 'Category', 'Priority', 'Due Date', 'Status'])
    }

# Function to authenticate user
def authenticate(username, password):
    if username in st.session_state['users'] and st.session_state['users'][username]['password'] == password:
        st.session_state['current_user'] = username
        return True
    return False

# Function to add a new task
def add_task(task, description, category, priority, due_date):
    new_task = pd.DataFrame({
        'Task': [task], 
        'Description': [description], 
        'Category': [category], 
        'Priority': [priority], 
        'Due Date': [due_date], 
        'Status': ['Pending']
    })
    
    current_tasks = st.session_state['users'][st.session_state['current_user']]['tasks']
    st.session_state['users'][st.session_state['current_user']]['tasks'] = pd.concat([current_tasks, new_task], ignore_index=True)

# Function to update a task
def update_task(task_to_update, description, category, priority, due_date):
    tasks_df = st.session_state['users'][st.session_state['current_user']]['tasks']
    index = tasks_df[tasks_df['Task'] == task_to_update].index
    if not index.empty:
        tasks_df.loc[index, ['Description', 'Category', 'Priority', 'Due Date']] = [description, category, priority, due_date]
        st.session_state['users'][st.session_state['current_user']]['tasks'] = tasks_df

# Function to delete a task
def delete_task(task_to_delete):
    tasks_df = st.session_state['users'][st.session_state['current_user']]['tasks']
    tasks_df = tasks_df[tasks_df['Task'] != task_to_delete]
    st.session_state['users'][st.session_state['current_user']]['tasks'] = tasks_df

# Function to save tasks to a file
def save_tasks_to_file(format):
    tasks_df = st.session_state['users'][st.session_state['current_user']]['tasks']
    if format == 'CSV':
        tasks_df.to_csv('tasks.csv', index=False)
        st.success("Tasks saved to tasks.csv")
    elif format == 'Excel':
        tasks_df.to_excel('tasks.xlsx', index=False, engine='openpyxl')
        st.success("Tasks saved to tasks.xlsx")

# Function to upload tasks from a file
def upload_tasks_from_file(file):
    if file is not None:
        file_type = file.name.split('.')[-1]
        if file_type == 'csv':
            tasks_df = pd.read_csv(file)
        elif file_type in ['xlsx', 'xls']:
            tasks_df = pd.read_excel(file, engine='openpyxl')
        else:
            st.error("Unsupported file type.")
            return
        
        st.session_state['users'][st.session_state['current_user']]['tasks'] = tasks_df
        st.success("Tasks uploaded successfully!")

# Function to send reminders
def send_reminders(tasks_df):
    upcoming_tasks = tasks_df[tasks_df['Due Date'] <= (datetime.now().date() + timedelta(days=2))]
    if not upcoming_tasks.empty:
        for _, task in upcoming_tasks.iterrows():
            st.warning(f"Reminder: Task '{task['Task']}' is due soon!")

# Function to display task distribution chart
def plot_task_distribution(tasks_df):
    fig, ax = plt.subplots()
    task_counts = tasks_df['Category'].value_counts()
    task_counts.plot(kind='bar', ax=ax)
    ax.set_title('Task Distribution by Category')
    ax.set_xlabel('Category')
    ax.set_ylabel('Number of Tasks')
    st.pyplot(fig)

# Sidebar for registration and login
with st.sidebar:
    st.header("User Authentication")

    if st.session_state['current_user'] is None:
        option = st.selectbox("Choose Action", ["Login", "Register"])

        if option == "Register":
            st.subheader("Register")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Register"):
                if username in st.session_state['users']:
                    st.warning("Username already exists. Please login.")
                else:
                    add_user(username, password)
                    st.success("Registration successful. Please log in.")

        if option == "Login":
            st.subheader("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                if authenticate(username, password):
                    st.success(f"Welcome, {username}!")
                else:
                    st.error("Invalid username or password.")
    else:
        st.success(f"Logged in as: {st.session_state['current_user']}")
        if st.button("Logout"):
            st.session_state['current_user'] = None
            st.experimental_rerun()

# UI theme toggle for Dark Mode
theme_option = st.sidebar.radio("Theme", ["Light", "Dark"])
if theme_option == "Dark":
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #2e2e2e;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# If logged in, show the dashboard
if st.session_state['current_user']:
    st.title("Todo List Manager")

    # Task input section
    st.subheader("Add New Task")
    task = st.text_input("Task")
    description = st.text_area("Description")
    category = st.selectbox("Category", ["Business", "Doctor", "Teacher", "Freelancer", "Personal", "Students", "Govt"])
    priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    due_date = st.date_input("Due Date")

    if st.button("Add Task"):
        add_task(task, description, category, priority, due_date)
        st.success("Task added successfully!")

    # Show tasks
    tasks_df = st.session_state['users'][st.session_state['current_user']]['tasks']

    if not tasks_df.empty:
        st.subheader("Your Tasks")

        # Search and filter tasks
        search_term = st.text_input("Search Tasks")
        filter_category = st.selectbox("Filter by Category", ["All"] + tasks_df['Category'].unique().tolist())
        tasks_df = tasks_df[tasks_df['Task'].str.contains(search_term, case=False, na=False)]
        if filter_category != "All":
            tasks_df = tasks_df[tasks_df['Category'] == filter_category]

        # Display upcoming tasks (due in 2 days or less)
        upcoming_tasks = tasks_df[tasks_df['Due Date'] <= (datetime.now().date() + timedelta(days=2))]
        if not upcoming_tasks.empty:
            st.markdown("### Upcoming Tasks (due in 2 days or less)")
            send_reminders(upcoming_tasks)
            st.table(upcoming_tasks)

        # Display all tasks
        st.markdown("### All Tasks")
        st.table(tasks_df)

        # Option to mark tasks as complete
        st.subheader("Mark Task as Complete")
        task_to_complete = st.selectbox("Select Task to Complete", tasks_df['Task'])
        if st.button("Complete Task"):
            tasks_df.loc[tasks_df['Task'] == task_to_complete, 'Status'] = 'Complete'
            st.session_state['users'][st.session_state['current_user']]['tasks'] = tasks_df
            st.success(f"Task '{task_to_complete}' marked as complete!")

        # Options to update and delete tasks
        st.subheader("Manage Tasks")

        # Manage task actions
        action = st.selectbox("Select Action", ["None", "Update", "Delete"])
        if action == "Update":
            task_to_update = st.selectbox("Select Task to Update", tasks_df['Task'])
            updated_description = st.text_area("Updated Description", value=tasks_df[tasks_df['Task'] == task_to_update]['Description'].values[0])
            updated_category = st.selectbox("Updated Category", ["Business", "Doctor", "Teacher", "Freelancer", "Personal", "Students", "Govt"], index=tasks_df[tasks_df['Task'] == task_to_update].index[0])
            updated_priority = st.selectbox("Updated Priority", ["High", "Medium", "Low"], index=tasks_df[tasks_df['Task'] == task_to_update].index[0])
            updated_due_date = st.date_input("Updated Due Date", value=tasks_df[tasks_df['Task'] == task_to_update]['Due Date'].values[0])

            if st.button("Update Task"):
                update_task(task_to_update, updated_description, updated_category, updated_priority, updated_due_date)
                st.success(f"Task '{task_to_update}' updated successfully!")

        elif action == "Delete":
            task_to_delete = st.selectbox("Select Task to Delete", tasks_df['Task'])
            if st.button("Delete Task"):
                delete_task(task_to_delete)
                st.success(f"Task '{task_to_delete}' deleted successfully!")

        # Options to save or upload tasks
        st.subheader("Save or Upload Tasks")
        save_option = st.selectbox("Save Tasks as", ["None", "CSV", "Excel"])
        if save_option != "None" and st.button("Save Tasks"):
            save_tasks_to_file(save_option)
        
        uploaded_file = st.file_uploader("Upload Tasks File", type=['csv', 'xlsx'])
        if uploaded_file is not None and st.button("Upload Tasks"):
            upload_tasks_from_file(uploaded_file)
    
    # Plot task distribution
    st.subheader("Task Distribution")
    if not tasks_df.empty:
        plot_task_distribution(tasks_df)
