import os
import mysql.connector
import requests

def lambda_handler(event, context):
    s3_event = event['Records'][0]['s3']
    image_key = s3_event['object']['key']
    image_url = f"https://{s3_event['bucket']['name']}.s3.amazonaws.com/{image_key}"

    # Generate caption via Gemini API
    prompt = f"Write a short caption for this image: {image_url}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['GOOGLE_API_KEY']}"
    }
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    gemini_api = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    response = requests.post(gemini_api, json=data, headers=headers)
    caption = response.json()['candidates'][0]['content']['parts'][0]['text']

    # Save to RDS
    conn = mysql.connector.connect(
        host=os.environ['DB_HOST'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        database=os.environ['DB_NAME']
    )
    cursor = conn.cursor()
    cursor.execute("UPDATE images SET caption=%s WHERE s3_url=%s", (caption, image_url))
    conn.commit()
    cursor.close()
    conn.close()

    return {
        'statusCode': 200,
        'body': f'Caption generated: {caption}'
    }
