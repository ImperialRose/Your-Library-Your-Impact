import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# PNWU Brand Colors
PACIFIC_BLUE    = "#1b3764"
FOREST_GREEN    = "#366732"
VINEYARD_GREEN  = "#659a41"
NEW_LEAF        = "#99ca3c"
CLOUD_BLUE      = "#72c7f0"
SILVER_GRAY     = "#a4a9ad"
BALANCE_GRAY    = "#616467"
WARNING_RED     = "#c0392b"

def plot_bookings_by_year(df: pd.DataFrame) -> None:
    """
    A big picture chart. How many appointments happened each year?
    Jan's strategic plan 5% annual growth target We can see 
    if the library's hitting it 
    """
    if df.empty:
        st.info("No appointment data available.")
        return

    agg = (
        df.groupby("AcademicYear", as_index=False)
        .size()
        .rename(columns={"size": "Appointments"})
        .sort_values("AcademicYear")
    )

    fig = px.bar(
        agg,
        x="AcademicYear",
        y="Appointments",
        text="Appointments",
        color_discrete_sequence=[CLOUD_BLUE],
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        title="Book a Librarian — Appointments by Academic Year",
        xaxis_title="Academic Year",
        yaxis_title="Total Appointments",
        plot_bgcolor="white",
        paper_bgcolor="white",
        yaxis=dict(gridcolor="#f0f0f0"),
    )
    st.plotly_chart(fig, width='stretch')


def plot_bookings_by_quarter(df: pd.DataFrame) -> None:
    """
    Quarterly appointment trend as an area chart.
    Shows seasonality which parts of the year are busiest
    """
    if df.empty:
        st.info("No appointment data available.")
        return

    agg = (
        df.groupby("YearQuarter", as_index=False)
        .size()
        .rename(columns={"size": "Appointments"})
        .sort_values("YearQuarter")
    )

    st.area_chart(
        agg.set_index("YearQuarter")["Appointments"],
        color=FOREST_GREEN,
    )

def plot_service_type(df: pd.DataFrame) -> None:
    """
    What are people booking? Research consultations,
    orientations, special projects? Shows which
    services are being used & which need promotion
    """
    if df.empty or "Service" not in df.columns:
        st.info("No service type data available.")
        return

    agg = (
        df["Service"]
        .value_counts()
        .reset_index()
        .rename(columns={"index": "Service", "count": "Count"})
    )

    fig = px.bar(
        agg,
        x="Count",
        y="Service",
        orientation="h",
        text="Count",
        color_discrete_sequence=[VINEYARD_GREEN],
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        title="Appointments by Service Type",
        xaxis_title="Number of Appointments",
        yaxis_title="",
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(gridcolor="#f0f0f0"),
    )
    st.plotly_chart(fig, width='stretch')


def plot_virtual_vs_inperson(df: pd.DataFrame) -> None:
    """
    Shows how appointments are delivered. 
    """
    if df.empty or "Location" not in df.columns:
        st.info("No location data available.")
        return

    # Renamed for clarity
    location_map = {
        "Virtual": "Virtual",
        "Library": "In-Person",
        "PNWU Library or Virtual": "In-Person",
    }
    df = df.copy()
    df["Location"] = df["Location"].replace(location_map)

    agg = df["Location"].value_counts().reset_index()
    agg.columns = ["Location", "Count"]

    fig = px.pie(
        agg,
        names="Location",
        values="Count",
        color_discrete_sequence=[PACIFIC_BLUE, CLOUD_BLUE],
        hole=0.4,
    )
    fig.update_layout(title="Appointment Delivery Method")
    st.plotly_chart(fig, width='stretch')

def plot_bioethics_topics(df: pd.DataFrame) -> None:
    """Plots bioethics topics discussed in Book A Librarian appointments.
    """
    if df.empty:
        st.info("No data available.")
        return

    # create bioethics only dataframe
    df_bioethics = df[df['Service'] == 'ELEC 704 Bioethics']

    # create groupby object
    agg = (df_bioethics.groupby("Topic", as_index=False).size())

    # PLOTLY BARPLOT VERSION
    labels = {'Topic':'Bioethics Topic', 'size':'Number of Bookings'}
    fig = px.bar(agg, x="Topic", y="size", labels=labels, title='Number of Bookings by Bioethics Topic',
                 color_discrete_sequence=[FOREST_GREEN])
    fig.update_xaxes(tickangle=45)

    st.plotly_chart(fig, width='stretch')

def plot_satisfaction_means(df: pd.DataFrame, year: int) -> None:
    """
    How satisfied are students with each area of the library?
    Scores are 0-5. The dotted line at 3.0 is neutral — anything
    below that line is a problem worth paying attention to.
    Green = strong, yellow = okay, red = needs work.
    """
    if df.empty:
        st.info(f"No satisfaction data available for {year}.")
        return

    question_cols = [
        c for c in df.columns
        if c not in ["LevelName", "SurveyStart", "SurveyEnd",
                     "Enrollments", "Respondents", "ResponseRate",
                     "Survey Year"]
    ]

    means = df[question_cols].mean().reset_index()
    means.columns = ["Question", "Mean Score"]
    means = means.sort_values("Mean Score", ascending=True)

    means["Color"] = means["Mean Score"].apply(
        lambda x: FOREST_GREEN if x >= 3.5
        else CLOUD_BLUE if x >= 3.0
        else WARNING_RED
    )
    

    fig = go.Figure(go.Bar(
        x=means["Mean Score"],
        y=means["Question"],
        orientation="h",
        marker_color=means["Color"],
        text=means["Mean Score"].round(2),
        textposition="outside",
    ))

    fig.add_vline(
        x=3.0,
        line_dash="dot",
        line_color=BALANCE_GRAY,
        annotation_text="Neutral (3.0)",
        annotation_position="top",
    )

    fig.update_layout(
        title=f"Student Satisfaction by Category — {year}",
        xaxis_title="Mean Score (0–5)",
        yaxis_title="",
        xaxis=dict(range=[0, 5.5], gridcolor="#f0f0f0"),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    with st.container():
        st.plotly_chart(fig, width='stretch')
        st.markdown(
            '<small>'
            '<span style="color:#366732;">■</span> Strong (3.5+) &nbsp;·&nbsp; '
            '<span style="color:#72c7f0;">■</span> Neutral (3.0–3.5) &nbsp;·&nbsp; '
            '<span style="color:#c0392b;">■</span> Needs attention (below 3.0)'
            '</small>',
            unsafe_allow_html=True
        )

def plot_satisfaction_comparison(df: pd.DataFrame) -> None:
    """
    Did things get better or worse between 2023 and 2025?
    Both years side by side so you can see exactly
    where scores went up, stayed flat, or dropped.
    """
    if df.empty or "Survey Year" not in df.columns:
        st.info("No comparison data available.")
        return

    question_cols = [
        c for c in df.columns
        if c not in ["LevelName", "SurveyStart", "SurveyEnd",
                     "Enrollments", "Respondents", "ResponseRate",
                     "Survey Year"]
    ]

    melted = df.melt(
        id_vars=["Survey Year"],
        value_vars=question_cols,
        var_name="Question",
        value_name="Score",
    )
    means = melted.groupby(
        ["Survey Year", "Question"], as_index=False
    )["Score"].mean()
    means["Survey Year"] = means["Survey Year"].astype(str)

    fig = px.bar(
        means,
        x="Question",
        y="Score",
        color="Survey Year",
        barmode="group",
        color_discrete_map={"2023": PACIFIC_BLUE, "2025": NEW_LEAF},
    )
    fig.update_layout(
        title="Satisfaction Scores: 2023 vs 2025",
        xaxis_title="",
        yaxis_title="Mean Score (0–5)",
        xaxis=dict(tickangle=30),
        yaxis=dict(range=[0, 5.5], gridcolor="#f0f0f0"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend_title="Survey Year",
    )
    st.plotly_chart(fig, width='stretch')

def plot_circulation(df: pd.DataFrame, metric: str) -> None:
    """
    Physical book checkouts by month over time.
    Tells a story of how students are using the library
    """
    names = {
        "Checkout": "Checkouts",
        "Checkin": "Checkins",
        "Renew": "Renewals",
        "Hold": "Holds",
        "Lost": "Items Lost",
        "Found": "Items Found"
    }


    if df.empty:
        st.info("No circulation data available.")
        return

    fig = px.line(
        df,
        x="Month",
        y=f"{metric}",
        color="AcademicYear",
        markers=True,
        color_discrete_sequence=[PACIFIC_BLUE, FOREST_GREEN, VINEYARD_GREEN, NEW_LEAF],
    )
    fig.update_layout(
        title=f"Physical Book {names[metric]} by Month",
        xaxis_title="Month",
        yaxis_title=f"{names[metric]}",
        plot_bgcolor="white",
        paper_bgcolor="white",
        yaxis=dict(gridcolor="#f0f0f0"),
        legend_title="Academic Year",
    )
    st.plotly_chart(fig, width='stretch')


def plot_circulation_by_year(df: pd.DataFrame, metric: str) -> None:
    """
    Total physical checkouts per academic year as a bar chart
    """
    names = {
        "Checkout": "Checkouts",
        "Checkin": "Checkins",
        "Renew": "Renewals",
        "Hold": "Holds",
        "Lost": "Items Lost",
        "Found": "Items Found"
    }
    if df.empty:
        st.info("No circulation data available.")
        return

    agg = df.groupby("AcademicYear", as_index=False)[f"{metric}"].sum()
    agg = agg.sort_values("AcademicYear")

    fig = px.bar(
        agg,
        x="AcademicYear",
        y=f"{metric}",
        text=f"{metric}",
        color_discrete_sequence=[FOREST_GREEN],
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        title=f"Total Physical {names[metric]} by Academic Year",
        xaxis_title="Academic Year",
        yaxis_title=f"Total {names[metric]}",
        plot_bgcolor="white",
        paper_bgcolor="white",
        yaxis=dict(gridcolor="#f0f0f0"),
    )
    st.plotly_chart(fig, width='stretch')

def plot_costs_sum_per_student(df: pd.DataFrame) -> None:
    '''
    Bar chart plotting cost per student per academic year
    '''

    if df.empty or "AY21-22" not in df.columns:
        st.info("No cost per student data available.")
        return

    df.set_index('Resource', inplace = True)

    costs_df = pd.Series(
        df.loc['TOTAL PER STUDENT'].values, # the cost
        df.loc['TOTAL PER STUDENT'].index # the academic year
    )

    fig = px.bar(
        costs_df,
        x = costs_df.index,
        y = costs_df.values,
        orientation = "v",
        color_discrete_sequence=[VINEYARD_GREEN]
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        title="Cost per Student by Academic Year",
        xaxis_title="Academic Year",
        yaxis_title="Dollars",
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(gridcolor="#f0f0f0"),
    )

    st.plotly_chart(fig, width='stretch')

    return

def plot_costs_by_resource(df: pd.DataFrame) -> None:
    '''
    Bar chart plotting cost per student per resource per academic year
    '''

    if df.empty or "AY21-22" not in df.columns:
        st.info("No cost per student data available.")
        return

    st.info("Cost by Resource coming soon.")

    return

def plot_avg_NPS(df: pd.DataFrame) -> None:
    """
    Bar chart plotting the average Net Promoter Score for each of the three Impact Survey respondent groups (Students, Faculty, and Admin).
    """
    if df.empty:
        st.info("No appointment data available.")
        return

    labels = {'group':'Respondent Group','scores':'NPS Score (0-10)'}
    fig = px.bar(df, x='group', y='scores', labels=labels, color = 'group', color_discrete_map={
    'Students':FOREST_GREEN,
    'Faculty':VINEYARD_GREEN,
    'Admin':PACIFIC_BLUE
    }, text_auto=True)
    fig.add_hline(y=7, line_dash='dash', annotation_text="Passive threshold (7) ",
              annotation_position="top right")

    st.plotly_chart(fig, width='stretch')

def plot_impact_satisfaction_ratings(df):
    """
    Horizontal bar chart plotting key satisfaction ratings across the three Imapct Survey respondent groups (Students, Faculty, and Admin).
    """
    if df.empty:
        st.info("No appointment data available.")
        return

    labels = {'rating':'Rating','scores':'Mean Score (1-5)'}
    fig = px.bar(df, x='scores', y='rating', labels=labels, color = 'rating', color_discrete_map={
    'Data Support Effectiveness (Admin)':CLOUD_BLUE,
    'Health Info Confidence (Students)':NEW_LEAF,
    'Collection Support (Faculty)':VINEYARD_GREEN,
    'Research Materials Satisfaction (Faculty)':FOREST_GREEN,
    'Course Materials Satisfaction (Faculty)':PACIFIC_BLUE
    }, text_auto=True)

    st.plotly_chart(fig, width='stretch')

## FUTURE ADDITIONS - Student Learning Outcomes

# Edit & complete this section and un-comment this code block when you are ready to add Student Learning Outcomes data to the dashboard.
# Use the dummy code below as a jumping-off point to write visualization plotting functions for Student Learning Outcomes data.

# def plot_student_learning_outcomes(df: pd.DataFrame) -> None:
    # if df.empty:
        # st.info("No circulation data available.")
        # return

    # [INSERT VISUALIZATION PLOT CODE HERE]

    # st.plotly_chart(fig, width='stretch')
