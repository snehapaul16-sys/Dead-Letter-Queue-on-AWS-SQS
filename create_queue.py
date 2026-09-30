import boto3


def create_queue():
    # Create an SQS client to interact with the queue service
    sqs = boto3.client("sqs")

    # Create a standard queue with custom settings
    response = sqs.create_queue(
        QueueName="order-processing-queue",
        Attributes={
            "VisibilityTimeout": "30",
            "MessageRetentionPeriod": "345600",
        },
    )

    # Extract and display the queue URL
    queue_url = response["QueueUrl"]
    print(f"Queue created successfully!")
    print(f"Queue URL: {queue_url}")
    return queue_url


if __name__ == "__main__":
    create_queue()
