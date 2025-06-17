from django.contrib.contenttypes.models import ContentType

from models_app.models import Port, VlanDevice


def change_mode_port(port_id: int) -> None:
    port_content_type = ContentType.objects.get_for_model(Port)
    VlanDevice.objects.filter(device_type=port_content_type, device_id=port_id).delete()
