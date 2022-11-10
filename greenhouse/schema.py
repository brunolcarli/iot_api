import graphene
from greenhouse.models import ESPTransmission


class ESPTransmissionType(graphene.ObjectType):
    timestamp_origin = graphene.Int()
    timestamp_receive = graphene.Int()
    mac_address = graphene.String()
    ldr_sensor = graphene.Float()
    temperature_sensor = graphene.Float()
    pressure = graphene.Float()
    moisture = graphene.Float()


class Query(graphene.ObjectType):
    version = graphene.String()

    def resolve_version(self, info, **kwargs):
        return '0.0.0'

    esp_transmissions = graphene.List(
        ESPTransmissionType
    )

    def resolve_esp_transmissions(self, info, **kwargs):
        return ESPTransmission.objects.Filter(**kwargs)
