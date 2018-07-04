#
# schemas.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
#
# Expected schemas for disk output format
#


PARTITION_SCHEMA = {
    'type': 'object',
    'properties': {
        'node': {'type': 'string'},
        'start': {'type': 'number'},
        'size': {'type': 'number'},
        'type': {'type': 'string'},
    }
}


DISK_SCHEMA = {
    'definitions': {
        'partition': PARTITION_SCHEMA,
    },
    'type': 'object',
    'properties': {
        'partitiontable': {
            'type': 'object',
            'properties': {
                'label': {'type': 'string'},
                'id': {'type': 'string'},
                'device': {'type': 'string'},
                'unit': {'type': 'string'},
                'partitions': {
                    'type': 'array',
                    'items': {'$ref': '#/definitions/partition'}
                },

            }
        }
    }
}
