import datetime


class LicenseException(Exception):
    pass


class LicenseSignatureException(LicenseException):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return f"LicenseError: {super().__str__()}"


class LicensePeriodException(LicenseException):
    def __init__(self, message, exp_date: datetime.datetime = None):
        self.exp_date = exp_date
        super().__init__(message)

    def __str__(self):
        if self.exp_date:
            return f"LicenseError (exp_date: {str(self.exp_date)}): {super().__str__()}"
        return f"LicenseError: {super().__str__()}"


class LicenseVerificationException(LicenseException):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return f"LicenseError: {super().__str__()}"


class LicenseInvalidException(LicenseException):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return f"LicenseError: {super().__str__()}"


class LicenseMaxCountException(LicenseException):
    def __init__(self, model_name, count):
        message = f"Превышено количество объектов={count} модели={model_name}"
        super().__init__(message)

    def __str__(self):
        return f"LicenseError: {super().__str__()}"


class LicenseNotFoundException(LicenseException):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return f"LicenseError: {super().__str__()}"


class LicenseMacException(LicenseException):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return f"LicenseError: {super().__str__()}"
