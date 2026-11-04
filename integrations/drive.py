import os
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.service_account import Credentials


def _build_drive():
    email = os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL')
    key = os.getenv('GOOGLE_PRIVATE_KEY', '').replace('\\n', '\n')
    if not email or not key:
        return None

    creds = Credentials.from_service_account_info(
        {
            "type": "service_account",
            "client_email": email,
            "private_key": key,
            "token_uri": "https://oauth2.googleapis.com/token",
        },
        scopes=["https://www.googleapis.com/auth/drive"],
    )
    return build('drive', 'v3', credentials=creds)


def upload_image(image_bytes, filename, mime_type='image/jpeg'):
    folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    drive = _build_drive()
    if not drive:
        raise Exception("Google Drive credentials nahi hain (.env mein GOOGLE_SERVICE_ACCOUNT_EMAIL aur GOOGLE_PRIVATE_KEY set karo).")

    media = MediaIoBaseUpload(io.BytesIO(image_bytes), mimetype=mime_type)
    file_meta = {'name': filename, 'parents': [folder_id] if folder_id else []}

    result = drive.files().create(
        body=file_meta,
        media_body=media,
        fields='id',
        supportsAllDrives=True,
    ).execute()

    file_id = result['id']

    drive.permissions().create(
        fileId=file_id,
        body={'type': 'anyone', 'role': 'reader'},
        supportsAllDrives=True,
    ).execute()

    return f"https://drive.google.com/uc?id={file_id}"
