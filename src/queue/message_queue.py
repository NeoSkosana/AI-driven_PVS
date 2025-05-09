"""
Message queue service for handling asynchronous tasks.
"""
import json
import pika
import os
from typing import Any, Callable
from dotenv import load_dotenv

class MessageQueue:
    """RabbitMQ message queue implementation."""
    
    def __init__(self):
        """Initialize RabbitMQ connection."""
        load_dotenv()
        
        # Get connection parameters from environment
        self.host = os.getenv('RABBITMQ_HOST', 'localhost')
        self.port = int(os.getenv('RABBITMQ_PORT', 5672))
        self.user = os.getenv('RABBITMQ_USER', 'guest')
        self.password = os.getenv('RABBITMQ_PASS', 'guest')
        
        # Create connection parameters
        credentials = pika.PlainCredentials(self.user, self.password)
        self.parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=credentials
        )
        
        # Initialize connection
        self.connection = None
        self.channel = None
        
    def connect(self) -> bool:
        """
        Establish connection to RabbitMQ server.
        
        Returns:
            bool: True if connection successful
        """
        try:
            self.connection = pika.BlockingConnection(self.parameters)
            self.channel = self.connection.channel()
            return True
        except Exception as e:
            print(f"RabbitMQ connection error: {str(e)}")
            return False
            
    def close(self):
        """Close RabbitMQ connection."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            
    def declare_queue(self, queue_name: str) -> bool:
        """
        Declare a queue for message handling.
        
        Args:
            queue_name: Name of the queue to declare
            
        Returns:
            bool: True if successful
        """
        try:
            self.channel.queue_declare(queue=queue_name, durable=True)
            return True
        except Exception as e:
            print(f"Queue declaration error: {str(e)}")
            return False
            
    def publish(self, queue_name: str, message: Any) -> bool:
        """
        Publish a message to a queue.
        
        Args:
            queue_name: Queue to publish to
            message: Message to publish (will be JSON serialized)
            
        Returns:
            bool: True if successful
        """
        try:
            if not self.connection or self.connection.is_closed:
                self.connect()
                
            # Ensure queue exists
            self.declare_queue(queue_name)
            
            # Publish message
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                )
            )
            return True
        except Exception as e:
            print(f"Message publish error: {str(e)}")
            return False
            
    def consume(self, queue_name: str, callback: Callable[[Any], None]):
        """
        Start consuming messages from a queue.
        
        Args:
            queue_name: Queue to consume from
            callback: Function to call with deserialized message
        """
        try:
            if not self.connection or self.connection.is_closed:
                self.connect()
                
            # Ensure queue exists
            self.declare_queue(queue_name)
            
            def message_handler(ch, method, properties, body):
                try:
                    message = json.loads(body)
                    callback(message)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    print(f"Message handling error: {str(e)}")
                    ch.basic_nack(delivery_tag=method.delivery_tag)
                    
            # Start consuming
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=message_handler
            )
            
            print(f"Started consuming from queue: {queue_name}")
            self.channel.start_consuming()
            
        except Exception as e:
            print(f"Message consume error: {str(e)}")
            self.close()
