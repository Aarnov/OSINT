
from modules.error_handler import classify_error


test_errors = [
    "ConnectError:",
    "Unexpected response status: 403",
    "Unexpected response status: 401",
    "HTTP 429",
    "Cloudflare challenge, cannot be solved without a browser",
    "GitHub's signup form is behind a bot challenge",
    "connection was reset",
    "HTTP Error: 406",
    "Failed to extract CSRF token",
    "Something completely unknown"
]


print("ERROR CLASSIFICATION")
print("=" * 50)


for error in test_errors:

    result = classify_error(error)

    print()
    print("Original:", error)
    print("Type:", result["type"])
    print("Label:", result["label"])
    print("Retryable:", result["retryable"])

