import pandas as pd
import io
from Sharepoint_Handler.Upload import upload_file_to_sharepoint
from Config import Config

def write_excel_to_sharepoint(df: pd.DataFrame) -> bool:
    try:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        buffer.seek(0)

        # Adapt these to however your SharePoint client uploads bytes
        # SHAREPOINT_FILE_PATH
        upload_file_to_sharepoint(filename="Suivi_des_fonds.xlsx", content=buffer.read())
        return True
    except Exception as e:
        print(f"Error writing Excel to SharePoint: {e}")
        return False