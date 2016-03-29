from rest_framework import routers


class RestRouter(routers.SimpleRouter):
    routes = [
        # list
        routers.Route(
            url=r'^{prefix}/?$',
            mapping={
                'get': 'list',
                'post': 'create'
            },
            name='{basename}-list',
            initkwargs={'suffix': 'List'},
        ),
        # dynamic list
        routers.DynamicListRoute(
            url=r'^{prefix}/{methodname}/?$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={},
        ),
        # detail
        routers.Route(
            url=r'^{prefix}/{lookup}/?$',
            mapping={
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy',
            },
            name='{basename}-detail',
            initkwargs={'suffix': 'Instance'},
        ),
        # dynamic detail
        routers.DynamicDetailRoute(
            url=r'^{prefix}/{lookup}/{methodname}/?$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={},
        ),
    ]
