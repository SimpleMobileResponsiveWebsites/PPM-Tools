import streamlit as st
import pandas as pd
from datetime import datetime, date
import json

def init_state():
    if "projects" not in st.session_state:
        st.session_state.projects = []
    if "tasks" not in st.session_state:
        st.session_state.tasks = []
    if "teams" not in st.session_state:
        st.session_state.teams = ["Personal"]
    if "current_user" not in st.session_state:
        st.session_state.current_user = "You"

init_state()

def get_project_names():
    return [p["name"] for p in st.session_state.projects]

def export_data():
    data = {
        "projects": st.session_state.projects,
        "tasks": st.session_state.tasks,
        "teams": st.session_state.teams,
        "current_user": st.session_state.current_user
    }
    return json.dumps(data, indent=2, default=str)

def import_data(uploaded_file):
    try:
        data = json.load(uploaded_file)
        st.session_state.projects = data.get("projects", [])
        st.session_state.tasks = data.get("tasks", [])
        st.session_state.teams = data.get("teams", ["Personal"])
        st.session_state.current_user = data.get("current_user", "You")
        st.success("Workspace imported successfully!")
        st.rerun()
    except Exception as e:
        st.error(f"Import failed: {e}")

st.sidebar.title("PPM Workspace")
st.session_state.current_user = st.sidebar.text_input("Your name", value=st.session_state.current_user)

st.sidebar.divider()
page = st.sidebar.radio("Go to", ["Dashboard", "Projects", "Tasks", "Teams", "Portfolio"])

st.sidebar.divider()
st.sidebar.subheader("Backup")
st.sidebar.download_button(
    label="Export Workspace",
    data=export_data(),
    file_name=f"ppm_workspace_{datetime.now().strftime('%Y%m%d')}.json",
    mime="application/json"
)

uploaded = st.sidebar.file_uploader("Import Workspace", type="json")
if uploaded:
    import_data(uploaded)

if page == "Dashboard":
    st.title("Dashboard")
    col1, col2, col3 = st.columns(3)
    col1.metric("Projects", len(st.session_state.projects))
    col2.metric("Tasks", len(st.session_state.tasks))
    col3.metric("Teams", len(st.session_state.teams))

    if st.session_state.projects:
        status_counts = pd.Series([p["status"] for p in st.session_state.projects]).value_counts()
        st.subheader("Project Status")
        st.bar_chart(status_counts)

elif page == "Projects":
    st.title("Projects")

    with st.form("new_project", clear_on_submit=True):
        col1, col2 = st.columns(2)
        name = col1.text_input("Project Name*")
        status = col2.selectbox("Status", ["Planning", "Active", "On Hold", "Completed"])
        team = st.selectbox("Team", st.session_state.teams)
        description = st.text_area("Description")
        submitted = st.form_submit_button("Create Project")

        if submitted and name:
            st.session_state.projects.append({
                "id": len(st.session_state.projects) + 1,
                "name": name,
                "description": description,
                "status": status,
                "team": team,
                "owner": st.session_state.current_user,
                "created_at": datetime.now().isoformat()
            })
            st.success(f"Project '{name}' created")
            st.rerun()

    if st.session_state.projects:
        df = pd.DataFrame(st.session_state.projects)
        st.dataframe(df[["name", "status", "team", "owner", "description"]], use_container_width=True)

        st.subheader("Update Project Status")
        proj_names = get_project_names()
        if proj_names:
            selected = st.selectbox("Select project", proj_names)
            new_status = st.selectbox("New status", ["Planning", "Active", "On Hold", "Completed"])
            if st.button("Update Status"):
                for p in st.session_state.projects:
                    if p["name"] == selected:
                        p["status"] = new_status
                st.rerun()

elif page == "Tasks":
    st.title("Tasks")

    if not st.session_state.projects:
        st.info("Create a project first")
    else:
        with st.form("new_task", clear_on_submit=True):
            proj_name = st.selectbox("Project", get_project_names())
            title = st.text_input("Task Title*")
            assignee = st.text_input("Assignee", value=st.session_state.current_user)
            status = st.selectbox("Status", ["To Do", "In Progress", "Done"])
            due = st.date_input("Due Date", value=date.today())
            submitted = st.form_submit_button("Add Task")

            if submitted and title:
                st.session_state.tasks.append({
                    "id": len(st.session_state.tasks) + 1,
                    "project": proj_name,
                    "title": title,
                    "assignee": assignee,
                    "status": status,
                    "due_date": due.isoformat(),
                    "created_at": datetime.now().isoformat()
                })
                st.success("Task added")
                st.rerun()

    if st.session_state.tasks:
        df = pd.DataFrame(st.session_state.tasks)
        st.dataframe(df[["project", "title", "assignee", "status", "due_date"]], use_container_width=True)

        st.subheader("Mark as Done")
        task_titles = [t["title"] for t in st.session_state.tasks if t["status"] != "Done"]
        if task_titles:
            selected_task = st.selectbox("Select task", task_titles)
            if st.button("Complete Task"):
                for t in st.session_state.tasks:
                    if t["title"] == selected_task:
                        t["status"] = "Done"
                st.rerun()

elif page == "Teams":
    st.title("Teams")

    new_team = st.text_input("New Team Name")
    if st.button("Add Team") and new_team and new_team not in st.session_state.teams:
        st.session_state.teams.append(new_team)
        st.success(f"Team '{new_team}' added")
        st.rerun()

    st.write("**Current Teams:**")
    for team in st.session_state.teams:
        st.write(f"• {team}")

elif page == "Portfolio":
    st.title("Portfolio Overview")

    if not st.session_state.projects:
        st.info("No projects yet")
    else:
        summary = []
        for p in st.session_state.projects:
            proj_tasks = [t for t in st.session_state.tasks if t["project"] == p["name"]]
            done = len([t for t in proj_tasks if t["status"] == "Done"])
            total = len(proj_tasks)
            progress = round((done / total * 100) if total else 0, 1)
            summary.append({
                "Project": p["name"],
                "Status": p["status"],
                "Team": p["team"],
                "Owner": p["owner"],
                "Tasks": total,
                "Done": done,
                "Progress %": progress
            })

        df = pd.DataFrame(summary)
        st.dataframe(df, use_container_width=True)

        if not df.empty:
            st.bar_chart(df.set_index("Project")[["Tasks", "Done"]])

st.sidebar.caption("Session-based · Export to save your work")
