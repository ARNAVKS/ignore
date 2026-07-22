import streamlit as st
from backend import check_food, FoodVerdict

st.set_page_config(
    page_title="Food Health Checker",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- sidebar ----------------
with st.sidebar:
    st.title("🥗 Food Health Checker")
    st.caption("LLM-powered nutrition report generator")
    st.divider()

    food_name = st.text_input("Enter food name", placeholder="e.g. Maggi, Paneer Butter Masala, Oats")
    check_btn = st.button("Check Food", type="primary", use_container_width=True)

    st.divider()


# ---------------- main ----------------
st.title("Food Health Report")
st.caption("Enter a food item in the sidebar to get a structured health verdict.")

if check_btn:
    if not food_name.strip():
        st.warning("Please enter a food name first.")
    else:
        with st.spinner(f"Analyzing '{food_name}'..."):
            try:
                verdict: FoodVerdict = check_food(food_name.strip())
                st.session_state.last_verdict = verdict
            except Exception as e:
                st.error(f"Failed to generate report: {e}")

# ---------------- report display ----------------
verdict = st.session_state.get("last_verdict")

if verdict:
    if not verdict.is_valid:
        st.subheader(verdict.food_name)
        st.error(f"⚠️ Invalid input: {verdict.reasoning}")
    else:
        status_color = "green" if verdict.is_healthy else "red"
        status_label = "HEALTHY" if verdict.is_healthy else "UNHEALTHY"

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.subheader(verdict.food_name)
        with col2:
            st.metric("Verdict", status_label)
        with col3:
            st.markdown(
                f"<div style='padding:10px;border-radius:8px;background-color:{status_color};"
                f"color:white;text-align:center;font-weight:bold;'>"
                f"{'✅ Good choice' if verdict.is_healthy else '⚠️ Needs attention'}</div>",
                unsafe_allow_html=True,
            )

        st.divider()

        st.markdown("### 🧠 Reasoning")
        st.write(verdict.reasoning)

        if not verdict.is_healthy:
            if verdict.recommendation:
                st.markdown("### 💡 Recommendation")
                st.info(verdict.recommendation)

            if verdict.healthier_alternatives:
                st.markdown("### 🔄 Healthier Alternatives")
                for alt in verdict.healthier_alternatives:
                    st.markdown(f"- {alt}")

else:
    st.info("Enter a food name in the sidebar and click 'Check Food' to see the report here.")