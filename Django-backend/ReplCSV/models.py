from mongoengine import Document, fields

# Create your models here.
class stores_static_rank(Document):
    Store_Code = fields.StringField(required=True)
    Static_Priority = fields.IntField(required=True)
