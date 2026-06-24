import requests
from Config import Config
import msal



def get_drive_id(token: str) -> str:
    headers = {"Authorization": f"Bearer {token}"}
    
    site_url = Config.SHAREPOINT_SITE_URL

    site_response = requests.get(
        f"https://graph.microsoft.com/v1.0/sites/{site_url}",
        headers=headers
    )
    site_id = site_response.json()["id"]

    drives_response = requests.get(
        f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives",
        headers=headers
    )
    drives = drives_response.json().get("value", [])
    return drives[0]["id"]

def get_drive_id_excel(token:str)-> str:
    headers = {"Authorization": f"Bearer {token}"}
    # site_url = vars["SHAREPOINT_SITE_URL"]

    site_response = requests.get(
        f"https://graph.microsoft.com/v1.0/drives",
        headers=headers
    )
    site_id = site_response.json()["value"][0]["id"]

    return site_id

def get_token() -> str | None:
    app = msal.ConfidentialClientApplication(
        client_id=Config.CLIENT_ID,
        client_credential=Config.PASSWORD_MAILBOX,
        authority=f"https://login.microsoftonline.com/{Config.TENANT_ID}"
    )
    result = app.acquire_token_for_client(
        scopes=[Config.SCOPES]
    )
    if "access_token" in result:
        print("✅ Token OK")
        return result["access_token"]
    else:
        print("❌ Token failed:", result.get("error_description"))
        return None