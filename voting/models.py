import re

from django.db import models


class Section(models.Model):
    name = models.TextField()
    program_codes = models.TextField()

    def get_program_codes(self):
        items = re.split('[, \n]', self.program_codes)  # Split
        items = [x.strip() for x in items]              # Strip
        items = [x for x in items if x]                 # Filter

        return items
