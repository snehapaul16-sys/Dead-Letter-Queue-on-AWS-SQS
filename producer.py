import boto3
import json


def get_queue_url():
    # Look up the queue URL by name so we don't hardcode it
    sqs = boto3.client("sqs")
    response = sqs.get_queue_url(QueueName="order-processing-queue")
    return response["QueueUrl"]


def send_messages():
    sqs = boto3.client("sqs")
    queue_url = get_queue_url()

    # Five well-formed order messages
    good_orders = [
        {"order_id": "1001", "product": "Wireless Mouse", "quantity": 2, "price": 29.99},
        {"order_id": "1002", "product": "USB-C Cable", "quantity": 5, "price": 12.50},
        {"order_id": "1003", "product": "Mechanical Keyboard", "quantity": 1, "price": 89.99},
        {"order_id": "1004", "product": "Monitor Stand", "quantity": 1, "price": 45.00},
        {"order_id": "1005", "product": "Webcam HD", "quantity": 3, "price": 59.99},
    ]
        # Deliberately broken messages to test error handling
    poison_messages = [
        "this is not valid json at all {{{{",
        json.dumps({"order_id": "9999"}),
    ]

    sent_count = 0

    # Send each good order as JSON
    for order in good_orders:
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(order),
        )
        sent_count += 1

    # Send poison messages as-is
    for poison in poison_messages:
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=poison,
        )
        sent_count += 1

    print(f"Sent {sent_count} messages ({len(good_orders)} good, {len(poison_messages)} poison)")


if __name__ == "__main__":
    send_messages()