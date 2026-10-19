import streamlit as st

# Configure the Streamlit application page
st.set_page_config(
    page_title="Quantum-Readiness Risk Score",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

def main():
    st.title("Quantum-Readiness Risk Score")
    st.markdown(
        """
        Welcome to the **Quantum-Readiness Risk Score for Bank Cryptographic Assets** platform.
        
        Use the sidebar to navigate between modules:
        - **Asset Inventory:** View and manage cryptographic assets.
        - **Risk Heatmap:** Explore algorithm vulnerability and exposure.
        - **Migration Roadmap:** Plan transition timelines to Post-Quantum Cryptography (PQC).
        - **Scenario Simulator:** Simulate quantum breakthrough timelines and cost impacts.
        - **Asset Detail:** Deep-dive into individual asset cryptographic specifications.
        """
    )

if __name__ == "__main__":
    main()
