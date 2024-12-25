from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from main import app, User, Message

client = TestClient(app)

def test_register_user():
    with patch('main.SessionLocal') as mock_session:
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_query = MagicMock()
        mock_db.query.return_value.filter.return_value = mock_query
        mock_query.first.return_value = None

        response = client.post("/api/users", json={"username": "testuser", "password": "testpass"})
        assert response.status_code == 200
        assert response.json() == {"message": "User registered successfully"}

def test_register_user_existing_username():
    with patch('main.SessionLocal') as mock_session:
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_query = MagicMock()
        mock_db.query.return_value.filter.return_value = mock_query
        mock_query.first.return_value = User(username="testuser", password="testpass")

        response = client.post("/api/users", json={"username": "testuser", "password": "testpass"})
        assert response.status_code == 400
        assert response.json() == {"detail": "Username already exists"}

def test_login_user_success():
    with patch('main.SessionLocal') as mock_session:
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_query = MagicMock()
        mock_db.query.return_value.filter.return_value = mock_query
        mock_query.first.return_value = User(username="testuser", password="testpass")

        response = client.post("/api/users/login", json={"username": "testuser", "password": "testpass"})
        assert response.status_code == 200
        assert response.json() == {"message": "Login successful"}

def test_login_user_invalid_credentials():
    with patch('main.SessionLocal') as mock_session:
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_query = MagicMock()
        mock_db.query.return_value.filter.return_value = mock_query
        mock_query.first.return_value = None

        response = client.post("/api/users/login", json={"username": "testuser", "password": "wrongpass"})
        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid credentials"}

def test_send_message_success():
    with patch('main.SessionLocal') as mock_session:
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_query_sender = MagicMock()
        mock_query_receiver = MagicMock()
        mock_db.query.return_value.filter.side_effect = [mock_query_sender, mock_query_receiver]
        mock_query_sender.first.return_value = User(username="sender", password="pass")
        mock_query_receiver.first.return_value = User(username="receiver", password="pass")

        response = client.post("/api/messages", json={"sender": "sender", "receiver": "receiver", "content": "Hello"})
        assert response.status_code == 200
        assert response.json() == {"message": "Message sent successfully", "message_id": mock_db.add.call_args[0][0].id}

def test_send_message_sender_not_exist():
    with patch('main.SessionLocal') as mock_session:
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_query_sender = MagicMock()
        mock_query_receiver = MagicMock()
        mock_db.query.return_value.filter.side_effect = [mock_query_sender, mock_query_receiver]
        mock_query_sender.first.return_value = None
        mock_query_receiver.first.return_value = User(username="receiver", password="pass")

        response = client.post("/api/messages", json={"sender": "sender", "receiver": "receiver", "content": "Hello"})
        assert response.status_code == 400
        assert response.json() == {"detail": "Sender does not exist"}

def test_send_message_receiver_not_exist():
    with patch('main.SessionLocal') as mock_session:
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_query_sender = MagicMock()
        mock_query_receiver = MagicMock()
        mock_db.query.return_value.filter.side_effect = [mock_query_sender, mock_query_receiver]
        mock_query_sender.first.return_value = User(username="sender", password="pass")
        mock_query_receiver.first.return_value = None

        response = client.post("/api/messages", json={"sender": "sender", "receiver": "receiver", "content": "Hello"})
        assert response.status_code == 400
        assert response.json() == {"detail": "Receiver does not exist"}
