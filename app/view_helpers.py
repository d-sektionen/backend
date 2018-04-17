def different_read_serializer(cls):
    class DifferentReadSerializer(cls):

        def __init__(self, *args, **kargs):
            super(DifferentReadSerializer, self).__init__(*args, **kargs)

        def get_serializer_class(self):
            if self.request.method == 'GET':
                return self.read_serializer_class

            # The read serializer does not support foreign keys in requests properly,
            # so return the normal serializer.
            return self.serializer_class

    return DifferentReadSerializer
