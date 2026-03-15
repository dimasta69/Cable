import json
import base64
import hmac
import hashlib
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from .exception import (
    LicenseSignatureException,
    LicensePeriodException,
    LicenseVerificationException,
    LicenseInvalidException,
)


class LicenseManager:
    master_key = 'mZ34ei0S6yAkkteOtyPokgl2S1LocwSrtr_8p4_9TeM='

    def __init__(self) -> None:
        self.backend = default_backend()

    def _derive_key(self, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=self.backend,
        )
        return base64.urlsafe_b64encode(kdf.derive(self.master_key.encode("utf-8")))

    def _generate_signature(self, data: dict, salt: bytes) -> str:
        data_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        key = base64.urlsafe_b64decode(self._derive_key(salt))
        h = hmac.new(key, data_str.encode(), hashlib.sha256)
        return base64.urlsafe_b64encode(h.digest()).decode()

    def verify_license(self, license_key: str) -> dict:
        try:
            combined = base64.urlsafe_b64decode(license_key.encode())
            salt = combined[:16]
            encrypted_data = combined[16:]

            try:
                cipher_suite = Fernet(self._derive_key(salt))
                decrypted_data = cipher_suite.decrypt(encrypted_data)
                parameters = json.loads(decrypted_data.decode())

                signature = parameters.pop('_signature')
                expected_signature = self._generate_signature(parameters, salt)

                if not hmac.compare_digest(signature, expected_signature):
                    raise LicenseSignatureException("Неверная подпись лицензии")

                if 'period_end_date' in parameters:
                    exp_date = datetime.fromisoformat(parameters['period_end_date'])
                    if datetime.utcnow() > exp_date:
                        raise LicensePeriodException("Лицензия истекла", exp_date)

                return parameters
            except Exception:
                raise LicenseVerificationException("Не удалось верифицировать лицензию")

        except Exception as e:
            raise LicenseInvalidException(f"Невалидная лицензия: {str(e)}")

    def get_license_info(self, license_key: str) -> dict:
        try:
            combined = base64.urlsafe_b64decode(license_key.encode())
            salt = combined[:16]
            encrypted_data = combined[16:]

            try:
                cipher_suite = Fernet(self._derive_key(salt))
                decrypted_data = cipher_suite.decrypt(encrypted_data)
                parameters = json.loads(decrypted_data.decode())
                return parameters

            except Exception:
                raise LicenseVerificationException("Не удалось расшифровать лицензию")

        except Exception as e:
            raise LicenseInvalidException(f"Не удалось получить информацию о лицензии: {str(e)}")
