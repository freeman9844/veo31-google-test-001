# Veo 3.1 4K Video Generation and Extension Demo

This project is a Python example code that uses Google Cloud Vertex AI's **Veo 3.1** model to generate 4K resolution videos and extend the generated videos while maintaining 4K resolution.

## Key Features

- **4K Video Generation**: Generates high-quality videos in 4K resolution based on text prompts.
- **4K Video Extension**: Extends the video by continuing from the last part of the generated video with new content, maintaining 4K resolution.
- **Automatic Retry and Error Handling**: Includes automatic retry logic with exponential backoff for API call failures.

## Prerequisites

To run this code, the following items are required:

1.  **Google Cloud Project**: A Google Cloud project with access to the Veo 3.1 model.
2.  **Vertex AI API Enabled**: The Vertex AI API must be enabled in the project.
3.  **Google Cloud Storage (GCS) Bucket**: A GCS bucket to store the generated videos.
4.  **Python Environment**: Python 3.9 or higher is recommended.
5.  **`uv` Package Manager**: Used for fast and efficient dependency management (recommended).

## Installation and Setup

### 1. Clone the Project

```bash
git clone https://github.com/freeman9844/veo31-google-test-001.git
cd veo31-google-test-001
```

### 2. Install Dependencies (Using `uv`)

Create a virtual environment and install the required packages using `uv`.

```bash
# Create virtual environment (if not exists)
uv venv

# Install packages
uv pip install google-genai
```

### 3. Google Cloud Authentication

Authenticate using the Google Cloud SDK when running locally.

```bash
gcloud auth application-default login
```

### 4. Code Configuration

Open the `veo_demo.py` file and modify the following variables to match your environment (or set them as environment variables).

```python
# veo_demo.py

# 1. Project ID & Location
# Set via environment variables GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION or modify code directly
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

# 2. GCS Bucket URI (Required)
OUTPUT_GCS_URI = "gs://your-bucket-name" 
```

## Usage

### Run Script

Run the script using `uv`.

```bash
uv run veo_demo.py
```

Alternatively, you can run it directly with dependencies included for a one-off execution.

```bash
uv run --with google-genai veo_demo.py
```

### Execution Results

If the script runs successfully, logs similar to the following will be printed to the console:

1.  **Video Generation**: Starts 4K video generation and shows progress.
2.  **Video Extension**: Extends 4K based on the generated video.
3.  **Result**: Outputs the GCS URI of the final generated video.

```text
--- Generating video with model veo-3.1-generate-preview ---
Prompt: A cinematic drone shot...
...
Video generation successful!
Video URI: gs://your-bucket-name/.../sample_0.mp4

--- Extending video ---
Input Video: gs://your-bucket-name/.../sample_0.mp4
...
Video extension successful!
Extended Video URI: gs://your-bucket-name/.../sample_0.mp4
```

## Troubleshooting

### Internal Error (Code 13)

An `Internal error. Please try again later.` (Code 13) error may occur during 4K generation or extension.

-   **Cause**: Veo 3.1 model's 4K generation requires high resources and may occur intermittently depending on temporary resource shortages or service status in specific regions (e.g., us-central1).
-   **Solution**:
    1.  Try again after a while. (Retry logic is included in the script.)
    2.  If it fails continuously, try testing with `1080p` resolution.

### Quota Error (Code 8)

-   **Cause**: Occurs when the API call quota is exceeded.
-   **Solution**: The exponential backoff logic included in the script will automatically retry. If it continues to fail, check your Quota in the GCP Console and request an increase.
