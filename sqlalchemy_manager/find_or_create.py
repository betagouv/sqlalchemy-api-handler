class FindOrCreate():
    @classmethod
    def find_or_create(self, **props):
        existing = self.query.filter_by(**props).first()
        if existing:
            return existing
        new = self()
        for key, value in props.items():
            setattr(new, key, value)
        return new
