import boto3
import json
import sys


def get_queue_url(queue_name):
    sqs = boto3.client("sqs")
    response = sqs.get_queue_url(QueueName=queue_name)
    return response["QueueUrl"]     
def inspect_dlq():
    sqs = boto3.client("sqs")
    dlq_url = get_queue_url("order-processing-dlq")

    print("Inspecting Dead Letter Queue...\n")

    response = sqs.receive_message(
        QueueUrl=dlq_url,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=5,
        AttributeNames=["All"],
    )

    messages = response.get("Messages", [])

    if not messages:
        print("DLQ is empty. No failed messages.")
        return messages

    print(f"Found {len(messages)} dead-lettered messages:\n")

    for i, message in enumerate(messages, 1):
        body = message["Body"]
        attributes = message.get("Attributes", {})
        sent_timestamp = attributes.get("SentTimestamp", "unknown")
        receive_count = attributes.get("ApproximateReceiveCount", "unknown")

        print(f"  Message {i}:")
        print(f"    Body: {body[:100]}")
        print(f"    Original receive count: {receive_count}")
        print(f"    Message ID: {message['MessageId']}")
        print(f"")

    return messages
def replay_messages():
    sqs = boto3.client("sqs")
    dlq_url = get_queue_url("order-processing-dlq")
    main_queue_url = get_queue_url("order-processing-queue")

    print("Replaying messages from DLQ to main queue...\n")

    response = sqs.receive_message(
        QueueUrl=dlq_url,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=5,
    )

    messages = response.get("Messages", [])

    if not messages:
        print("DLQ is empty. Nothing to replay.")
        return

    replayed = 0
    for message in messages:
        sqs.send_message(
            QueueUrl=main_queue_url,
            MessageBody=message["Body"],
        )

        sqs.delete_message(
            QueueUrl=dlq_url,
            ReceiptHandle=message["ReceiptHandle"],
        )

        replayed += 1
        print(f"  Replayed message: {message['Body'][:60]}...")

    print(f"\nReplayed {replayed} messages back to main queue.")
  

if __name__ == "__main__":
    if "--replay" in sys.argv:
        replay_messages()
    else:
        inspect_dlq()