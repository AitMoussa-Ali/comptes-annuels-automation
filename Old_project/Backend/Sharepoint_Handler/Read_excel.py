import io
from Config import Config
import pandas as pd
from Sharepoint_Handler.Requests import get_token, get_drive_id
import requests

def read_excel_from_sharepoint() -> pd.DataFrame:
    token = get_token()
    drive_id = get_drive_id(token)
    
    file_path = Config.PATH_LOGIN_FILE
    sheet_name = Config.SHEET_LOGIN_NAME
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(
            f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{file_path}/{sheet_name}:/content",
            headers=headers
        )
        response.raise_for_status()
        
        df = pd.read_excel(io.BytesIO(response.content))
        
        print("✅ File read successfully from SharePoint")
        return df
            
    except Exception as e:
        print(f"Error reading file: {e}")
        return None