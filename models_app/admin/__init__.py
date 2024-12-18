from models_app.admin.access.resources import AccessAdmin
from models_app.admin.scheme.resources import SchemeAdmin
from models_app.admin.building.resources import BuildingAdmin
from models_app.admin.room.resources import RoomAdmin
from models_app.admin.equipment.resources import EquipmentAdmin
from models_app.admin.server_rack.resources import ServerRackAdmin
from models_app.admin.type_port.resources import TypePortAdmin
from models_app.admin.equipment_template.resources import EquipmentTemplateAdmin
from models_app.admin.manufacturer.resources import ManufacturerAdmin
from models_app.admin.equipment_template_type.resources import EquipmentTemplateTypeAdmin
from models_app.admin.port_template.resources import PortTemplateAdmin
from models_app.admin.speed.resources import SpeedAdmin
from models_app.admin.line_type.resources import LineTypeAdmin
from models_app.admin.sfp_template.resources import SfpTemplateAdmin
from models_app.admin.user.resources import UserAdmin

from django.contrib import admin
from django.contrib.auth.models import Group


admin.site.unregister(Group)
