import streamlit as st
from database import create_user, login_user, get_or_create_demo_user


def authentication_page():
    st.markdown("<h1 style='text-align: center; margin-bottom: 0.2rem;'>Budget Buddy</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; margin-bottom: 2rem;'>Personal Expense Tracking and Dataset Analysis</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        tab_login, tab_signup, tab_demo = st.tabs(["Sign In", "Sign Up", "Demo Access"])

        with tab_login:
            st.markdown("### Account Login")
            email = st.text_input("Email Address", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")

            if st.button("Sign In", use_container_width=True):
                if not email or not password:
                    st.error("Please enter your email and password.")
                else:
                    user = login_user(email.strip(), password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_id = user[0]
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")

        with tab_signup:
            st.markdown("### Create Account")
            new_email = st.text_input("Email Address", key="signup_email")
            new_password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")

            if st.button("Create Account", use_container_width=True):
                if not new_email or not new_password:
                    st.error("Please provide both email and password.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(new_password) < 4:
                    st.error("Password must contain at least 4 characters.")
                else:
                    success = create_user(new_email.strip(), new_password)
                    if success:
                        st.success("Account created successfully. Please sign in.")
                    else:
                        st.error("An account with this email address already exists.")

        with tab_demo:
            st.markdown("### Instant Access")
            st.write("Explore Budget Buddy with a pre-configured profile without registration.")
            if st.button("Launch Demo Account", use_container_width=True):
                demo_user = get_or_create_demo_user()
                st.session_state.logged_in = True
                st.session_state.user_id = demo_user[0]
                st.rerun()
