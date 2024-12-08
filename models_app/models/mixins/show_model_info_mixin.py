class ShowModelInfoMixin:
    def show_info(self):
        """Custom method to show record fields inside the console"""
        print("-" * 20)
        fields = [field.name for field in list(self._meta.fields)]
        for field in [f"{field}: {getattr(self, field)}" for field in fields]:
            print(field, end="\n")
        print("-" * 20)
