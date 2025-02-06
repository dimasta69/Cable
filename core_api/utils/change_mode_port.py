from django.contrib.contenttypes.models import ContentType

from models_app.models import Port, VlanDevice

port_content_type = ContentType.objects.get_for_model(Port)


def change_mode_port(port_id: int) -> None:
    VlanDevice.objects.filter(object_type=port_content_type, object_id=port_id).delete()
