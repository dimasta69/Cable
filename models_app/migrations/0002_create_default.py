from django.db import migrations, models


def create_default(apps, schema_editor):
    from models_app.models import Manufacturer, TypePort, EquipmentTemplateType, LineType, PortMode, Speed
    Manufacturer.objects.bulk_create(
        [
            Manufacturer(name="Cisco"),
            Manufacturer(name="Juniper"),
            Manufacturer(name="Arista"),
            Manufacturer(name="D-Link"),
            Manufacturer(name="TP-Link"),
            Manufacturer(name="MikroTik"),
            Manufacturer(name="Extreme"),
            Manufacturer(name="Huawei"),
            Manufacturer(name="Allied Telesis"),
        ]
    )

    TypePort.objects.bulk_create(
        [
            TypePort(name="RJ-45"),
            TypePort(name="RJ-11"),
            TypePort(name="LC"),
            TypePort(name="SC"),
            TypePort(name="ST"),
            TypePort(name="FC"),
        ]
    )

    EquipmentTemplateType.objects.bulk_create(
        [
            EquipmentTemplateType(name='Коммутатор', is_active=True),
            EquipmentTemplateType(name='Патч-панель', is_active=False),
            EquipmentTemplateType(name='Разетка', is_active=False)
        ]
    )

    LineType.objects.bulk_create(
        [
            LineType(name="Одномодовый"),
            LineType(name="Многомодовый"),
            LineType(name="Медный"),
        ]
    )

    PortMode.objects.bulk_create(
        [
            PortMode(name='Access', is_only_one_vlan=True, red=0, green=100, blue=0, alfa=50),
            PortMode(name='Trunk', is_only_one_vlan=False, red=100, green=0, blue=0, alfa=50),
        ]
    )

    Speed.objects.bulk_create(
        [
            Speed(value=100),
            Speed(value=1000),
        ]
    )


class Migration(migrations.Migration):
    dependencies = [
        ("models_app", "0001_initial"),
    ]

    operations = [migrations.RunPython(code=create_default, reverse_code=migrations.RunPython.noop)]
