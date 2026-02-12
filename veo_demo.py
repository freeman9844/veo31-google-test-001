import time
import os
import random
import math
from google import genai
from google.genai.types import GenerateVideosConfig, Video, Part

# TODO: Replace with your Google Cloud Project ID and Location
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "jwlee-argolis-202104")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

# TODO: Replace with your GCS bucket URI
OUTPUT_GCS_URI = "gs://jwlee-gcs-bucket-123"

def generate_video(client, prompt: str, output_uri: str, model: str = "veo-3.1-generate-preview", aspect_ratio: str = "16:9", resolution: str = "4k"):
    """Generates a video from a text prompt.
    
    Args:
        client: The GenAI client.
        prompt: The text prompt for video generation.
        output_uri: The GCS URI for the output video.
        model: The Veo model version.
        aspect_ratio: The aspect ratio of the video (e.g., "16:9", "9:16").
        resolution: The resolution of the video (e.g., "1080p").
    """
    print(f"--- Generating video with model {model} ---")
    print(f"Prompt: {prompt}")
    
    max_retries = 5
    base_delay = 30 # Increased base delay

    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}...")
            operation = client.models.generate_videos(
                model=model,
                prompt=prompt,
                config=GenerateVideosConfig(
                    output_gcs_uri=output_uri,
                    aspect_ratio=aspect_ratio,
                    resolution=resolution, 
                ),
            )
            
            print(f"Operation started: {operation.name}")
            while not operation.done:
                time.sleep(15)
                operation = client.operations.get(operation)
                print(f"Processing... {operation.metadata.get('state', 'UNKNOWN') if operation.metadata else 'UNKNOWN'}")

            if operation.result:
                 # actual result structure might vary, fetching the first video uri
                generated_video = operation.result.generated_videos[0]
                video_uri = generated_video.video.uri
                print(f"Video generation successful!")
                print(f"Video URI: {video_uri}")
                return video_uri
            else:
                 print("\n[ERROR] Video generation failed: Operation completed but no result returned.")
                 if operation.error:
                     print(f"Details: {operation.error}")
                     # Check for throttling error (Code 8)
                     if hasattr(operation.error, 'code') and operation.error.code == 8:
                         # Exponential backoff with jitter: delay = base * 2^attempt + jitter
                         delay = (base_delay * (2 ** attempt)) + random.uniform(0, 10)
                         print(f"Throttling error detected. Waiting {delay:.2f} seconds before retrying...")
                         time.sleep(delay)
                         continue
                 return None

        except Exception as e:
            print(f"An error occurred during video generation: {e}")
            # If exception is related to resource exhaustion, could also retry here, 
            # but usually it comes via operation.error for LROs.
            return None
    
    print("Max retries exceeded for video generation.")
    return None

def extend_video(client, input_video_uri: str, prompt: str, output_uri: str, model: str = "veo-3.1-generate-preview", aspect_ratio: str = "16:9", resolution: str = "4k"):
    """Extends an existing video.
    
    In Veo 3.1, video extension generates a new segment based on the last part 
    (typically the final second) of the input video to maintain continuity.

    Args:
        client: The GenAI client.
        input_video_uri: The GCS URI of the video to be extended.
        prompt: The text prompt describing what happens in the extension.
        output_uri: The GCS URI for the output video.
        model: The Veo model version.
        aspect_ratio: The aspect ratio of the video.
        resolution: The resolution of the video.
    """
    print(f"\n--- Extending video ---")
    print(f"Input Video: {input_video_uri}")
    print(f"Prompt: {prompt}")

    max_retries = 5
    base_delay = 30 # Increased base delay

    for attempt in range(max_retries):
        try:
             # Note: Extension typically generates a new segment based on the last part of the input.
             # The 'prompt' describes what happens *next*.
            print(f"Attempt {attempt + 1}/{max_retries}...")
            
            operation = client.models.generate_videos(
                model=model,
                prompt=prompt,
                video=Video(
                    uri=input_video_uri,
                    mime_type="video/mp4" 
                ),
                config=GenerateVideosConfig(
                    output_gcs_uri=output_uri,
                    aspect_ratio=aspect_ratio,
                    resolution=resolution,
                ),
            )

            print(f"Operation started: {operation.name}")
            while not operation.done:
                time.sleep(15)
                operation = client.operations.get(operation)
                print(f"Processing extension... {operation.metadata.get('state', 'UNKNOWN') if operation.metadata else 'UNKNOWN'}")
            
            if operation.result:
                extended_video = operation.result.generated_videos[0]
                video_uri = extended_video.video.uri
                print(f"Video extension successful!")
                print(f"Extended Video URI: {video_uri}")
                return video_uri
            else:
                print("\n[ERROR] Video extension failed: Operation completed but no result returned.")
                if operation.error:
                    print(f"Details: {operation.error}")
                    # Check for throttling error (Code 8)
                    if hasattr(operation.error, 'code') and operation.error.code == 8:
                         # Exponential backoff with jitter: delay = base * 2^attempt + jitter
                         delay = (base_delay * (2 ** attempt)) + random.uniform(0, 10)
                         print(f"Throttling error detected. Waiting {delay:.2f} seconds before retrying...")
                         time.sleep(delay)
                         continue
                return None

        except Exception as e:
            print(f"An error occurred during video extension: {e}")
            return None

    print("Max retries exceeded for video extension.")
    return None

def main():
    # Helper to enable Vertex AI in GenAI SDK
    # Ensure you have authenticated: gcloud auth application-default login
    if "GOOGLE_GENAI_USE_VERTEXAI" not in os.environ:
         os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
         os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
         os.environ["GOOGLE_CLOUD_LOCATION"] = LOCATION

    client = genai.Client(
        vertexai=True, 
        project=PROJECT_ID, 
        location=LOCATION
    )

    # 1. Generate initial video
    prompt = "A cinematic drone shot of a futuristic cyberpunk city at night with neon lights, 4k high resolution."
    
    # Check if bucket is set
    if "your-bucket-name" in OUTPUT_GCS_URI:
        print("ERROR: Please update the 'OUTPUT_GCS_URI' variable in the script with your GCS bucket.")
        return

    generated_video_uri = generate_video(client, prompt, OUTPUT_GCS_URI, resolution="4k")
    # generated_video_uri = "gs://jwlee-gcs-bucket-123/14159446156087135794/sample_0.mp4" # Testing with existing video

    if generated_video_uri:
        # 2. Extend the video
        extension_prompt = "The camera flies forward through the street, revealing more flying cars and skyscrapers."
        extend_video(client, generated_video_uri, extension_prompt, OUTPUT_GCS_URI, resolution="4k")

if __name__ == "__main__":
    main()
