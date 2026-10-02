"""Live database access. No guest realm or authentication overrides."""
from contextvars import ContextVar

namespace = ContextVar('nexus_namespace', default='')

def api_prefix():
    return '/api'

class ScopedDatabase:
    def __init__(self, database):
        self.database = database

    def __getitem__(self, name):
        return self.database[name]

    def __getattr__(self, name):
        return self[name]