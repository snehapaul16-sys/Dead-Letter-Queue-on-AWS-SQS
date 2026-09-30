import json
import boto3


def setup_dead_letter_queue():
    sqs = boto3.client("sqs")

    print("Creating Dead Letter Queue...")
    dlq_response = sqs.create_queue(
        QueueName="order-processing-dlq",
        Attributes={
            "MessageRetentionPeriod": "1209600",
        },
    )
    dlq_url = dlq_response["QueueUrl"]
    print(f"DLQ created: {dlq_url}")

    dlq_attributes = sqs.get_queue_attributes(
        QueueUrl=dlq_url,
        AttributeNames=["QueueArn"],
    )
    dlq_arn = dlq_attributes["Attributes"]["QueueArn"]
    print(f"DLQ ARN: {dlq_arn}")

    # Main queue URL lookup
    main_queue_url = sqs.get_queue_url(QueueName="order-processing-queue")["QueueUrl"]

    redrive_policy = {
        "deadLetterTargetArn": dlq_arn,
        "maxReceiveCount": "3",
    }

    sqs.set_queue_attributes(
        QueueUrl=main_queue_url,
        Attributes={
            "RedrivePolicy": json.dumps(redrive_policy),
            "VisibilityTimeout": "5",
        },
    )

    print("\nRedrive policy attached to main queue:")
    print("  maxReceiveCount: 3")
    print(f"  deadLetterTargetArn: {dlq_arn}")
    print("  VisibilityTimeout: 5 seconds (short for demo)")
    print("\nMessages that fail 3 times will automatically move to the DLQ.")


if __name__ == "__main__":
    setup_dead_letter_queue()