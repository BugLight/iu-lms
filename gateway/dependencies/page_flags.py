from fastapi import Query


class PageFlags(object):
    def __init__(self, offset: int = Query(0, ge=0), limit: int = Query(10, ge=1)):
        self.offset = offset
        self.limit = limit
