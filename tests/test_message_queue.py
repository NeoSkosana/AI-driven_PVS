"""Tests for RabbitMQ message queue implementation."""
import pytest
from unittest.mock import Mock, patch, call
import pika
from src.queue.message_queue import MessageQueue

@pytest.fixture
def mock_pika_connection():
    """Create a mock pika connection."""
    with patch('pika.BlockingConnection') as mock:
        mock_conn = Mock()
        mock_channel = Mock()
        mock_conn.channel.return_value = mock_channel
        mock.return_value = mock_conn
        yield mock

@pytest.fixture
def message_queue(mock_pika_connection):
    """Create a MessageQueue instance with mocked connection."""
    return MessageQueue()

def test_connect(message_queue, mock_pika_connection):
    """Test connecting to RabbitMQ."""
    result = message_queue.connect()
    assert result is True
    mock_pika_connection.assert_called_once()

def test_declare_queue(message_queue, mock_pika_connection):
    """Test queue declaration."""
    message_queue.connect()
    result = message_queue.declare_queue("test_queue")
    
    assert result is True
    message_queue.channel.queue_declare.assert_called_once_with(
        queue="test_queue",
        durable=True
    )

def test_publish_message(message_queue, mock_pika_connection):
    """Test publishing a message."""
    message_queue.connect()
    result = message_queue.publish("test_queue", {"test": "data"})
    
    assert result is True
    message_queue.channel.basic_publish.assert_called_once()

def test_consume_messages(message_queue, mock_pika_connection):
    """Test message consumption."""
    callback = Mock()
    message_queue.connect()
    
    # Mock channel methods
    message_queue.channel.basic_consume = Mock()
    message_queue.channel.basic_qos = Mock()
    message_queue.channel.start_consuming = Mock()
    
    # Start consuming
    message_queue.consume("test_queue", callback)
    
    # Verify method calls
    message_queue.channel.basic_qos.assert_called_once_with(prefetch_count=1)
    message_queue.channel.basic_consume.assert_called_once()
    message_queue.channel.start_consuming.assert_called_once()

def test_close_connection(message_queue, mock_pika_connection):
    """Test closing connection."""
    message_queue.connect()
    message_queue.close()
    
    message_queue.connection.close.assert_called_once()
