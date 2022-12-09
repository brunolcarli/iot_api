import asyncio
from datetime import datetime
import graphene
import pytz
from greenhouse.models import ESPTransmission, Device, Installation
from greenhouse.util import translate_ldr_value
from greenhouse.statistics import hour_relative_freq


class Subscription(graphene.ObjectType):
    foo = graphene.String()

    async def resolve_foo(root, info):
        while True:
            yield 'baz'
            await asyncio.sleep(1)
            break
        await 'spam'


class HourRelativeFrequency(graphene.ObjectType):
    hours = graphene.List(graphene.String)
    ldr_relative_frequency = graphene.List(graphene.Float)
    ldr_high_std = graphene.List(graphene.Float)
    ldr_low_std = graphene.List(graphene.Float)
    temperature_relative_frequency = graphene.List(graphene.Float)
    temperature_high_std = graphene.List(graphene.Float)
    temperature_low_std = graphene.List(graphene.Float)
    pressure_relative_frequency = graphene.List(graphene.Float)
    pressure_high_std = graphene.List(graphene.Float)
    pressure_low_std = graphene.List(graphene.Float)
    moisture_relative_frequency = graphene.List(graphene.Float)
    moisture_high_std = graphene.List(graphene.Float)
    moisture_low_std = graphene.List(graphene.Float)


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
    light_level = graphene.String()

    def resolve_light_level(self, info, **kwargs):
        return translate_ldr_value(self.ldr_sensor)

    def resolve_datetime_origin(self, info, **kwargs):
        return datetime.fromtimestamp(self.timestamp_origin).astimezone(
            pytz.timezone('America/Sao_Paulo')
        )

    def resolve_datetime_receive(self, info, **kwargs):
        return datetime.fromtimestamp(self.timestamp_receive).astimezone(
            pytz.timezone('America/Sao_Paulo')
        )


class DeviceType(graphene.ObjectType):
    hardware_type = graphene.String()
    device_id = graphene.String()
    description = graphene.String()
    transmissions = graphene.List(ESPTransmissionType)
    transmission_count = graphene.Int()
    is_installed = graphene.Boolean()
    last_transmission = graphene.Field(ESPTransmissionType)
    hour_relative_frequency = graphene.Field(HourRelativeFrequency)

    def resolve_last_transmission(self, info, **kwargs):
        return ESPTransmission.objects.filter(mac_address=self.device_id).last()

    def resolve_hour_relative_frequency(self, info, **kwargs):
        if 'dt_start' in self.__dict__:
            tx = ESPTransmission.objects.filter(
                mac_address=self.device_id,
                timestamp_origin__gte=self.__dict__['dt_start'].timestamp()
            )
        else:
            tx = ESPTransmission.objects.filter(mac_address=self.device_id)
        if not tx:
            return None

        rel_freq = hour_relative_freq(tx, '3600S')
        return HourRelativeFrequency(
            hours=rel_freq.index.values,
            ldr_relative_frequency=rel_freq.LDR_REL_FREQ.values,
            ldr_high_std=rel_freq.LDR_POS_STD.values,
            ldr_low_std=rel_freq.LDR_NEG_STD.values,
            temperature_relative_frequency=rel_freq.TEMP_REL_FREQ.values,
            temperature_high_std=rel_freq.TEMP_POS_STD.values,
            temperature_low_std=rel_freq.TEMP_NEG_STD.values,
            pressure_relative_frequency=rel_freq.PRES_REL_FREQ.values,
            pressure_high_std=rel_freq.PRES_POS_STD.values,
            pressure_low_std=rel_freq.PRES_NEG_STD.values,
            moisture_relative_frequency=rel_freq.MOIS_REL_FREQ.values,
            moisture_high_std=rel_freq.MOIS_POS_STD.values,
            moisture_low_std=rel_freq.MOIS_NEG_STD.values,
        )

    def resolve_transmissions(self, info, **kwargs):
        if 'dt_start' in self.__dict__:
            return ESPTransmission.objects.filter(
                mac_address=self.device_id,
                timestamp_origin__gte=self.__dict__['dt_start'].timestamp()
            )
        return ESPTransmission.objects.filter(mac_address=self.device_id)

    def resolve_transmission_count(self, info, **kwargs):
        if 'dt_start' in self.__dict__:
            return ESPTransmission.objects.filter(
                mac_address=self.device_id,
                timestamp_origin__gte=self.__dict__['dt_start'].timestamp()
            ).count()
        return ESPTransmission.objects.filter(mac_address=self.device_id).count()

    def resolve_is_installed(self, info, **kwargs):
        return bool(self.installation_set.count())


class InstallationType(graphene.ObjectType):
    reference = graphene.String()
    device = graphene.Field(DeviceType)
    latitude = graphene.Float()
    longitude = graphene.Float()
    description = graphene.String()


class Query(graphene.ObjectType):
    version = graphene.String()

    def resolve_version(self, info, **kwargs):
        return '0.0.7'

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
        reference=graphene.String(required=True),
        tx_datetime_start=graphene.DateTime()
    )

    def resolve_installation(self, info, **kwargs):
        installation = Installation.objects.get(reference=kwargs['reference'])
        if installation.device and kwargs.get('tx_datetime_start'):
            installation.device.dt_start = kwargs['tx_datetime_start']
        return installation


# MUTATIONS

class CreateDevice(graphene.relay.ClientIDMutation):
    device = graphene.Field(DeviceType)

    class Input:
        hardware_type = graphene.String(required=True)
        device_id = graphene.String(requried=True)
        description = graphene.String()

    def mutate_and_get_payload(self, info, **kwargs):
        device, created = Device.objects.get_or_create(
            device_id=kwargs['device_id']
        )
        if not created:
            raise Exception("Device ID already registered")

        device.hardware_type = kwargs['hardware_type']
        device.description = kwargs.get('description', "")
        device.save()

        return CreateDevice(device)


class CreateInstallation(graphene.relay.ClientIDMutation):
    installation = graphene.Field(InstallationType)

    class Input:
        reference = graphene.String(required=True)
        device_id = graphene.String(required=True)
        latitude = graphene.Float(required=True)
        longitude = graphene.Float(required=True)
        description = graphene.String()

    def mutate_and_get_payload(self, info, **kwargs):
        try:
            device = Device.objects.get(device_id=kwargs['device_id'])
        except Device.DoesNotExist:
            raise Exception('Device not found')

        if bool(device.installation_set.count()):
            raise Exception('Device already installed in another installation')

        installation = Installation.objects.create(
            reference=kwargs['reference'],
            device=device,
            latitude=kwargs['latitude'],
            longitude=kwargs['longitude'],
            description=kwargs.get('description', '')
        )
        installation.save()

        return CreateInstallation(installation)


class Mutation:
    create_device = CreateDevice.Field()
    create_installation = CreateInstallation.Field()
