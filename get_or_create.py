def get_or_create(session, Model, defaults=None, **kwargs):
    instance = session.query(Model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        kwargs |= defaults or {}
        instance = Model(**kwargs)
        session.add(instance)
        return instance