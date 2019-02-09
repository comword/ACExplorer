from pyUbiForge.misc.file_object import FileObjectDataWrapper
from pyUbiForge.misc.file_readers import BaseReader
import numpy


class Reader(BaseReader):
	file_type = '1CBDE084'

	def __init__(self, py_ubi_forge, file_object_data_wrapper: FileObjectDataWrapper, out_file, indent_count):
		file_object_data_wrapper.read_str(2, out_file, indent_count)
		file_object_data_wrapper.read_id(out_file, indent_count)
		file_object_data_wrapper.out_file_write('\n', out_file, indent_count)

		for _ in range(2):
			py_ubi_forge.read_file.get_data_recursive(file_object_data_wrapper, out_file, indent_count)

		self.transformation_matrix = file_object_data_wrapper.read_numpy(numpy.float32, 64, out_file, indent_count).reshape((4, 4))
		file_object_data_wrapper.out_file_write('\n', out_file, indent_count)

		count1 = file_object_data_wrapper.read_uint_32(out_file, indent_count)

		self.files = []

		for _ in range(count1):
			file_object_data_wrapper.read_str(1, out_file, indent_count)
			self.files.append(
				file_object_data_wrapper.read_id(out_file, indent_count)
			)
		file_object_data_wrapper.out_file_write('\n', out_file, indent_count)