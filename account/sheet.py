# import pygsheets
# from django.conf import settings

# NAME = settings.SA_COL_NAME
# LIU_ID = settings.SA_COL_LIU_ID
# UTSKOTT = settings.SA_COL_UTSKOTT
# TITLE = settings.SA_COL_TITLE


# class Sheet:
#     def __init__(self):
#         self.worksheet = self._open()
#         self.column_map = self._map_columns()

#     def read_data(self):
#         all_rows = self.worksheet.get_all_values()
#         all_data = []

#         for row in all_rows[1:]:
#             data = {}
#             for column, index in self.column_map.items():
#                 data[column] = row[index]

#             all_data.append(data)

#         return all_data

#     def _map_columns(self):
#         row = self.worksheet.get_row(1, 'cells')

#         return {row[i].value: i for i in range(len(row)) if row[i].value}

#     @staticmethod
#     def _open():
#         google_client = pygsheets.authorize(service_file=settings.SA_CREDENTIALS_FILE)
#         spreadsheet = google_client.open_by_key(settings.SA_FILE_ID)
#         return spreadsheet[0]
