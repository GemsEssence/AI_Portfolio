# app/webapp.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from src.pipeline.orchestrator import SafetyOrchestrator

st.set_page_config(page_title="AI Safety Demo", layout="centered")

# Sidebar configuration
st.sidebar.header("⚙️ Configuration")
age = st.sidebar.number_input("User Age", min_value=7, max_value=99, value=16)

# Orchestrator
orch = SafetyOrchestrator(user_age=age)

# Title
st.title("AI Safety Models POC")
st.write("Test classification with multiple AI Safety filters")

# Chat input
user_input = st.text_area("💬 Enter a message:")

def render_outputs(outputs):
    st.subheader("🔎 Model Outputs")

    # Iterate through all modules
    for module_name, result in outputs.items():
        if module_name == "action":
            continue  # skip final action for separate section

        with st.expander(f"📌 {module_name.title()}"):
            label = result["label"]
            details = result.get("details", "")

            # Color-coded labels
            if label in ["abusive", "crisis", "escalated", "deny"]:
                st.error(f"**{label.upper()}**")
            elif label in ["warn"]:
                st.warning(f"**{label.upper()}**")
            elif label in ["allow", "none", "stable"]:
                st.success(f"**{label.upper()}**")
            else:
                st.info(f"**{label.upper()}**")

            st.caption(details)

    # Final Action
    st.subheader("✅ Final Action")
    action = outputs["action"]["label"]
    details = outputs["action"]["details"]

    if action == "warn":
        st.warning(f"⚠️ Action: **{action.upper()}** \n\n_{details}_")
    elif action == "block":
        st.error(f"🛑 Action: **{action.upper()}** \n\n_{details}_")
    else:
        st.success(f"🟢 Action: **{action.upper()}** \n\n_{details}_")

# Analyze button
if st.button("Analyze"):
    if not user_input.strip():
        st.warning("Please enter some text")
    else:
        outputs = orch.step(user_input)
        render_outputs(outputs)