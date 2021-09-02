from pyUbiForge.misc.file_object import FileObjectDataWrapper
from pyUbiForge.misc.file_readers import BaseReader


class Reader(BaseReader):
	file_type = '49F4CA3E'

	def __init__(self, file_object_data_wrapper: FileObjectDataWrapper):
		file_object_data_wrapper.read_bytes(1)
		file_object_data_wrapper.read_id()
		file_object_data_wrapper.read_bytes(5)
		for _ in range(2):
			check_byte = file_object_data_wrapper.read_uint_8()
			if check_byte != 3:
				file_object_data_wrapper.read_id()

		file_object_data_wrapper.read_bytes(32)
