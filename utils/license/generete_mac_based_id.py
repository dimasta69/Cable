import uuid


def generate_stable_id_from_mac(mac_address=None):
    if mac_address is None:
        mac_address = ':'.join(('%012X' % uuid.getnode())[i:i + 2] for i in range(0, 12, 2))

    namespace = uuid.NAMESPACE_DNS
    stable_uuid = uuid.uuid5(namespace, mac_address)
    return str(stable_uuid)
