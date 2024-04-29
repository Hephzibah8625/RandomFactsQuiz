from os.path import exists
import streamlit as st
import requests
import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String

DATABASE_FILENAME = 'user.db'

if not exists(DATABASE_FILENAME):
    open(DATABASE_FILENAME, 'w').close()

# Create a SQLAlchemy engine
engine = create_engine(f'sqlite:///{DATABASE_FILENAME}')
Session = sessionmaker(bind=engine)
session = Session()

# Create a SQLAlchemy base model
Base = declarative_base()

# Define a User model


class User(Base):
    __tablename__ = 'users'
    username = Column(String, primary_key=True)
    password = Column(String)


Base.metadata.create_all(engine)


def main():
    st.title("Random Facts Quiz")

    # Initialize the session state if it doesn't exist
    if "user_id" not in st.session_state:
        st.session_state.user_id = None

    # Check if the user is logged in
    if st.session_state.user_id is None:
        show_login_form()
    else:
        show_quiz()


def show_login_form():

    menu = st.sidebar.selectbox('Menu', ['Sign In', 'Sign Up'])

    if menu == 'Sign In':
        st.header("Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if len(username) > 0 and len(password) > 0:
                # Retrieve the user from the database
                user = session.query(User).filter_by(username=username).first()

                if user:
                    # Verify the password
                    if bcrypt.checkpw(
                            password.encode('utf-8'),
                            user.password.encode('utf-8')):
                        st.session_state["user_id"] = user.username
                        st.rerun()
                    else:
                        st.error('Invalid username or password.')
                else:
                    st.error('Invalid username or password.')
            else:
                st.error('Empty input value.')
    else:
        st.header("Registration")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        if st.button("Register"):
            if len(new_password) > 0 and len(new_username) > 0:
                # Check if the username already exists
                existing_user = session.query(User).filter_by(
                    username=new_username).first()

                if existing_user:
                    st.error(
                        'Username already exists.' +
                        ' Please choose a different username.')
                else:
                    # Hash and salt the password
                    salt = bcrypt.gensalt()
                    hashed_password = bcrypt.hashpw(
                        new_password.encode('utf-8'), salt)

                    # Insert the new user into the database
                    new_user = User(
                        username=new_username,
                        password=hashed_password.decode('utf-8'))
                    session.add(new_user)
                    session.commit()
                    st.session_state["user_id"] = new_user.username
                    st.rerun()
            else:
                st.error("Empty input value.")


def show_quiz():
    st.header(f"Welcome, {st.session_state.user_id}")
    if st.button("Logout"):
        st.session_state.pop("user_id")  # Logout the user
        if "quiz_started" in st.session_state:
            del st.session_state.quiz_started
        if "questions" in st.session_state:
            del st.session_state.questions
        if "correct_answers" in st.session_state:
            del st.session_state.correct_answers
        if "completed_questions" in st.session_state:
            del st.session_state.completed_questions
        st.rerun()

    if "quiz_started" not in st.session_state:
        st.session_state.quiz_started = False

    if not st.session_state.quiz_started:
        number_of_questions = st.number_input(
            "Number of Questions:", min_value=1, max_value=10, value=5, step=1)
        if st.button("Start Quiz"):
            st.session_state.quiz_started = True
            st.session_state.questions = fetch_questions(number_of_questions)
            st.session_state.correct_answers = 0
            st.session_state.completed_questions = 0
            st.rerun()

    if st.session_state.quiz_started:
        play_quiz(st.session_state.questions)
        if st.session_state.completed_questions == len(
                st.session_state.questions):
            st.success(
                f"Quiz completed! Your Score: {
                    st.session_state.correct_answers}")
            if st.button("Play Again"):
                st.session_state.quiz_started = False
                st.session_state.correct_answers = 0
                st.session_state.completed_questions = 0
                st.rerun()


def fetch_questions(number: int):
    response = requests.post(
        f"https://opentdb.com/api.php?amount={number}&type=boolean")
    if response.status_code == 200:
        return response.json()['results']
    else:
        st.error("Failed to fetch questions.")
        return None


def play_quiz(questions):
    for i, question in enumerate(questions):
        st.header(f"Question {i + 1}:")
        st.write(question["question"])
        answer = st.radio(
            "Your Answer:", ["True", "False"],
            None, key=i + 1, on_change=on_radio_click(questions))

        if answer is not None:
            if answer.lower() == question['correct_answer'].lower():
                st.success("Correct!")
            else:
                st.error(
                    f"Incorrect! Correct answer: {
                        question['correct_answer']}")


def on_radio_click(questions):
    st.session_state.correct_answers = 0
    st.session_state.completed_questions = 0

    for i, question in enumerate(questions):
        key = i + 1

        if key in st.session_state and st.session_state[key] is not None:
            if st.session_state[key].lower(
            ) == question['correct_answer'].lower():
                st.session_state.correct_answers += 1

            st.session_state.completed_questions += 1


if __name__ == "__main__":
    main()
