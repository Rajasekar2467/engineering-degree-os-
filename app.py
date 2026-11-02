import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="My Engineering Degree OS",
    page_icon="🎓",
    layout="wide"
)

# ---------------------------------------------------------
# Data Loader Functions
# ---------------------------------------------------------
DATA_DIR = "data"

def load_data(filename, default_cols):
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        try:
            return pd.read_csv(filepath)
        except Exception as e:
            st.error(f"Error reading {filename}: {e}")
            return pd.DataFrame(columns=default_cols)
    else:
        st.warning(f"File {filename} is missing in /{DATA_DIR}. Showing empty data.")
        return pd.DataFrame(columns=default_cols)

def save_data(df, filename):
    filepath = os.path.join(DATA_DIR, filename)
    try:
        df.to_csv(filepath, index=False)
        st.success(f"Successfully saved {filename}!")
    except Exception as e:
        st.error(f"Error saving {filename}: {e}")

# Load all core CSVs
semesters_df = load_data("semesters.csv", ["semester", "status", "total_credits", "completed_credits"])
courses_df = load_data("courses.csv", ["semester", "course_code", "course_name", "credits", "syllabus", "status"])
calendar_df = load_data("academic_calendar.csv", ["academic_year", "semester", "date", "event_type", "title"])
assessments_df = load_data("assessments.csv", ["semester", "course_code", "assessment_type", "date", "max_marks", "status"])
scores_df = load_data("scores.csv", ["semester", "course_code", "assessment_type", "score", "max_marks", "grade"])
checklist_df = load_data("plan_checklist.csv", ["category", "item", "target_date", "status", "notes"])

# ---------------------------------------------------------
# Sidebar Navigation (11 Required Tabs)
# ---------------------------------------------------------
st.sidebar.title("🎓 Degree OS")
menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Semesters 1-8",
        "Courses & Syllabus",
        "University Syllabus",
        "Academic / Leave Calendar",
        "Internal Assessments",
        "Status Tracker",
        "Scorecard",
        "Plan & Checklist",
        "Ask Degree AI",
        "Data Admin"
    ]
)

# ---------------------------------------------------------
# 1. Dashboard
# ---------------------------------------------------------
if menu == "Dashboard":
    st.title("📊 Degree Dashboard")
    st.write("Welcome to your 1st-to-8th semester command center.")

    # Calculate summary metrics
    total_creds = pd.to_numeric(semesters_df["total_credits"], errors="coerce").sum() if not semesters_df.empty else 0
    comp_creds = pd.to_numeric(semesters_df["completed_credits"], errors="coerce").sum() if not semesters_df.empty else 0
    pct_complete = (comp_creds / total_creds * 100) if total_creds > 0 else 0

    current_sem_rows = semesters_df[semesters_df["status"].str.strip().str.lower() == "in progress"] if not semesters_df.empty else pd.DataFrame()
    curr_sem = current_sem_rows.iloc[0]["semester"] if not current_sem_rows.empty else 3

    # Upcoming assessment & Next holiday
    today = datetime.now().strftime("%Y-%m-%d")
    next_assess = "None scheduled"
    if not assessments_df.empty and "date" in assessments_df.columns:
        upcoming_a = assessments_df[assessments_df["date"] >= today].sort_values("date")
        if not upcoming_a.empty:
            r = upcoming_a.iloc[0]
            next_assess = f"{r['course_code']} {r['assessment_type']} ({r['date']})"

    next_holiday = "None listed"
    if not calendar_df.empty and "date" in calendar_df.columns and "event_type" in calendar_df.columns:
        upcoming_h = calendar_df[(calendar_df["event_type"].str.lower() == "holiday") & (calendar_df["date"] >= today)].sort_values("date")
        if not upcoming_h.empty:
            rh = upcoming_h.iloc[0]
            next_holiday = f"{rh['title']} ({rh['date']})"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Semester", f"Sem {curr_sem}")
    col2.metric("Degree Progress", f"{pct_complete:.1f}%", f"{int(comp_creds)}/{int(total_creds)} Credits")
    col3.metric("Next Assessment", next_assess)
    col4.metric("Next Holiday", next_holiday)

    st.markdown("---")
    st.subheader("Semester Progress Overview")
    if not semesters_df.empty and "semester" in semesters_df.columns and "completed_credits" in semesters_df.columns:
        chart_data = semesters_df.copy()
        chart_data["completed_credits"] = pd.to_numeric(chart_data["completed_credits"], errors="coerce").fillna(0)
        chart_data["total_credits"] = pd.to_numeric(chart_data["total_credits"], errors="coerce").fillna(0)
        st.bar_chart(chart_data.set_index("semester")[["completed_credits", "total_credits"]])

# ---------------------------------------------------------
# 2. Semesters 1-8
# ---------------------------------------------------------
elif menu == "Semesters 1-8":
    st.title("📚 Semesters 1 to 8 Overview")
    cols = st.columns(4)
    for i in range(1, 9):
        sem_info = semesters_df[semesters_df["semester"] == i] if not semesters_df.empty else pd.DataFrame()
        with cols[(i - 1) % 4]:
            with st.container(border=True):
                st.subheader(f"Semester {i}")
                if not sem_info.empty:
                    row = sem_info.iloc[0]
                    st.write(f"**Status:** {row['status']}")
                    st.write(f"**Credits:** {row['completed_credits']} / {row['total_credits']}")
                else:
                    st.write("No record found")

# ---------------------------------------------------------
# 3. Courses & Syllabus
# ---------------------------------------------------------
elif menu == "Courses & Syllabus":
    st.title("📖 Courses & Syllabus")
    selected_sem = st.selectbox("Select Semester", options=list(range(1, 9)), index=2)
    filtered = courses_df[courses_df["semester"] == selected_sem] if not courses_df.empty else pd.DataFrame()
    st.dataframe(filtered, use_container_width=True)

# ---------------------------------------------------------
# 4. University Syllabus
# ---------------------------------------------------------
elif menu == "University Syllabus":
    st.title("🏛️ University Syllabus Reference")
    st.markdown("""
    **Degree Programme:** Bachelor of Engineering / Technology (Computer Science & Engineering)  
    **Total Semesters:** 8  
    **Total Minimum Expected Credits:** 160  
    """)
    st.text_input("Official Syllabus URL / Document Reference", value="https://university.ac.in/regulations-cse-syllabus.pdf")
    st.info("Course regulations and syllabus reference source stored for accreditation and verification.")

# ---------------------------------------------------------
# 5. Academic / Leave Calendar
# ---------------------------------------------------------
elif menu == "Academic / Leave Calendar":
    st.title("🗓️ Academic & Leave Calendar")
    c1, c2 = st.columns(2)
    with c1:
        years = calendar_df["academic_year"].dropna().unique().tolist() if not calendar_df.empty else ["2026-27"]
        sel_year = st.selectbox("Academic Year", years)
    with c2:
        sel_sem = st.selectbox("Semester", options=["All"] + list(range(1, 9)), index=3)

    cal_filtered = calendar_df[calendar_df["academic_year"] == sel_year] if not calendar_df.empty else pd.DataFrame()
    if sel_sem != "All" and not cal_filtered.empty:
        cal_filtered = cal_filtered[cal_filtered["semester"] == sel_sem]
    st.dataframe(cal_filtered, use_container_width=True)

# ---------------------------------------------------------
# 6. Internal Assessments
# ---------------------------------------------------------
elif menu == "Internal Assessments":
    st.title("📝 Internal Assessments & Exams")
    sel_sem = st.selectbox("Filter by Semester", options=["All"] + list(range(1, 9)), index=3)
    ass_filtered = assessments_df.copy() if not assessments_df.empty else pd.DataFrame()
    if sel_sem != "All" and not ass_filtered.empty:
        ass_filtered = ass_filtered[ass_filtered["semester"] == sel_sem]
    st.dataframe(ass_filtered, use_container_width=True)

# ---------------------------------------------------------
# 7. Status Tracker
# ---------------------------------------------------------
elif menu == "Status Tracker":
    st.title("📈 Course Status Tracker")
    sel_sem = st.selectbox("Select Semester", options=list(range(1, 9)), index=2)
    c_sem = courses_df[courses_df["semester"] == sel_sem] if not courses_df.empty else pd.DataFrame()
    
    if not c_sem.empty and "status" in c_sem.columns:
        counts = c_sem["status"].str.strip().value_counts()
        done = counts.get("Completed", 0)
        in_prog = counts.get("In Progress", 0)
        not_start = counts.get("Not Started", 0)
        total = len(c_sem)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Courses", total)
        c2.metric("Completed", done)
        c3.metric("In Progress", in_prog)
        c4.metric("Not Started", not_start)

        st.progress(done / total if total > 0 else 0)
    st.dataframe(c_sem, use_container_width=True)

# ---------------------------------------------------------
# 8. Scorecard
# ---------------------------------------------------------
elif menu == "Scorecard":
    st.title("🎯 Scorecard & Performance")
    st.caption("Note: Prototype percentage calculation. Does not reflect official weighted university CGPA formulas.")
    if not scores_df.empty and "score" in scores_df.columns and "max_marks" in scores_df.columns:
        scores_df["score"] = pd.to_numeric(scores_df["score"], errors="coerce")
        scores_df["max_marks"] = pd.to_numeric(scores_df["max_marks"], errors="coerce")
        total_sc = scores_df["score"].sum()
        total_max = scores_df["max_marks"].sum()
        pct = (total_sc / total_max * 100) if total_max > 0 else 0
        st.metric("Prototype Score Percentage", f"{pct:.2f}%")
        st.dataframe(scores_df, use_container_width=True)
    else:
        st.info("No score data available.")

# ---------------------------------------------------------
# 9. Plan & Checklist
# ---------------------------------------------------------
elif menu == "Plan & Checklist":
    st.title("✅ Degree Execution Plan & Checklist")
    st.write("Maintain degree milestones, document readiness, and placement prep.")
    
    edited_checklist = st.data_editor(checklist_df, num_rows="dynamic", use_container_width=True)
    if st.button("Save Checklist Changes"):
        save_data(edited_checklist, "plan_checklist.csv")

# ---------------------------------------------------------
# 10. Ask Degree AI
# ---------------------------------------------------------
elif menu == "Ask Degree AI":
    st.title("🤖 Ask Degree AI")
    st.caption("Answers strictly grounded in Degree OS data.")

    user_query = st.text_input("Ask a question (e.g., 'What subjects are left in Sem 3?', 'When is my next assessment?')")

    if st.button("Ask") and user_query:
        q = user_query.lower()
        if "next assessment" in q or "when is my next ia" in q:
            today = datetime.now().strftime("%Y-%m-%d")
            upcoming = assessments_df[assessments_df["date"] >= today].sort_values("date") if not assessments_df.empty else pd.DataFrame()
            if not upcoming.empty:
                r = upcoming.iloc[0]
                st.write(f"**Source: Assessments** | Next upcoming assessment is **{r['course_code']} ({r['assessment_type']})** on **{r['date']}**.")
            else:
                st.write("No upcoming assessments found in Degree OS data.")
        elif "holiday" in q:
            today = datetime.now().strftime("%Y-%m-%d")
            upcoming_h = calendar_df[(calendar_df["event_type"].str.lower() == "holiday") & (calendar_df["date"] >= today)].sort_values("date") if not calendar_df.empty else pd.DataFrame()
            if not upcoming_h.empty:
                r = upcoming_h.iloc[0]
                st.write(f"**Source: Calendar** | Next holiday is **{r['title']}** on **{r['date']}**.")
            else:
                st.write("No upcoming holidays found.")
        elif "incomplete" in q or "left in sem" in q or "pending" in q:
            incomp = courses_df[courses_df["status"].str.strip() != "Completed"] if not courses_df.empty else pd.DataFrame()
            st.write("**Source: Courses** | Pending courses:")
            st.dataframe(incomp[["semester", "course_code", "course_name", "status"]])
        elif "cgpa" in q or "formula" in q:
            st.warning("I cannot verify that from the current Degree OS data.")
        else:
            st.info("I cannot verify that from the current Degree OS data. (AI API key not connected; using local deterministic fallback)")

# ---------------------------------------------------------
# 11. Data Admin
# ---------------------------------------------------------
elif menu == "Data Admin":
    st.title("⚙️ Data Admin")
    st.write("Directly edit and save CSV tables without touching application code.")

    table_choice = st.selectbox("Select Table to Edit", ["Semesters", "Courses", "Academic Calendar", "Assessments", "Scores"])
    
    if table_choice == "Semesters":
        ed = st.data_editor(semesters_df, num_rows="dynamic", use_container_width=True)
        if st.button("Save Semesters"): save_data(ed, "semesters.csv")
    elif table_choice == "Courses":
        ed = st.data_editor(courses_df, num_rows="dynamic", use_container_width=True)
        if st.button("Save Courses"): save_data(ed, "courses.csv")
    elif table_choice == "Academic Calendar":
        ed = st.data_editor(calendar_df, num_rows="dynamic", use_container_width=True)
        if st.button("Save Calendar"): save_data(ed, "academic_calendar.csv")
    elif table_choice == "Assessments":
        ed = st.data_editor(assessments_df, num_rows="dynamic", use_container_width=True)
        if st.button("Save Assessments"): save_data(ed, "assessments.csv")
    elif table_choice == "Scores":
        ed = st.data_editor(scores_df, num_rows="dynamic", use_container_width=True)
        if st.button("Save Scores"): save_data(ed, "scores.csv")