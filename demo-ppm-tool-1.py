import json
from datetime import date, datetime

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="PPM Workspace",
    page_icon="📊",
    layout="wide"
)


# -----------------------------
# SESSION STATE
# -----------------------------

def init_state():
    defaults = {
        "projects": [],
        "tasks": [],
        "teams": ["Personal"],
        "current_user": "You"
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()


# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

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

        if not isinstance(data, dict):
            raise ValueError("Invalid backup format.")

        projects = data.get("projects", [])
        tasks = data.get("tasks", [])
        teams = data.get("teams", ["Personal"])

        if not all(isinstance(x, list) for x in [projects, tasks, teams]):
            raise ValueError("Projects, tasks, and teams must be lists.")

        if not all(isinstance(x, dict) for x in projects + tasks):
            raise ValueError("Invalid project or task records.")

        st.session_state.projects = projects
        st.session_state.tasks = tasks
        st.session_state.teams = teams or ["Personal"]
        st.session_state.current_user = str(
            data.get("current_user", "You")
        )

        st.success("Workspace imported successfully!")
        st.rerun()

    except Exception as e:
        st.error(f"Import failed: {e}")


# -----------------------------
# SIDEBAR
# -----------------------------

st.sidebar.title("PPM Workspace")

st.session_state.current_user = st.sidebar.text_input(
    "Your name",
    value=st.session_state.current_user
)

st.sidebar.divider()

page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Projects", "Tasks", "Teams", "Portfolio"]
)

st.sidebar.divider()

st.sidebar.subheader("Backup")

st.sidebar.download_button(
    label="Export Workspace",
    data=export_data(),
    file_name=f"ppm_workspace_{datetime.now().strftime('%Y%m%d')}.json",
    mime="application/json"
)

uploaded = st.sidebar.file_uploader(
    "Import Workspace",
    type=["json"]
)

if uploaded:
    if st.session_state.get("last_import_name") != uploaded.name:
        import_data(uploaded)
        st.session_state.last_import_name = uploaded.name


# -----------------------------
# DASHBOARD
# -----------------------------

if page == "Dashboard":

    st.title("Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric("Projects", len(st.session_state.projects))
    col2.metric("Tasks", len(st.session_state.tasks))
    col3.metric("Teams", len(st.session_state.teams))

    if st.session_state.projects:

        status_counts = pd.Series(
            [p.get("status", "Unknown")
             for p in st.session_state.projects]
        ).value_counts()

        st.subheader("Project Status")
        st.bar_chart(status_counts)

    else:
        st.info("Create your first project to see dashboard analytics.")


# -----------------------------
# PROJECTS
# -----------------------------

elif page == "Projects":

    st.title("Projects")

    with st.form("new_project", clear_on_submit=True):

        col1, col2 = st.columns(2)

        name = col1.text_input("Project Name")
        status = col2.selectbox(
            "Status",
            ["Planning", "Active", "On Hold", "Completed"]
        )

        team = st.selectbox(
            "Team",
            st.session_state.teams
        )

        description = st.text_area("Description")

        submitted = st.form_submit_button("Create Project")

        if submitted:

            if not name.strip():
                st.error("Project name is required.")

            elif name.strip() in get_project_names():
                st.error("A project with this name already exists.")

            else:
                st.session_state.projects.append({
                    "id": len(st.session_state.projects) + 1,
                    "name": name.strip(),
                    "description": description,
                    "status": status,
                    "team": team,
                    "owner": st.session_state.current_user,
                    "created_at": datetime.now().isoformat()
                })

                st.success(f"Project '{name}' created!")
                st.rerun()

    if st.session_state.projects:

        st.subheader("Project Register")

        df = pd.DataFrame(st.session_state.projects)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Update Project Status")

        selected = st.selectbox(
            "Select project",
            get_project_names()
        )

        new_status = st.selectbox(
            "New status",
            ["Planning", "Active", "On Hold", "Completed"]
        )

        if st.button("Update Status"):

            for project in st.session_state.projects:
                if project["name"] == selected:
                    project["status"] = new_status

            st.success("Project status updated.")
            st.rerun()


# -----------------------------
# TASKS
# -----------------------------

elif page == "Tasks":

    st.title("Tasks")

    if not st.session_state.projects:

        st.info("Create a project before adding tasks.")

    else:

        with st.form("new_task", clear_on_submit=True):

            proj_name = st.selectbox(
                "Project",
                get_project_names()
            )

            title = st.text_input("Task Title")

            assignee = st.text_input(
                "Assignee",
                value=st.session_state.current_user
            )

            status = st.selectbox(
                "Status",
                ["To Do", "In Progress", "Done"]
            )

            due = st.date_input(
                "Due Date",
                value=date.today()
            )

            submitted = st.form_submit_button("Add Task")

            if submitted:

                if not title.strip():
                    st.error("Task title is required.")

                else:
                    st.session_state.tasks.append({
                        "id": len(st.session_state.tasks) + 1,
                        "project": proj_name,
                        "title": title.strip(),
                        "assignee": assignee,
                        "status": status,
                        "due_date": due.isoformat(),
                        "created_at": datetime.now().isoformat()
                    })

                    st.success("Task added successfully.")
                    st.rerun()

    if st.session_state.tasks:

        st.subheader("Task Register")

        df = pd.DataFrame(st.session_state.tasks)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        incomplete_tasks = [
            t for t in st.session_state.tasks
            if t["status"] != "Done"
        ]

        if incomplete_tasks:

            st.subheader("Mark Task as Done")

            task_options = {
                f'{t["title"]} — {t["project"]} (#{t["id"]})': t["id"]
                for t in incomplete_tasks
            }

            selected_task = st.selectbox(
                "Select task",
                list(task_options.keys())
            )

            if st.button("Complete Task"):

                task_id = task_options[selected_task]

                for task in st.session_state.tasks:
                    if task["id"] == task_id:
                        task["status"] = "Done"

                st.success("Task completed.")
                st.rerun()


# -----------------------------
# TEAMS
# -----------------------------

elif page == "Teams":

    st.title("Teams")

    new_team = st.text_input("New Team Name")

    if st.button("Add Team"):

        team_name = new_team.strip()

        if not team_name:
            st.error("Enter a team name.")

        elif team_name in st.session_state.teams:
            st.warning("This team already exists.")

        else:
            st.session_state.teams.append(team_name)
            st.success(f"Team '{team_name}' added.")
            st.rerun()

    st.subheader("Current Teams")

    for team in st.session_state.teams:
        st.write(f"• {team}")


# -----------------------------
# PORTFOLIO
# -----------------------------

elif page == "Portfolio":

    st.title("Portfolio Overview")

    if not st.session_state.projects:

        st.info("No projects yet.")

    else:

        summary = []

        for project in st.session_state.projects:

            project_tasks = [
                t for t in st.session_state.tasks
                if t["project"] == project["name"]
            ]

            done = sum(
                1 for t in project_tasks
                if t["status"] == "Done"
            )

            total = len(project_tasks)

            progress = round(
                (done / total * 100) if total else 0,
                1
            )

            summary.append({
                "Project": project["name"],
                "Status": project["status"],
                "Team": project["team"],
                "Owner": project["owner"],
                "Tasks": total,
                "Done": done,
                "Progress %": progress
            })

        df = pd.DataFrame(summary)

        st.subheader("Portfolio Register")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Task Progress")

        st.bar_chart(
            df.set_index("Project")[["Tasks", "Done"]]
        )

        st.subheader("Project Completion")

        st.bar_chart(
            df.set_index("Project")["Progress %"]
        )


# -----------------------------
# FOOTER
# -----------------------------

st.sidebar.caption(
    "Session-based · Export to save your work"
)
