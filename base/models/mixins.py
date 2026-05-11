from django.db import models

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    #   auto_now_add=True → Set timestamp only when the row is first created. Never updates again.
    updated_at = models.DateTimeField(auto_now=True)
    #   auto_now=True → Update timestamp every time the row is saved.

    class Meta:
        abstract = True
        # abstract = True means: don't create a real database table for BaseModel itself. Just share its fields with whoever inherits from it.