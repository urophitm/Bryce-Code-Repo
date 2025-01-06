import os
from google.cloud import speech, storage
from pydub import AudioSegment
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set Google Application Credentials from the .env file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    """
    Uploads a file to Google Cloud Storage.

    Args:
        bucket_name (str): The name of the GCS bucket.
        source_file_name (str): The path to the file to upload.
        destination_blob_name (str): The name of the destination blob in the bucket.

    Returns:
        str: The GCS URI of the uploaded file.
    """
    # Initialize the Google Cloud Storage client
    storage_client = storage.Client()
    # Get the bucket object
    bucket = storage_client.bucket(bucket_name)
    # Create a blob object from the bucket
    blob = bucket.blob(destination_blob_name)
    # Upload the file to GCS
    blob.upload_from_filename(source_file_name)
    # Return the GCS URI of the uploaded file
    return f"gs://{bucket_name}/{destination_blob_name}"

def transcribe_audio(audio_path, output_path, bucket_name):
    """
    Transcribes an audio file using Google Cloud Speech-to-Text API.

    Args:
        audio_path (str): The path to the audio file to transcribe.
        output_path (str): The path to save the transcription output.
        bucket_name (str): The name of the GCS bucket to upload the audio file.
    """
    # Initialize the Google Cloud Speech client
    client = speech.SpeechClient()

    # Convert MP3 file to WAV format
    audio = AudioSegment.from_mp3(audio_path)
    wav_path = audio_path.replace(".mp3", ".wav")
    audio.export(wav_path, format="wav")

    # Upload the WAV audio file to Google Cloud Storage
    gcs_uri = upload_to_gcs(bucket_name, wav_path, os.path.basename(wav_path))

    # Configure the audio settings for the transcription request
    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    # Perform the transcription using long_running_recognize for large files
    operation = client.long_running_recognize(config=config, audio=audio)
    # Wait for the operation to complete (timeout set to 180 seconds)
    response = operation.result(timeout=180)

    # Write the transcription results to the output file
    with open(output_path, "w") as output_file:
        for result in response.results:
            output_file.write(result.alternatives[0].transcript + "\n")

if __name__ == "__main__":
    # Path to the input audio file
    audio_file_path = r"C:\Users\Admin\Desktop\API-Data-Collection\Audio Files\Basic Addition for Kids.mp3"
    # Path to save the transcription output
    transcript_output_path = r"C:\Users\Admin\Desktop\API-Data-Collection\Converted Audio Files\transcription.txt"
    # Name of the Google Cloud Storage bucket
    bucket_name = "your-gcs-bucket-name"  # Replace with your GCS bucket name
    # Call the transcribe_audio function to perform the transcription
    transcribe_audio(audio_file_path, transcript_output_path, bucket_name)