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
            name='{basename}_list',
            initkwargs={'suffix': 'List'},
        ),
        # dynamic list
        routers.DynamicListRoute(
            url=r'^{prefix}/{methodname}/?$',
            name='{basename}_{methodnamehyphen}',
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
            name='{basename}_detail',
            initkwargs={'suffix': 'Instance'},
        ),
        # dynamic detail
        routers.DynamicDetailRoute(
            url=r'^{prefix}/{lookup}/{methodname}/?$',
            name='{basename}_{methodnamehyphen}',
            initkwargs={},
        ),
    ]
