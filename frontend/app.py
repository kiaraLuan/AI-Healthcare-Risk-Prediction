import streamlit as st
import joblib
import pandas as pd
import sqlite3
from datetime import datetime
from pathlib import Path

# PAGE CONFIG

st.set_page_config(
    page_title="Health Risk Check",
    page_icon="🩺",
    layout="centered"
)


# PROJECT PATHS

BASE_DIR = Path(__file__).resolve().parent.parent

MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"

DB_PATH = DATA_DIR / "assessments.db"


# LOAD MODELS

@st.cache_resource
def load_models():

    chronic_model = joblib.load(
        MODELS_DIR / "chronic_model.pkl"
    )

    chronic_features = joblib.load(
        MODELS_DIR / "chronic_features.pkl"
    )

    mental_model = joblib.load(
        MODELS_DIR / "mental_model.pkl"
    )

    mental_features = joblib.load(
        MODELS_DIR / "mental_features.pkl"
    )

    return (
        chronic_model,
        chronic_features,
        mental_model,
        mental_features
    )
def get_assessment_history(assessment_type):
    conn = sqlite3.connect('data/assessments.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS assessments
        (id INTEGER PRIMARY KEY, type TEXT, result TEXT, probability REAL, timestamp TEXT)''')
    rows = conn.execute(
        "SELECT result, probability, timestamp FROM assessments WHERE type = ? ORDER BY timestamp DESC",
        (assessment_type,)
    ).fetchall()
    conn.close()
    return rows
# RISK RESULT DISPLAY

def show_risk_result(risk_label, confidence, explanation, disclaimer):
    label_lower = risk_label.lower()

    if "low" in label_lower:
        color = "#1e7e34"
        bg = "#d4edda"
        icon = "✅"
    elif "moderate" in label_lower or "at risk" in label_lower:
        color = "#856404"
        bg = "#fff3cd"
        icon = "⚠️"
    else:
        color = "#721c24"
        bg = "#f8d7da"
        icon = "🔴"

    st.markdown(
        f"""
        <div style="background-color:{bg}; border-left: 6px solid {color};
                    padding: 16px 20px; border-radius: 6px; margin-bottom: 12px;">
            <p style="color:{color}; font-size:22px; font-weight:600; margin:0;">
                {icon} {risk_label}
            </p>
            <p style="color:{color}; font-size:15px; margin:4px 0 0;">
                Confidence: {confidence}%
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write(explanation)
    st.caption(disclaimer)

# RISK EXPLANATIONS

CHRONIC_EXPLANATIONS = {
    "Low risk": "Your responses suggest a lower likelihood of diabetes-related risk based on the factors provided. Maintaining current activity levels and health checks is still worthwhile.",
    "At risk": "Your responses suggest an elevated likelihood of diabetes-related risk. Factors like blood pressure, cholesterol, and activity level contributed to this result.",
    "Moderate risk (Prediabetes)": "Your responses suggest some indicators associated with prediabetes risk. This is not a diagnosis, but may be worth discussing with a healthcare provider.",
    "High risk (Diabetes)": "Your responses align with patterns associated with higher diabetes risk. Please consider discussing these results with a healthcare professional.",
}

MENTAL_EXPLANATIONS = {
    "Low": "Your responses suggest lower levels of stress, anxiety, or depression symptoms this week.",
    "Moderate": "Your responses suggest a moderate level of stress, anxiety, or depressive symptoms. Consider checking in with yourself or someone you trust.",
    "High": "Your responses suggest a higher level of stress, anxiety, or depressive symptoms. Speaking with a mental health professional could help.",
}

CHRONIC_DISCLAIMER = "This is not a medical diagnosis. Please consult a healthcare professional for concerns about your health."

MENTAL_DISCLAIMER = "This is not a clinical diagnosis. If you're struggling, please consider speaking with a mental health professional."


CHRONIC_RANK = {"Low risk": 0, "Moderate risk (Prediabetes)": 1, "High risk (Diabetes)": 2, "At risk": 1}
MENTAL_RANK = {"Low risk": 0, "Moderate risk": 1, "High risk": 2}

def compare_trend(current_rank, previous_rank):
    if current_rank < previous_rank:
        return "improving", "🟢"
    elif current_rank > previous_rank:
        return "increasing", "🔴"
    else:
        return "stable", "🟡"
(
    chronic_model,
    chronic_features,
    mental_model,
    mental_features
) = load_models()


# DATABASE

def initialize_database():

    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            result TEXT NOT NULL,
            probability REAL,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


initialize_database()


# BRFSS AGE GROUP MAPPING

AGE_GROUPS = {
    "18–24": 1,
    "25–29": 2,
    "30–34": 3,
    "35–39": 4,
    "40–44": 5,
    "45–49": 6,
    "50–54": 7,
    "55–59": 8,
    "60–64": 9,
    "65–69": 10,
    "70–74": 11,
    "75–79": 12,
    "80+": 13
}


# DASS-21 QUESTIONS

DASS_QUESTIONS = [
    "I found it hard to wind down.",
    "I was aware of dryness of my mouth.",
    "I couldn't seem to experience any positive feeling at all.",
    "I experienced breathing difficulty (e.g. excessively rapid breathing, breathlessness in the absence of physical exertion).",
    "I found it difficult to work up the initiative to do things.",
    "I tended to over-react to situations.",
    "I experienced trembling (e.g. in the hands).",
    "I felt that I was using a lot of nervous energy.",
    "I was worried about situations in which I might panic and make a fool of myself.",
    "I felt that I had nothing to look forward to.",
    "I found myself getting agitated.",
    "I found it difficult to relax.",
    "I felt down-hearted and blue.",
    "I was intolerant of anything that kept me from getting on with what I was doing.",
    "I felt I was close to panic.",
    "I was unable to become enthusiastic about anything.",
    "I felt I wasn't worth much as a person.",
    "I felt that I was rather touchy.",
    "I was aware of the action of my heart in the absence of physical exertion.",
    "I felt scared without any good reason.",
    "I felt that life was meaningless."
]


DASS_OPTIONS = {
    0: "Did not apply to me at all",
    1: "Applied to me to some degree, or some of the time",
    2: "Applied to me to a considerable degree, or a good part of time",
    3: "Applied to me very much, or most of the time"
}

# SESSION STATE
if "screen" not in st.session_state:
    st.session_state.screen = "landing"


def go_to(screen_name):
    st.session_state.screen = screen_name

# SIDEBAR

with st.sidebar:

    st.title("🩺 Health Risk Check")

    st.radio(
        "Assessment type",
        [
            "Landing",
            "Chronic Health",
            "Mental Health",
            "History"
        ],
        key="nav_choice",
        on_change=lambda: go_to(
            st.session_state.nav_choice.lower().replace(" ", "_")
        )
    )


# LANDING PAGE

if st.session_state.screen == "landing":

    st.title("Health Risk Check")

    st.write(
        "Welcome to the AI-based health risk assessment system."
    )

    st.write(
        "Choose an assessment below to get started."
    )

    st.info(
        "This system provides a risk indicator based on "
        "self-reported information. It is not a medical diagnosis."
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🫀 Chronic Health Check",
            use_container_width=True
        ):

            go_to("chronic_health")
            st.rerun()

    with col2:

        if st.button(
            "🧠 Mental Health Check",
            use_container_width=True
        ):

            go_to("mental_health")
            st.rerun()


# CHRONIC HEALTH ASSESSMENT

elif st.session_state.screen == "chronic_health":

    st.header("Chronic Health Assessment")

    high_bp = st.selectbox(
        "High blood pressure?",
        ["No", "Yes"]
    )

    high_chol = st.selectbox(
        "High cholesterol?",
        ["No", "Yes"]
    )

    bmi = st.number_input(
        "BMI",
        min_value=10.0,
        max_value=70.0,
        value=25.0,
        step=0.1
    )

    smoker = st.selectbox(
        "Smoker?",
        ["No", "Yes"]
    )

    phys_activity = st.selectbox(
        "Physically active in the last 30 days?",
        ["No", "Yes"]
    )

    gen_health = st.slider(
        "General health (1 = excellent, 5 = poor)",
        1,
        5,
        3
    )

    age_range = st.selectbox(
        "Age group",
        list(AGE_GROUPS.keys())
    )

    sex = st.selectbox(
        "Sex",
        ["Female", "Male"]
    )


    if st.button(
        "Get my result",
        type="primary"
    ):
        errors = []

        if bmi < 10 or bmi > 70:
            errors.append("BMI must be between 10 and 70.")

        if errors:
            for e in errors:
                st.error(e)
            st.stop()

        input_dict = {

            "HighBP":
                1 if high_bp == "Yes" else 0,

            "HighChol":
                1 if high_chol == "Yes" else 0,

            "BMI":
                bmi,

            "Smoker":
                1 if smoker == "Yes" else 0,

            "PhysActivity":
                1 if phys_activity == "Yes" else 0,

            "GenHlth":
                gen_health,

            "Age":
                AGE_GROUPS[age_range],

            "Sex":
                1 if sex == "Male" else 0,
        }


        input_row = pd.DataFrame(
            [
                [
                    input_dict[col]
                    for col in chronic_features
                ]
            ],
            columns=chronic_features
        )


        prediction = chronic_model.predict(
            input_row
        )[0]

        probabilities = chronic_model.predict_proba(
            input_row
        )[0]

        confidence = round(
            max(probabilities) * 100,
            1
        )


        if len(chronic_model.classes_) == 2:

            label_map = {
                0: "Low risk",
                1: "At risk"
            }

        else:

            label_map = {
                0: "Low risk",
                1: "Moderate risk (Prediabetes)",
                2: "High risk (Diabetes)"
            }


        risk_label = label_map.get(
            prediction,
            str(prediction)
        )


        st.session_state.last_chronic_result = {
            "label": risk_label,
            "confidence": confidence
        }

        explanation = CHRONIC_EXPLANATIONS.get(risk_label, "")
        show_risk_result(
            risk_label,
            confidence,
            explanation,
            CHRONIC_DISCLAIMER
        )


        conn = sqlite3.connect(DB_PATH)

        conn.execute(
            """
            INSERT INTO assessments
            (type, result, probability, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (
                "chronic",
                risk_label,
                confidence,
                datetime.now().isoformat()
            )
        )

        conn.commit()
        conn.close()


# MENTAL HEALTH ASSESSMENT

elif st.session_state.screen == "mental_health":

    st.header("Mental Health Check-In")

    st.write(
        "Please answer the following 21 questions "
        "based on how you have been feeling recently."
    )

    st.info(
        "Each question uses the standard DASS-21 response scale."
    )


    # DEMOGRAPHIC INFORMATION

    st.subheader("Basic Information")

    age = st.number_input(
        "Age",
        min_value=18,
        max_value=100,
        value=21,
        step=1
    )


    gender = st.selectbox(
        "Gender",
        ["Female", "Male"]
    )


    # DASS QUESTIONS

    st.subheader("DASS-21 Questionnaire")


    mental_answers = {}


    for i, question in enumerate(
        DASS_QUESTIONS
    ):

        column_name = mental_features[i]

        mental_answers[column_name] = st.selectbox(
            f"{i + 1}. {question}",
            options=list(DASS_OPTIONS.keys()),
            format_func=lambda x: DASS_OPTIONS[x],
            key=f"dass_{i}"
        )


    # PREDICTION

    if st.button(
        "Get my mental health result",
        type="primary"
    ):
        errors = []

        if age < 10 or age > 100:
           errors.append("Age must be between 10 and 100.")

        if errors:
            for e in errors:
                st.error(e)
            st.stop()

        input_dict = {}


        # Add all 21 DASS responses
        for question_col in mental_features[:21]:

            input_dict[question_col] = mental_answers[
                question_col
            ]


        # Add Age
        input_dict["Age"] = age


        input_dict["Gender"] = (
    1 if gender == "Female" else 0
)


        # Ensure EXACT feature order
        input_row = pd.DataFrame(
            [
                [
                    input_dict[col]
                    for col in mental_features
                ]
            ],
            columns=mental_features
        )


        # Make prediction
        prediction = mental_model.predict(
            input_row
        )[0]


        probabilities = mental_model.predict_proba(
            input_row
        )[0]


        confidence = round(
            max(probabilities) * 100,
            1
        )


        # DISPLAY RESULT

        if prediction == "Low":
            result_label = "Low risk"

        elif prediction == "Moderate":
            result_label = "Moderate risk"

        else:
            result_label = "High risk"

        explanation = MENTAL_EXPLANATIONS.get(prediction, "")
        show_risk_result(
            result_label,
            confidence,
            explanation,
            MENTAL_DISCLAIMER
        )


        # SAVE RESULT

        conn = sqlite3.connect(DB_PATH)

        conn.execute(
            """
            INSERT INTO assessments
            (type, result, probability, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (
                "mental",
                result_label,
                confidence,
                datetime.now().isoformat()
            )
        )

        conn.commit()
        conn.close()


# HISTORY

elif st.session_state.screen == "history":
    st.header("History")

    tab1, tab2 = st.tabs(["Chronic Health", "Mental Health"])

    with tab1:
        chronic_history = get_assessment_history("chronic")
        if not chronic_history:
            st.info("No chronic health assessments yet. Complete one to see your history here.")
        else:
            st.subheader("Past assessments")
            for result, probability, timestamp in chronic_history:
                ts_display = timestamp.split("T")[0] + " " + timestamp.split("T")[1][:5]
                st.write(f"**{ts_display}** — {result} ({probability}% confidence)")

            if len(chronic_history) >= 2:
                latest_result, latest_prob, _ = chronic_history[0]
                previous_result, previous_prob, _ = chronic_history[1]

                latest_rank = CHRONIC_RANK.get(latest_result, 0)
                previous_rank = CHRONIC_RANK.get(previous_result, 0)
                trend, icon = compare_trend(latest_rank, previous_rank)

                st.markdown("---")
                st.subheader("Trend")
                st.write(f"{icon} Your chronic health risk appears to be **{trend}** compared to your last assessment.")
            else:
                st.caption("Complete a second assessment to see a trend comparison.")

    with tab2:
        mental_history = get_assessment_history("mental")
        if not mental_history:
            st.info("No mental health assessments yet. Complete one to see your history here.")
        else:
            st.subheader("Past assessments")
            for result, probability, timestamp in mental_history:
                ts_display = timestamp.split("T")[0] + " " + timestamp.split("T")[1][:5]
                st.write(f"**{ts_display}** — {result} ({probability}% confidence)")

            if len(mental_history) >= 2:
                latest_result, latest_prob, _ = mental_history[0]
                previous_result, previous_prob, _ = mental_history[1]

                latest_rank = MENTAL_RANK.get(latest_result, 0)
                previous_rank = MENTAL_RANK.get(previous_result, 0)
                trend, icon = compare_trend(latest_rank, previous_rank)

                st.markdown("---")
                st.subheader("Trend")
                st.write(f"{icon} Your mental health risk appears to be **{trend}** compared to your last assessment.")
            else:
                st.caption("Complete a second assessment to see a trend comparison.")

# FALLBACK

else:

    st.session_state.screen = "landing"
    st.rerun()