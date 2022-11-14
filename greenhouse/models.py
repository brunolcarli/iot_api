from django.db import models


class ESPTransmission(models.Model):
    timestamp_origin = models.IntegerField(null=False)
    timestamp_receive = models.IntegerField(null=False)
    mac_address = models.CharField(max_length=50, null=False, blank=False)
    ldr_sensor = models.FloatField()
    temperature_sensor = models.FloatField()
    pressure = models.FloatField()
    moisture = models.FloatField()


class Device(models.Model):
    hardware_type = models.CharField(max_length=100, null=False, blank=False)
    device_id = models.CharField(max_length=50, null=False, blank=False)
    description = models.TextField()


class Installation(models.Model):
    reference = models.CharField(max_length=100, null=False, blank=False)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    latitude = models.FloatField(null=False)
    longitude = models.FloatField(null=False)
    description = models.TextField()
