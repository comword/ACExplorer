from pyUbiForge.misc.file_object import FileObjectDataWrapper
from pyUbiForge.misc.file_readers import BaseReader


class Reader(BaseReader):
	file_type = '4661AAEF'

	def __init__(self, file_object_data_wrapper: FileObjectDataWrapper):
		file_object_data_wrapper.read_bytes(2)
		count1 = file_object_data_wrapper.read_uint_32()
		file_object_data_wrapper.read_bytes(2 * count1)
		file_object_data_wrapper.read_bytes(4 * 6) # 6 floats
		count2 = file_object_data_wrapper.read_uint_32()
		for _ in range(count2):
			file_object_data_wrapper.read_bytes(24)
		file_object_data_wrapper.read_bytes(1)
		file_object_data_wrapper.out_file_write('\n')
