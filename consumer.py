import json
import time
import boto3


def get_queue_url():
    # Look up the queue URL by name
    sqs = boto3.client("sqs")
    response = sqs.get_queue_url(QueueName="order-processing-queue")
    return response["QueueUrl"]


def validate_order(message_body):
    # Check that the message has all required order fields
    required_fields = ["order_id", "product", "quantity", "price"]

    order = json.loads(message_body)

    missing_fields = [field for field in required_fields if field not in order]
    if missing_fields:
        raise ValueError(f"Missing required fields: {missing_fields}")

    if order["quantity"] <= 0:
        raise ValueError(f"Invalid quantity: {order['quantity']}")

    return order


def process_messages():
    sqs = boto3.client("sqs")
    queue_url = get_queue_url()

    print("Polling for messages...\n")

    # Receive up to 10 messages, wait up to 5 seconds
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=5,
        AttributeNames=["ApproximateReceiveCount"],
    )

    messages = response.get("Messages", [])

    if not messages:
        print("No messages in queue.")
        return

    print(f"Received {len(messages)} messages:\n")

    for message in messages:
        body = message["Body"]
        receipt_handle = message["ReceiptHandle"]
        receive_count = message.get("Attributes", {}).get(
            "ApproximateReceiveCount", "?"
        )

        try:
            order = validate_order(body)
            print(
                f"  [OK] Processed order #{order['order_id']}: "
                f"{order['quantity']}x {order['product']} @ ${order['price']}"
            )

            # Delete successfully processed messages from the queue
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle,
            )

        except (json.JSONDecodeError, ValueError) as e:
            # Failed messages are NOT deleted - SQS will redeliver them
            print(
                f"  [FAIL] Could not process message (receive #{receive_count}): {e}"
            )
            print(f"         Body: {body[:80]}...")
            print("         Message NOT deleted - will be redelivered.\n")


if __name__ == "__main__":
    process_messages()