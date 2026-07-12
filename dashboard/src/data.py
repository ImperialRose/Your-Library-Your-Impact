import pandas as pd
import streamlit as st
from pathlib import Path

# Data lives here
# Here Path() means relative to this files location
DATA_DIR = Path(__file__).parent.parent / "data"

# Book a Librarian files, used in Service Activity tab
BOOKING_DIR = "book_a_librarian"
BOOKING_FILES = [
    "Bookings Report Data AY21-22 - Deidentified.xlsx",
    "Book A Librarian Export Q1 AY22-23 - Deidentified.xlsx",
    "Book A Librarian Export Q2 AY22-23 - Deidentified.xlsx",
    "Book A Librarian Export Q3 AY22-23 - Deidentified.xlsx",
    "Book A Librarian Export Q4 AY22-23 - Deidentified.xlsx",
    "Book a Librarian Export Q1 AY23-24 - Deidentified.xlsx",
    "Book a Librarian Export Q2 AY23-24 - Deidentified.xlsx",
    "Book a Librarian Export Q3 AY23-24 - Deidentified.xlsx",
    "Book a Librarian Export Q4 AY23-24 - Deidentified.xlsx",
    "Book a Librarian Export Q1 AY24-25 - Deidentified.xlsx",
    "Book a Librarian Export Q2 AY24-25 - Deidentified.xlsx",
    "Book a Librarian Export Q3 AY24-25 - Deidentified.xlsx",
    "Book a Librarian Export Q4 AY24-25 - Deidentified.xlsx",
]

@st.cache_data(show_spinner=False)
def load_bookings() -> pd.DataFrame:
    """
    Load and combine all Book a Librarian appointment files.
    
    Returns a single dataframe with all appointments across all years,
    plus a YearQuarter column (2022 Q1) for easy grouping
    
    If a file is missing, it's silently skipped, adding new
    quarters later is easy just drop a new file in data/
    and adding its name to BOOKING_FILES
    """
    frames = []
    for fname in BOOKING_FILES:
        fpath = DATA_DIR / BOOKING_DIR / fname
        if not fpath.exists():
            continue
        df = pd.read_excel(fpath)
        frames.append(df)

    if not frames:
        return pd.DataFrame()

    combined = pd.concat(frames, ignore_index=True)

    # Parse dates so we can sort and group by time
    combined["Date"] = pd.to_datetime(combined["Date"], errors="coerce")
    combined = combined.dropna(subset=["Date"])

    # Add a Year-Quarter label for grouping in charts
    combined["YearQuarter"] = (
        combined["Date"].dt.year.astype(str)
        + " Q"
        + combined["Date"].dt.quarter.astype(str)
    )

    # Add academic year label (AY runs July-June)
    # July 2022 - June 2023 = AY22-23
    def get_academic_year(date):
        if date.month >= 7:
            return f"AY{str(date.year)[2:]}-{str(date.year+1)[2:]}"
        else:
            return f"AY{str(date.year-1)[2:]}-{str(date.year)[2:]}"

    combined["AcademicYear"] = combined["Date"].apply(get_academic_year)
    # Some files had extra spaces or diff caps
    # or making dupes, this  should clean it up
    combined["Service"] = combined["Service"].str.strip()
    combined["Location"] = combined["Location"].str.strip()
    combined["Topic"] = combined["Topic"].str.strip()
    combined["PNWU Status"] = combined["PNWU Status"].str.strip()
    combined["PNWU Academic Affiliation"] = combined["PNWU Academic Affiliation"].str.strip()

    # for bioethics topics - consolidate multiple-category topics for better visualization
    combined['Service'] = combined['Service'].replace('ELEC 704 Bioethics Consultation','ELEC 704 Bioethics')
    combined['Topic'] = combined['Topic'].replace(
        'Physician Aid-in-Dying AND Do Not Resuscitate Orders AND End-of-Life Issues AND Parental Decision Making',
        'Physician Aid in Dying')
    combined['Topic'] = combined['Topic'].replace(
        'End-of-Life Issues AND (Treatment Refusal OR Cross-Cultural Issues and Diverse Beliefs)', 'End-of-Life Issues')
    combined['Topic'] = combined['Topic'].replace('End-of-Life Issues OR Termination of Life-Sustaining Treatment',
                                                  'End-of-Life Issues')
    combined['Topic'] = combined['Topic'].replace('Public Health Ethics AND Mistakes', 'Public Health Ethics')

    # drop unnecessary columns
    combined = combined.drop(['Status', 'Program/Dept', 'Booking Id', 'Tracking Data', ' PNWU Status'], axis=1)

    return combined


# Survey data, used in General Student Satisfaction tab

SATISFACTION_DIR = "student_satisfaction"

# Separate years if diff questions

QUESTION_LABELS_2023 = {
    "Question 45": "Professionalism of Staff",
    "Question 46": "Ease of Contacting Library",
    "Question 47": "Timeliness in Responding",
    "Question 48": "Collections & Information Resources",
    "Question 49": "Adequacy of Library Space",
    "Question 50": "Library Instruction Quality",
}

QUESTION_LABELS_2025 = {
    "Question 44": "Website Easy to Navigate",
    "Question 45": "Staff Respond Promptly",
    "Question 46": "Workshops Help Me Use Research Tools",
    "Question 47": "Inclusive & Welcoming Environment",
    "Question 48": "Library Responds to Student Needs",
    "Question 49": "Contributed to My Academic Success",
    "Question 50": "Print & Digital Books Useful",
    "Question 51": "Journals Useful",
    "Question 52": "Databases Useful",
    "Question 53": "Online Guides & Tutorials Useful",
    "Question 54": "Variety & Quality Meet My Needs",
}

@st.cache_data(show_spinner=False)
def load_satisfaction(year: int) -> pd.DataFrame:
    """
    Load a student satisfaction survey by year 2023 or 2025.
    Each year asked different questions so we use different label maps.
    """
    fname = (
        f"{year} PNWU Student Satisfaction Survey"
        " - Raw Data - Library Likert-scale Questions.xlsx"
    )
    fpath = DATA_DIR / SATISFACTION_DIR / fname
    if not fpath.exists():
        return pd.DataFrame()

    df = pd.read_excel(fpath)

    # Use the right label map for each year
    labels = QUESTION_LABELS_2023 if year == 2023 else QUESTION_LABELS_2025
    df = df.rename(columns=labels)

    question_cols = list(labels.values())
    df = df.dropna(subset=question_cols, how="all")
    df["Survey Year"] = year

    return df

@st.cache_data(show_spinner=False)
def load_satisfaction_both() -> pd.DataFrame:
    """
    Loads both survey years and stacks them together.
    Used for the 2023 vs 2025 comparison chart.
    Note: only questions that appear in both years will overlap —
    the rest will show as empty for the year that didn't ask them.
    """
    df23 = load_satisfaction(2023)
    df25 = load_satisfaction(2025)
    frames = [df for df in [df23, df25] if not df.empty]
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)

# Circulation Data, used in Collection Activity tab 
# Physical book checkout data from LibraryWorld
# Extract the text and parse it into a dataframe
# Format is consistent across all years — monthly rows with
# Checkout, Checkin, Renew, In House, Hold, Lost, Found columns.

CIRCULATION_DIR = "library_world_circulation_count"

CIRCULATION_FILES = {
    "AY21-22": "Library World Circulation Count AY21-22 - Deidentified.pdf",
    "AY22-23": "Library World Circulation Count AY22-23 - Deidentified.pdf",
    "AY23-24": "Library World Circulation Count AY23-24 - Deidentified.pdf",
    "AY24-25": "Library World Circulation Count AY24-25 - Deidentified.pdf",
}

@st.cache_data(show_spinner=False)
def load_circulation() -> pd.DataFrame:
    """
    Reads all four LibraryWorld circulation PDFs and combines them
    into one dataframe with monthly checkout counts by academic year.
    """
    from pypdf import PdfReader
    import re

    all_rows = []

    for ay, fname in CIRCULATION_FILES.items():
        fpath = DATA_DIR / CIRCULATION_DIR / fname
        if not fpath.exists():
            continue

        reader = PdfReader(str(fpath))
        text = reader.pages[0].extract_text()

        # Each data line looks like: "2021-07 9 6 1 0 1 0 0"
        # Match lines starting with a year-month pattern
        for line in text.split("\n"):
            match = re.match(
                r"(\d{4}-\d{2})\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)",
                line.strip()
            )
            if match:
                all_rows.append({
                    "Month": match.group(1),
                    "Checkout": int(match.group(2)),
                    "Checkin": int(match.group(3)),
                    "Renew": int(match.group(4)),
                    "InHouse": int(match.group(5)),
                    "Hold": int(match.group(6)),
                    "Lost": int(match.group(7)),
                    "Found": int(match.group(8)),
                    "AcademicYear": ay,
                })

    if not all_rows:
        return pd.DataFrame()

    df = pd.DataFrame(all_rows)
    df["Month"] = pd.to_datetime(df["Month"], format="%Y-%m")
    df = df.sort_values("Month")
    return df

# Impact survey data, used in Qualitative Impact tab

IMPACT_DIR = "library_impact_surveys"
ADMIN_IMPACT_FILE = "admin_clean_full.csv"
FACULTY_IMPACT_FILE = "faculty_clean_full.csv"
STUDENT_IMPACT_FILE = "student_clean_full.csv"

@st.cache_data(show_spinner=False)
def load_admin_quant_data() -> pd.DataFrame:
    fname = ADMIN_IMPACT_FILE
    fpath = DATA_DIR / IMPACT_DIR / fname
    if not fpath.exists():
        return pd.DataFrame
    df = pd.read_csv(fpath)
    return df

@st.cache_data(show_spinner=False)
def load_faculty_quant_data() -> pd.DataFrame:
    fname = FACULTY_IMPACT_FILE
    fpath = DATA_DIR / IMPACT_DIR / fname
    if not fpath.exists():
        return pd.DataFrame
    df = pd.read_csv(fpath)
    return df

@st.cache_data(show_spinner=False)
def load_student_quant_data() -> pd.DataFrame:

    fname = STUDENT_IMPACT_FILE
    fpath = DATA_DIR / IMPACT_DIR / fname
    if not fpath.exists():
        return pd.DataFrame()

    df = pd.read_csv(fpath)
    return df

@st.cache_data(show_spinner=False)
def get_NPS_scores(df_admin, df_faculty, df_student) -> pd.DataFrame:
    avg_NPS_admin = round(df_admin['dashboard_use_nps_score'].mean(), 2)
    avg_NPS_faculty = round(df_faculty['library_partner_nps_score'].mean(), 2)
    avg_NPS_student = round(df_student['library_nps_score'].mean(), 2)
    NPS_scores = {'group':['Students','Faculty','Admin'], 'scores':[avg_NPS_student,avg_NPS_faculty,avg_NPS_admin]}
    df = pd.DataFrame.from_dict(NPS_scores)
    return df

@st.cache_data(show_spinner=False)
def get_impact_satisfaction_ratings(df_admin, df_faculty, df_student) -> pd.DataFrame:
    data_support_effectiveness = round(df_admin['data_support_effectiveness'].dropna().mean(), 2)
    health_info_confidence = round(df_student['health_info_confidence'].dropna().mean(), 2)
    collection_support = round(df_faculty['collection_support_rating'].dropna().mean(), 2)
    research_materials_satisfaction = round(df_faculty['research_materials_satisfaction'].dropna().mean(), 2)
    course_materials_satisfaction = round(df_faculty['course_materials_satisfaction'].dropna().mean(), 2)
    satisfaction_ratings = {'rating':['Data Support Effectiveness (Admin)','Health Info Confidence (Students)','Collection Support (Faculty)', 'Research Materials Satisfaction (Faculty)', 'Course Materials Satisfaction (Faculty)'], 'scores':[data_support_effectiveness,health_info_confidence,collection_support, research_materials_satisfaction, course_materials_satisfaction]}
    satisfaction_ratings_df = pd.DataFrame.from_dict(satisfaction_ratings)
    return satisfaction_ratings_df


# Cost data, used in Library Costs per Student tab

COSTS_DIR = "costs"
COSTS_FILE = "Collection Cost per Student FINAL.xlsx"

@st.cache_data(show_spinner=False)
def load_costs() -> pd.DataFrame:
    '''
    Loads collection cost per student data.
    Expects first column to be collection resource
    and subsequent columns to be cost per student per academic year (USD).
    '''

    fname = COSTS_FILE
    fpath = DATA_DIR / COSTS_DIR / fname
    if not fpath.exists():
        return pd.DataFrame()
    df_costs = pd.read_excel(fpath)

    return df_costs


## FUTURE ADDITIONS - Student Learning Outcomes
# Use the dummy code below as a jumping-off point to write functions for loading & cleaning student learning outcomes data.
# Edit & complete this section and un-comment this code block when you are ready to add Student Learning Outcomes data to the dashboard.

    # def load_learning_outcomes() -> pd.DataFrame:
    # '''Loads and cleans Student Learning Outcomes dataset(s).
    # '''

    ## LOAD DATA
    # fname = ("[PLACEHOLDER - Insert file name or file name pattern]")
    # fpath = DATA_DIR / fname
    # if not fpath.exists():
        # return pd.DataFrame()
    # df_learning_outcomes = pd.read_csv(fpath) --> adjust this from csv depending on file source type

    ## CLEAN DATA
    # Add any data cleaning steps required to prepare the Learning Outcomes data here

    # return df
