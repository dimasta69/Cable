from models_app.admin.access.resources import AccessAdmin
from models_app.admin.scheme.resources import SchemeAdmin
from models_app.admin.building.resources import BuildingAdmin
from models_app.admin.room.resources import RoomAdmin
from models_app.admin.server_rack.resources import ServerRack

from django.contrib import admin
from django.contrib.auth.models import Group


admin.site.unregister(Group)
