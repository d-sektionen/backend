import pygsheets
from django.conf import settings

COL_NAME = settings.MEMBER_SHEET_COL_NAME
COL_LIU_ID = settings.MEMBER_SHEET_COL_LIU_ID
COL_UTSKOTT = settings.MEMBER_SHEET_COL_UTSKOTT
COL_TITLE = settings.MEMBER_SHEET_COL_TITLE


class Sheet:
    def __init__(self):
        self.worksheet = self.open()
        self.column_map = self.map_columns()



    @staticmethod
    def open():
        google_client = pygsheets.authorize(service_file='credentials.json')
        spreadsheet = google_client.open_by_key('1qWJiXnr1L2yGXgb578IpsoaNyJ_UXbWD8Dhv_DD8_Pg')
        return spreadsheet[0]

    def map_columns(self):
        row = self.worksheet.get_row(1, 'cells')

        return {row[i].value: i for i in range(len(row))}
