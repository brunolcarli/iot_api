from django.db import models


class ESPTransmission(models.Model):
    timestamp_origin = models.IntegerField(null=False)
    timestamp_receive = models.IntegerField(null=False)
    mac_address = models.CharField(max_length=50, null=False, blank=False)
    ldr_sensor = models.FloatField()
    temperature_sensor = models.FloatField()
    pressure = models.FloatField()
    moisture = models.FloatField()
