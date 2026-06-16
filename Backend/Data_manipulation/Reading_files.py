from win32com.client import DispatchEx

class Reading_files:
    
    def __init__(self):
        self.excel = None
        self.workbook = None

    def open_excel_file(self, path):
        print("Ouverture du fichier...")
        self.excel = DispatchEx("Excel.Application")
        self.excel.Visible = False
        self.excel.DisplayAlerts = False
        self.workbook = self.get_or_open(self.excel, path)
        print("Fichier ouvert avec succès")
        return self.workbook, self.excel

    def close_excel_file(self, save=True):
        if self.workbook:
            self.workbook.Save() if save else None
            self.workbook.Close(SaveChanges=save)
        if self.excel:
            self.excel.Quit()
        print("Fichier fermé")

    def get_sheet(self, workbook, target_name):
        target = target_name.strip().lower()
        for ws in workbook.Worksheets:
            if ws.Name.strip().lower() == target:
                return ws
        raise Exception(f"Feuille '{target_name}' introuvable")

    def get_or_open(self, excel, path):
        for wb in excel.Workbooks:
            if wb.FullName.lower() == path.lower():
                return wb
        return excel.Workbooks.Open(path)