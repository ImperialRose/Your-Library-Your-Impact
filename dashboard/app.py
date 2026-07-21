import streamlit as st
from src.data import (load_bookings,
                      load_satisfaction,
                      load_satisfaction_both,
                      load_circulation,
                      load_admin_quant_data,
                      load_faculty_quant_data,
                      load_student_quant_data,
                      load_costs,
                      get_NPS_scores,
                      get_impact_satisfaction_ratings)
from src.filters import render_booking_filters, render_satisfaction_filters
from src.charts import (
    plot_bookings_by_year,
    plot_bookings_by_quarter,
    plot_service_type,
    plot_virtual_vs_inperson,
    plot_bioethics_topics,
    plot_satisfaction_means,
    plot_satisfaction_comparison,
    plot_circulation,
    plot_circulation_by_year,
    plot_costs_sum_per_student,
    plot_avg_NPS,
    plot_impact_satisfaction_ratings
)

## FUTURE ADDITIONS - Student Learning Outcomes
# When you are ready to add Student Learning Outcomes data to the dashboard, uncomment the lines below:
# from src.data import load_learning_outcomes
# from src.charts import plot_student_learning_outcomes
# from src.filters import render_learning_outcomes_filters

st.set_page_config(
    page_title="Your Library, Your Impact",
    page_icon="assets/pnwu_logo.png",
    layout="wide",
    initial_sidebar_state="auto"
)

st.markdown("""
<style>
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #1b3764 0%, #366732 100%); }
    [data-testid="stSidebar"] * { color: white !important; }
    .main-header {
        background: linear-gradient(135deg, #1b3764 0%, #366732 100%);
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    .main-header h1 { color: white; margin: 0; font-size: 2rem; }
    .main-header p { color: white; opacity: 0.85; margin: 0.3rem 0 0 0; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### YLYI Dashboard")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["Home", "Insights Bot"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown(
        "<small>E.R.A.I. Informatics · UW MSIM<br/>PNWU Health Sciences Library</small>",
        unsafe_allow_html=True,
    )

bookings_df = load_bookings()
sat23_df = load_satisfaction(2023)
sat25_df = load_satisfaction(2025)
sat_both_df = load_satisfaction_both()
circ_df = load_circulation()
costs_df = load_costs()
admin_df = load_admin_quant_data()
faculty_df = load_faculty_quant_data()
student_df = load_student_quant_data()
NPS_scores_df = get_NPS_scores(admin_df, faculty_df, student_df)
satisfaction_ratings_df = get_impact_satisfaction_ratings(admin_df, faculty_df, student_df)

if page == "Home":
    import base64
    with open("assets/pnwu_logo.png", "rb") as f:
        logo_data = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <div class="main-header" style="display:flex; align-items:center; gap:1.5rem;">
        <img src="data:image/png;base64,{logo_data}" width="90" style="border-radius:8px;">
        <div>
            <h1 style="margin:0; color:white; font-size:2rem;">Your Library, Your Impact</h1>
            <p style="margin:0.3rem 0 0 0; color:white; opacity:0.85;">PNWU Health Sciences Library · Analytics & Insights Dashboard</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Appointments", len(bookings_df))
    with col2:
        st.metric("Academic Years", bookings_df["AcademicYear"].nunique() if not bookings_df.empty else 0)
    with col3:
        st.metric("2023 Survey Respondents", len(sat23_df))
    with col4:
        st.metric("2025 Survey Respondents", len(sat25_df))

    st.markdown("---")

    # Creating tabs; note - see commented code below for when you want to add more tabs
    t1, t2, t3, t4, t5 = st.tabs([
        "Service Activity",
        "Collection Activity",
        "Library Costs per Student",
        "General Student Satisfaction",
        "Qualitative Impact"
    ])

    ## FUTURE ADDITION
    # When ready to add Student Learning Outcomes data, delete the section above and uncomment this section.
    # t1, t2, t3, t4, t5, t6 = st.tabs([
        # "Service Activity",
        # "Collection Activity",
        # "Library Costs per Student",
        # "General Student Satisfaction",
        # "Student Learning Outcomes",
        # "Qualitative Impact"
    # ])

    with t1:
        st.subheader("Service Activity")
        st.caption("Book a Librarian appointment activity and trends.")
        filtered_df = render_booking_filters(bookings_df, key_prefix="t1")
        if not filtered_df.empty:
            plot_bookings_by_year(filtered_df)
            col1, col2 = st.columns(2)
            with col1:
                plot_service_type(filtered_df)
            with col2:
                plot_virtual_vs_inperson(filtered_df)
            plot_bookings_by_quarter(filtered_df)
            st.info("Strategic plan target: 5% annual growth in student appointments.")
            plot_bioethics_topics(filtered_df)

    with t2:
        st.subheader("Collection Activity")
        st.caption("Physical book circulation data, by academic year.")
        col_cir1, col_cir2, col_cir3, col_cir4, col_cir5 = st.columns(5)
        with col_cir1:
            st.metric("Total Checkouts", circ_df["Checkout"].sum())
        with col_cir2:
            st.metric("Total Checkins", circ_df["Checkin"].sum())
        with col_cir3:
            st.metric("Total Renewals", circ_df["Renew"].sum())
        with col_cir4:
            st.metric("Total Lost Items", circ_df["Lost"].sum())
        with col_cir5:
            st.metric("Total Found Items", circ_df["Found"].sum())
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Checkouts", "Checkins", "Renews", "Hold", "Lost Items", "Found Items"])

        if circ_df.empty:
            st.error("No circulation data found.")
        else:
            with tab1:

                plot_circulation_by_year(circ_df, "Checkout")
                plot_circulation(circ_df, "Checkout")
            with tab2:

                plot_circulation_by_year(circ_df, "Checkin")
                plot_circulation(circ_df, "Checkin")
            with tab3:

                plot_circulation_by_year(circ_df, "Renew")
                plot_circulation(circ_df, "Renew")
            with tab4:

                plot_circulation_by_year(circ_df, "Hold")
                plot_circulation(circ_df, "Hold")

            with tab5:

                plot_circulation_by_year(circ_df, "Lost")
                plot_circulation(circ_df, "Lost")
            with tab6:

                plot_circulation_by_year(circ_df, "Found")
                plot_circulation(circ_df, "Found")
            st.info("Physical checkouts dropped from 415 in AY21-22 to 55 in AY24-25 — an 87% decline. Digital usage data coming when database reports are available.")

    with t3:
        st.subheader("Library Costs per Student")
        st.caption("Collection costs per student by collection resource and academic year.")
        if costs_df.empty:
            st.error("No cost data found")
        else:
            plot_costs_sum_per_student(costs_df)

    with t4:
        st.subheader("General Student Satisfaction")
        st.caption("PNWU Student Satisfaction Survey, library questions only. Scale 1-5.")
        survey_tab1, survey_tab2, survey_tab3 = st.tabs(["2023", "2025", "Year-over-Year"])
        with survey_tab1:
            if sat23_df.empty:
                st.warning("2023 data not found.")
            else:
                filtered_sat23 = render_satisfaction_filters(sat23_df, key_prefix="sat23")
                plot_satisfaction_means(filtered_sat23, 2023)
                st.caption(f"{len(filtered_sat23)} respondents · 57.99% response rate")
        with survey_tab2:
            if sat25_df.empty:
                st.warning("2025 data not found.")
            else:
                filtered_sat25 = render_satisfaction_filters(sat25_df, key_prefix="sat25")
                plot_satisfaction_means(filtered_sat25, 2025)
                st.caption(f"{len(filtered_sat25)} respondents · 62.89% response rate")
        with survey_tab3:
            st.info("2023 and 2025 used different question sets so overlap is limited.")
            plot_satisfaction_comparison(sat_both_df)

    with t5:
        st.subheader("Qualitative Impact")
        st.caption("Results from a mixed impact (qualitative and quantitative) survey of students, faculty & staff, and administration. Survey developed by E.R.A.I. Informatics and the PNWU Library, administered Q3 AY25-26 (calendar Q1 2026).")
        subtab1, subtab2 = st.tabs(["Average NPS Score by Respondent Group", "Satisfaction Ratings Across All Groups"])
        with subtab1:
            if NPS_scores_df.empty:
                st.warning("NPS score data not found.")
            else:
                plot_avg_NPS(NPS_scores_df)
                st.info("Students, the most frequent users of the library, gave the highest NPS score. Faculty rated the library just below the passive threshold (NPS 7): they know the library is there but do not see it as a true partner in their own teaching & research. Administrators gave the lowest score.")
        with subtab2:
            if satisfaction_ratings_df.empty:
                st.warning("Impact survey satisfaction ratings data not found.")
            else:
                plot_impact_satisfaction_ratings(satisfaction_ratings_df)

    st.markdown("---")

    with open("assets/uw_logo.png", "rb") as f:
        uw_logo = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-top:1rem; opacity:0.7;">
        <small>Built by E.R.A.I. Informatics (Em Stelter · Rose Brown · AJ Amrous · Ivette Ivanov) · Sponsor: Jan Kuebel-Hernandez</small>
        <div style="display:flex; align-items:center; gap:0.5rem;">
            <small>Powered by</small>
            <img src="data:image/png;base64,{uw_logo}" width="50">
            <small>UW iSchool</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif page == "Insights Bot":
    from src.bot import answer, OLLAMA_HOST, OLLAMA_MODEL

    st.markdown("## AI Insights Bot")
    st.caption(
        "Ask about service activity (Book a Librarian appointments) or student satisfaction (PNWU Student Satisfaction Surveys)."
    )
    st.caption(
        "Answers are computed directly from the dashboard data. The "
        f"local model ({OLLAMA_MODEL}) only interprets your question."
    )

    with st.expander("Example questions"):
        st.markdown(
            "- How many Book a Librarian appointments were there in 2023-2024?\n"
            "- What percent of AY24-25 appointments were virtual?\n"
            "- Break down appointments by service for AY23-24\n"
            "- How many appointments each year?\n"
            "- Show the 2025 satisfaction scores"
        )

    if "bot_messages" not in st.session_state:
        st.session_state.bot_messages = [
            {"role": "assistant",
             "content": "Hi! Ask me about library appointments or student satisfaction surveys."}
        ]

    for msg in st.session_state.bot_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about library appointments or surveys..."):
        st.session_state.bot_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Looking at the data..."):
                reply = answer(prompt)
            st.markdown(reply)
        st.session_state.bot_messages.append({"role": "assistant", "content": reply})
