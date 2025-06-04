import os
import boto3
import tempfile
from PIL import Image

s3 = boto3.client('s3')

def lambda_handler(event, context):
    try:
        # Get the uploaded image's bucket and key
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']

        if key.startswith("thumbnails/"):
            print("Already a thumbnail. Skipping.")
            return {'statusCode': 200, 'body': 'Skipped'}

        # Download original image to temporary file
        with tempfile.NamedTemporaryFile() as temp_input:
            s3.download_file(bucket, key, temp_input.name)

            with Image.open(temp_input.name) as img:
                img.thumbnail((128, 128))

                with tempfile.NamedTemporaryFile(suffix=".jpg") as temp_output:
                    img.save(temp_output.name, "JPEG")
                    thumb_key = f"thumbnails/{os.path.basename(key)}"
                    s3.upload_file(temp_output.name, bucket, thumb_key, ExtraArgs={'ContentType': 'image/jpeg'})

        print(f"Thumbnail saved at: {thumb_key}")
        return {'statusCode': 200, 'body': f'Thumbnail stored at {thumb_key}'}

    except Exception as e:
        print("[ERROR]", str(e))
        return {'statusCode': 500, 'body': str(e)}
