import os
import logging
from typing import Tuple, List
import numpy
import pyUbiForge
from pyUbiForge.misc import decompress
from pyUbiForge.misc.forge import BaseForge, DataFile
from pyUbiForge.misc.file_object import FileObjectDataWrapper


class Forge(BaseForge):
    """This is a container which houses pointers to the data for each forge file and methods to decompress it."""

    def __init__(self, path: str, forge_file_name: str):
        """Initiate the class and read the header tables to get the locations of the files.

        The forge file has a couple of data tables before the actual data that points to where the actual data is stored.
        These tables are parsed and the data from them stored for each datafile in self.datafiles for use later
        """
        BaseForge.__init__(self, path, forge_file_name)
        logging.info(f'Building file tree for {forge_file_name}')

        forge_file = FileObjectDataWrapper.from_file(self.path)
        # header
        if forge_file.read_bytes(8) != b'scimitar':
            return
        forge_file.seek(1, 1)
        forge_file_version, file_data_header_offset = forge_file.read_struct(
            'iQ')
        if forge_file_version != 27:
            raise Exception(
                f'Unsupported Forge file format : "{forge_file_version}"')
        forge_file.seek(file_data_header_offset + 36)
        file_data_offset = forge_file.read_int_64()
        forge_file.seek(file_data_offset)
        # File Data
        index_count, index_table_offset, file_data_offset2, name_table_offset, raw_data_table_offset = forge_file.read_struct(
            'i4x2q8x2q')
        forge_file.seek(index_table_offset)
        index_table = forge_file.read_numpy([
            ('raw_data_offset', numpy.uint64),
            ('file_id', numpy.uint64),
            ('raw_data_size', numpy.uint32)
        ], 20 * index_count)
        forge_file.seek(name_table_offset)
        name_table = forge_file.read_numpy([
            ('raw_data_size', numpy.uint32),
            ('', numpy.uint64),
            ('', numpy.uint32),
            ('file_type', numpy.uint32),
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
        ], 192 * index_count)
        for n in range(index_count):
            if index_table['raw_data_size'][n] != name_table['raw_data_size'][n]:
                raise Exception(
                    'These should be the same. Is something wrong?')
            self._datafiles[int(index_table['file_id'][n])] = DataFile(
                int(index_table['raw_data_offset'][n]),
                int(index_table['raw_data_size'][n]),
                name_table['file_name'][n].replace(
                    b'\x00', b'').decode("utf-8"),
                int(name_table['file_type'][n])
            )

        forge_file.close()

    @staticmethod
    def _read_compressed_data_section(raw_data_chunk: FileObjectDataWrapper) -> Tuple[int, List[bytes]]:
        """This is a helper function used in decompression"""
        raw_data_chunk.seek(2, 1)
        compression_type = raw_data_chunk.read_uint_8()
        raw_data_chunk.seek(3, 1)
        format_version = raw_data_chunk.read_uint_8()
        if format_version == 0:
            uncompressed_data_list = []
            comp_block_count = 1
            while comp_block_count == 1:
                try:
                    comp_block_count = raw_data_chunk.read_uint_8()
                except:
                    comp_block_count = 0
                    continue
                if comp_block_count != 1:
                    raise Exception(
                        'This file has a count not equal to 1. No example of this has been found yet. Please let the creator know where you found this.')
                # 'compressed_size', 'uncompressed_size'
                size_table = raw_data_chunk.read_numpy(
                    '<u4', comp_block_count * 8).reshape(-1, 2).astype(int)
                for size in size_table:  # Could do this using numpy and then vectorise the decompression
                    # I think this is the hash of the data
                    raw_data_chunk.seek(4, 1)
                    uncompressed_data_list.append(decompress(
                        compression_type, raw_data_chunk.read_bytes(size[0]), size[1]))

        elif format_version == 128:
            comp_block_count = raw_data_chunk.read_uint_32()
            # 'uncompressed_size', 'compressed_size'
            size_table = raw_data_chunk.read_numpy(
                '<u2', comp_block_count * 4).reshape(-1, 2).astype(int)
            uncompressed_data_list = []
            for size in size_table:  # Could do this using numpy and then vectorise the decompression
                # I think this is the hash of the data
                raw_data_chunk.seek(4, 1)
                uncompressed_data_list.append(decompress(
                    compression_type, raw_data_chunk.read_bytes(size[1]), size[0]))
        else:
            raise Exception(
                'Format version not known. Please let the creator know where you found this.')

        return format_version, uncompressed_data_list

    def decompress_datafile(self, datafile_id: int):
        """This is the decompression method

        Given a numerical id of a datafile that is present in the forge file, this method will decompress that datafile, storing
        the data in the pyUbiForgeMain instance which was given to this class. It will populate self.datafiles[datafile_id].files
        with mappings from numerical id to file_name for each file within the datafile. It will also add the datafile id to
        self.new_datafiles so that external applications (such as the UI wrapper ACExplorer) will know which datafiles have been
        decompressed and have data to be added to the UI.
        """
        repopulate_tree = self.datafiles[datafile_id].files == {}
        if datafile_id == 0 or datafile_id > 2 ** 40:
            return
        uncompressed_data_list = []

        with open(os.path.join(pyUbiForge.CONFIG.game_folder(pyUbiForge.game_identifier()), self.forge_file_name), 'rb', buffering=0) as forge_file:
            forge_file.seek(self.datafiles[datafile_id].raw_data_offset)
            raw_data_chunk = FileObjectDataWrapper.from_binary(
                forge_file.read(self.datafiles[datafile_id].raw_data_size))
        header = raw_data_chunk.read_bytes(8)
        if header == b'\x33\xAA\xFB\x57\x99\xFA\x04\x10':  # if compressed
            format_version, uncompressed_data_list = self._read_compressed_data_section(
                raw_data_chunk)
            if format_version == 128:
                if raw_data_chunk.read_bytes(8) == b'\x33\xAA\xFB\x57\x99\xFA\x04\x10':
                    _, uncompressed_data_list_ = self._read_compressed_data_section(
                        raw_data_chunk)
                    uncompressed_data_list += uncompressed_data_list_
                else:
                    raise Exception(
                        'Compression Issue. Second compression block not found')
            if len(raw_data_chunk.read_rest()) != 0:
                raise Exception('Compression Issue. More data found')
        else:
            format_version = 128
            raw_data_chunk_rest = header + raw_data_chunk.read_rest()
            if b'\x33\xAA\xFB\x57\x99\xFA\x04\x10' in raw_data_chunk_rest:
                raise Exception('Compression Issue')
            else:
                # The file is not compressed
                uncompressed_data_list.append(raw_data_chunk_rest)

        if format_version == 0:
            pyUbiForge.temp_files.add(datafile_id, self.forge_file_name, datafile_id, 0,
                                      self.datafiles[datafile_id].file_name, raw_file=b''.join(uncompressed_data_list))
            self.datafiles[datafile_id].files[datafile_id] = self.datafiles[datafile_id].file_name

        elif format_version == 128:
            write_to_disk = pyUbiForge.CONFIG.get('writeToDisk', False)
            dump_folder = pyUbiForge.CONFIG.get('dumpFolder', 'output')

            uncompressed_data = FileObjectDataWrapper.from_binary(
                b''.join(uncompressed_data_list))

            file_count = uncompressed_data.read_uint_16()
            index_table = []
            for _ in range(file_count):
                # file_id, data_size (file_size + header), extra16_count (for next line)
                index_table.append(uncompressed_data.read_struct('QIH'))
                uncompressed_data.seek(index_table[-1][2] * 2, 1)
            for index in range(file_count):
                file_type, file_size, file_name_size = uncompressed_data.read_struct(
                    '3I')
                file_id = index_table[index][0]
                file_name = uncompressed_data.read_bytes(
                    file_name_size).decode("utf-8")
                check_byte = uncompressed_data.read_uint_8()
                if check_byte == 1:
                    uncompressed_data.seek(3, 1)
                    unk_count = uncompressed_data.read_uint_32()
                    uncompressed_data.seek(12 * unk_count, 1)
                elif check_byte != 0:
                    raise Exception(
                        'Either something has gone wrong or a new value has been found here')

                raw_file = uncompressed_data.read_bytes(file_size)

                if file_name == '':
                    file_name = f'{file_id:016X}'
                pyUbiForge.temp_files.add(
                    file_id, self.forge_file_name, datafile_id, file_type, file_name, raw_file=raw_file)
                self.datafiles[datafile_id].files[file_id] = file_name
                if write_to_disk:
                    folder = os.path.join(
                        dump_folder,
                        pyUbiForge.game_identifier(),
                        self.forge_file_name,
                        self.datafiles[datafile_id].file_name,
                        f'{file_type:08X}'
                    )
                    if os.path.isfile(os.path.join(folder, f'{file_name}.{pyUbiForge.game_identifier().lower()}')):
                        duplicate = 1
                        while os.path.isfile(os.path.join(folder, f'{file_name}_{duplicate}.{pyUbiForge.game_identifier().lower()}')):
                            duplicate += 1
                        path = os.path.join(
                            folder, f'{file_name}_{duplicate}.{pyUbiForge.game_identifier().lower()}')
                    else:
                        path = os.path.join(
                            folder, f'{file_name}.{pyUbiForge.game_identifier().lower()}')
                    if not os.path.isdir(folder):
                        os.makedirs(folder)
                    try:
                        open(path, 'wb').write(raw_file)
                    except Exception as e:
                        logging.warning(
                            f'Error saving temporary file with path "{path}"\n{e}')

        else:
            raise Exception(
                'Format version not known. Please let the creator know where you found this.')

        if repopulate_tree:
            self.new_datafiles.append(datafile_id)
