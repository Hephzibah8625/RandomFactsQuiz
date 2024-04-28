import pytest
from unittest.mock import patch, MagicMock
from app.app import show_login_form, User, session, show_quiz, fetch_questions, play_quiz

@patch('requests.post', return_value=MagicMock(status_code=200, json=MagicMock(return_value={'results': 'test_questions'})))
def test_fetch_questions(mock_post):
    result = fetch_questions(5)
    assert result == 'test_questions'
    mock_post.assert_called_once_with('https://opentdb.com/api.php?amount=5&type=boolean')

@patch('requests.post', return_value=MagicMock(status_code=404))
def test_fail_fetch_questions(mock_post):
    result = fetch_questions(5)
    assert result is None
    mock_post.assert_called_once_with('https://opentdb.com/api.php?amount=5&type=boolean')

@patch('app.app.st')
def test_show_quiz(mock_st):
    mock_st.button.return_value = True

    mock_st.session_state.user_id = 'test_username'
    mock_st.session_state.quiz_started = False

    show_quiz()

    assert mock_st.session_state.quiz_started == True

@patch('app.app.st')
@patch('app.app.on_radio_click')
def test_play_quiz(mock_on_radio_click, mock_st):
    mock_st.header.side_effect = None
    mock_st.write.side_effect = None
    mock_st.radio.return_value = 'True'

    questions = [
        {"question": "Test question 1", "correct_answer": "True"},
        {"question": "Test question 2", "correct_answer": "False"},
        {"question": "Test question 3", "correct_answer": "True"}
    ]
    play_quiz(questions)

    mock_st.header.assert_called()
    mock_st.write.assert_called()
    mock_st.radio.assert_called()
    mock_on_radio_click.assert_called()

@patch('app.app.st')
@patch('app.app.on_radio_click')
def test_quiz_completed(mock_on_radio_click, mock_st):
    mock_st.header.side_effect = None
    mock_st.write.side_effect = None
    mock_st.radio.side_effect = ['True', 'False', 'True']

    questions = [
        {"question": "Test question 1", "correct_answer": "True"},
        {"question": "Test question 2", "correct_answer": "False"},
        {"question": "Test question 3", "correct_answer": "True"}
    ]

    play_quiz(questions)

    mock_st.success.assert_called()
    mock_st.header.assert_called()
    mock_st.write.assert_called()
    mock_st.radio.assert_called()
    mock_on_radio_click.assert_called()

@patch('app.app.st')
def test_sign_in(mock_st):
    mock_st.sidebar.selectbox.return_value = 'Sign In'
    show_login_form()
    mock_st.button.assert_called_with(("Login"))
