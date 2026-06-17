import requests
from Config import Config
from Sharepoint_Handler.Requests import get_token, get_drive_id


def upload_file_to_sharepoint(filename: str, content: bytes) -> bool:
    token = get_token()
    drive_id = get_drive_id(token)

    # folder_path = f"{Config.SHAREPOINT_FOLDER}/{fond_name}"
    url = (
        f"https://graph.microsoft.com/v1.0/drives/{drive_id}"
        f"/root:/{Config.SHAREPOINT_FOLDER}/{filename}:/content"
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/octet-stream",
    }
    response = requests.put(url, headers=headers, data=content)
    return response.status_code in (200, 201)
