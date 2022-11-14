from datetime import datetime
import graphene
from greenhouse.models import ESPTransmission, Device, Installation


class ESPTransmissionType(graphene.ObjectType):
    timestamp_origin = graphene.Int()
    timestamp_receive = graphene.Int()
    mac_address = graphene.String()
    ldr_sensor = graphene.Float()
    temperature_sensor = graphene.Float()
    pressure = graphene.Float()
    moisture = graphene.Float()
    datetime_origin = graphene.DateTime()
    datetime_receive = graphene.DateTime()

    def resolve_datetime_origin(self, info, **kwargs):
        return datetime.fromtimestamp(self.timestamp_origin)

    def resolve_datetime_receive(self, info, **kwargs):
        return datetime.fromtimestamp(self.timestamp_receive)


class DeviceType(graphene.ObjectType):
    hardware_type = graphene.String()
    device_id = graphene.String()
    description = graphene.String()
    transmissions = graphene.List(ESPTransmissionType)
    transmission_count = graphene.Int()

    def resolve_transmissions(self, info, **kwargs):
        return ESPTransmission.objects.filter(mac_address=self.device_id)

    def resolve_transmission_count(self, info, **kwargs):
        return ESPTransmission.objects.filter(mac_address=self.device_id).count()


class InstallationType(graphene.ObjectType):
    reference = graphene.String()
    device = graphene.Field(DeviceType)
    latitude = graphene.Float()
    longitude = graphene.Float()
    description = graphene.String()


class Query(graphene.ObjectType):
    version = graphene.String()

    def resolve_version(self, info, **kwargs):
        return '0.0.1'

    esp_transmissions = graphene.List(
        ESPTransmissionType,
        ldr_sensor__gte=graphene.Float(),
        ldr_sensor__lte=graphene.Float(),
        temperature_sensor__gte=graphene.Float(),
        temperature_sensor__lte=graphene.Float(),
        pressure__gte=graphene.Float(),
        moisture__lte=graphene.Float(),
        mac_address__in=graphene.List(graphene.String),
        mac_address__icontains=graphene.String()
    )

    def resolve_esp_transmissions(self, info, **kwargs):
        return ESPTransmission.objects.filter(**kwargs)

    devices = graphene.List(DeviceType)

    def resolve_devices(self, info, **kwargs):
        return Device.objects.filter(**kwargs)

    device = graphene.Field(
        DeviceType,
        device_id=graphene.String(required=True)
    )    

    def resolve_device(self, info, **kwargs):
        try:
            return Device.objects.get(device_id=kwargs['device_id'])
        except Device.DoesNotExist:
            raise Exception('Device Not found!')

    installations = graphene.List(InstallationType)

    def resolve_installations(self, info, **kwargs):
        return Installation.objects.filter(**kwargs)

    installation = graphene.Field(
        InstallationType,
        reference=graphene.String(required=True)
    )

    def resolve_installation(self, info, **kwargs):
        return Installation.objects.get(reference=kwargs['reference'])
