from rest_framework import status

from utils.services import ServiceWithResult
from utils.license.generete_mac_based_id import generate_stable_id_from_mac


class MacService(ServiceWithResult):

    def process(self):
        if self.is_valid():
            self.result = {"mac_uuid": generate_stable_id_from_mac()}
            self.response_status = status.HTTP_200_OK
        return self
