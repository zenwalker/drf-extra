class AnyOfPermission:
    def __init__(self, *permissions):
        self.permissions = [p() for p in permissions]

    def __call__(self):
        return self

    def has_permission(self, request, views):
        return any(p.has_permission(request, views)
                   for p in self.permissions)

    def has_object_permission(self, request, view, obj):
        return any(p.has_object_permission(request, view, obj)
                   for p in self.permissions)
