from .models import stores_static_rank
from rest_framework_mongoengine import serializers

class rank(serializers.DocumentSerializer):
    class Meta:
        model = stores_static_rank
        fields = '__all__'
