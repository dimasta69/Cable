import datetime
import os.path


class LicenseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from utils.license.exception import LicenseNotFoundException

        if request.method in ['POST', 'PUT', 'PATCH']:
            from cabel.settings.django import BASE_DIR
            license_dir_path = BASE_DIR.parent / "license_api" / "license"
            if not os.path.exists(license_dir_path):
                license_dir_path.mkdir(parents=True, exist_ok=True)
                raise LicenseNotFoundException("Нет файлов в license")

            files = list(license_dir_path.glob("*.license"))
            files = [f for f in files if f.is_file()]

            if files:
                first_file = sorted(files)[0]

                with open(first_file, "r", encoding="utf-8") as file:
                    content = file.read()
                    self.process_license_content(content)
            else:
                raise LicenseNotFoundException("Папка license_api пуста")
        response = self.get_response(request)
        return response

    def process_license_content(self, content: str) -> None:
        from models_app import models
        from utils.license.license_manager import LicenseManager
        from utils.license.exception import LicenseMaxCountException, LicenseMacException, LicenseTimeException
        from utils.license.generete_mac_based_id import generate_stable_id_from_mac

        license_engine = LicenseManager()
        parameters = license_engine.get_license_info(content)

        if parameters['mac_id'] != generate_stable_id_from_mac():
            raise LicenseMacException('Не совпадает mac устройства.')
        if parameters['time_unlimited'] is None or parameters['period_end_date'] < datetime.datetime.now():
            raise LicenseTimeException(parameters['period_end_date'], datetime.datetime.now())

        for model_name, count in parameters['restrictions'].items():
            if getattr(models, model_name).objects.all().count() >= int(count):
                raise LicenseMaxCountException(model_name, count)
