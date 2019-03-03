from django.db import models
from django.contrib.auth.models import User

class Entry(models.Model):
  FATAL = 'F'
  ERROR = 'E'
  WARN = 'W'
  INFO = 'I'
  DEBUG = 'D'
  SEVERITY_LEVELS = (
      (FATAL, 'Fatal'),
      (ERROR, 'Error'),
      (WARN, 'Warning'),
      (INFO, 'Info'),
      (DEBUG, 'Debug'),
  )

  NETLIGHT = 'NL'
  UNCATEGORIZED = 'UN'
  CATEGORIES = (
    (NETLIGHT, 'Netlight'),
    (UNCATEGORIZED, 'Uncategorized'),
  )

  category = models.CharField(
      max_length=2,
      choices=CATEGORIES,
      default=UNCATEGORIZED,
  )
  severity = models.CharField(
      max_length=1,
      choices=SEVERITY_LEVELS,
      default=INFO,
  )
  description = models.TextField(max_length=128)
  timestamp = models.DateTimeField(auto_now_add=True)
  user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="+")
  
  def __str__(self):
    return self.category + ' - ' + self.description[:32]

  class Meta:
    verbose_name = "Log Entry"
    verbose_name_plural = "Log Entries"