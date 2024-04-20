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

    menu = st.selectbox('Menu', ['Sign In', 'Sign Up'])

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
                    if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                        st.success(f'Welcome back, {username}!')
                        st.session_state["user_id"] = user.username
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
                existing_user = session.query(User).filter_by(username=new_username).first()
                
                if existing_user:
                    st.error('Username already exists. Please choose a different username.')
                else:
                    # Hash and salt the password
                    salt = bcrypt.gensalt()
                    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)
            
                    # Insert the new user into the database
                    new_user = User(username=new_username, password=hashed_password.decode('utf-8'))
                    session.add(new_user)
                    session.commit()
                    st.success('You have successfully signed up!')
                    st.session_state["user_id"] = new_user.username
            else:
                st.error("Empty input value.")


def show_quiz():
    if "quiz_started" not in st.session_state:
        st.session_state.quiz_started = False

    if not st.session_state.quiz_started:
        number_of_questions = st.number_input("Number of Questions:", min_value=1, max_value=10, value=5, step=1)
        if st.button("Start Quiz"):
            st.session_state.quiz_started = True
            st.session_state.questions = fetch_questions(number_of_questions)

    if st.session_state.quiz_started:
        answers = play_quiz(st.session_state.questions)
        if st.button('Submit'):
            score = answers.count(True)
            st.success(f"Quiz completed! Your Score: {score}")
            st.session_state.quiz_started = False  # Reset the quiz state
            #    st.session_state.pop("user_id")  # Logout the user after completing the quiz

def fetch_questions(number: int):
    response = requests.post(f"https://opentdb.com/api.php?amount={number}&type=boolean")
    if response.status_code == 200:
        return response.json()['results']
    else:
        st.error("Failed to fetch questions.")
        return None

def play_quiz(questions):
    answers = []
    for i, question in enumerate(questions):
        st.header(f"Question {i+1}:")
        st.write(question["question"])
        answer = st.radio("Your Answer:", ["True", "False"], key=i+1)
        answers.append(answer.lower() == question['correct_answer'].lower())
    return answers

if __name__ == "__main__":
    main()
