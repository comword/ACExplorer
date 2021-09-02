import numpy
from pyUbiForge.misc.file_object import FileObjectDataWrapper


class EntryTable:
    def __init__(self, forge: FileObjectDataWrapper, forge_file_version: int):
        self.index_count = forge.read_int_32()  # 0x4a
        self.dir_count = forge.read_int_32()  # 0x4e
        self.index_table_offset = forge.read_int_64()  # 0x52
        self.file_data_offset2 = forge.read_int_64()  # 0x5a
        self.first_index = forge.read_int_32()  # 0x62
        self.last_index = forge.read_int_32()  # 0x66
        self.meta_table_offset = forge.read_int_64()  # 0x6a
        self.directory_offset = forge.read_int_64()  # 0x72

        forge.seek(self.index_table_offset)  # To 0x7a
        self.index_table = forge.read_numpy([
            ('raw_data_offset', numpy.uint64),
            ('file_id', numpy.uint64),
            ('raw_data_size', numpy.uint32)
        ], 20 * self.index_count)

        forge.seek(self.meta_table_offset)
        if forge_file_version == 27:
            self.name_table = forge.read_numpy([
                ('raw_data_size', numpy.uint32),  # 0x0
                ('', numpy.uint64),  # 0x4
                ('', numpy.uint32),  # 0xC
                ('file_type', numpy.uint32),  # 0x10
                ('', numpy.uint64),
                ('', numpy.uint32),     # next file count
                ('', numpy.uint32),     # previous file count
                ('', numpy.uint32),
                ('', numpy.uint32),     # timestamp
                ('file_name', 'S128'),
                ('', numpy.uint32),
                ('', numpy.uint32),
                ('', numpy.uint32),
                ('', numpy.uint32),
                ('', numpy.uint32)
            ], 192 * self.index_count)
        elif forge_file_version == 29:
            self.name_table = forge.read_numpy([
                ('raw_data_size', numpy.uint32),  # 0x0
                ('', numpy.uint64),  # 0x4
                ('', numpy.uint32),  # 0xC
                ('file_type', numpy.uint32),  # 0x10
                ('', numpy.uint64),  # 0x18
                ('next_entry_idx', numpy.int32),  # 0x1c
                ('prev_entry_idx', numpy.int32),  # 0x20
                ('', numpy.uint32),  # 0x24
                ('timestamp', numpy.uint32),  # 0x28
                ('file_name', 'S255'),  # 0x2c
                ('name_length', numpy.byte),  # 0x12b
                ('', numpy.uint32),  # 0x12c
                ('', numpy.uint32),  # 0x130
                ('', numpy.uint32),  # 0x134
                ('', numpy.uint32),  # 0x138
                ('', numpy.uint32)  # 0x13c
            ], 320 * self.index_count)
        elif forge_file_version == 30:
            self.name_table = forge.read_numpy([
                ('', numpy.uint32),  # 0x0
                ('', numpy.uint32),  # 0x4
                ('', numpy.uint64),  # 0xC
                ('old_type', numpy.uint32),  # 0x10
                ('file_name', 'S255'),  # 0x14
                ('name_length', numpy.byte),  # 0x113
                ('timestamp', numpy.uint32),  # 0x114
                ('', numpy.uint32),  # 0x118
                ('prev_entry_idx', numpy.int32),  # 0x11c
                ('next_entry_idx', numpy.int32),  # 0x120
                ('', numpy.uint64),  # 0x124
                ('file_type', numpy.uint32),  # 0x12c
                ('', numpy.uint32),  # 0x130
                ('', numpy.uint64),  # 0x134
                ('raw_data_size', numpy.uint32)  # 0x13c
            ], 320 * self.index_count)
        else:
            raise Exception(
                f'Unsupported Forge file format : "{forge_file_version}"')
