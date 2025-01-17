import time
import unittest
from typing import Type, Dict
import os
import traceback

from pyUbiForge2.api import log, BaseGame


class BaseGameTestCase:
    class BaseGameTestCase(unittest.TestCase):
        @classmethod
        def setUpGame(cls, game_class: Type[BaseGame], game_path: str):
            cls._game = game_class(game_path)
            return cls

        def test_setup(self):
            pass

        def _test_file(self, resource_type: int):
            failures = 0
            success = 0
            failure_reasons: Dict[str, int] = {}
            for forge_name, forge_file in self._game.forge_files.items():
                for data_file_id, data_file in forge_file.data_files.items():
                    for file_id, (resource_type_, file_name) in data_file.files.items():
                        if resource_type == resource_type_:
                            try:
                                self._game.get_file(file_id, forge_name, data_file_id)
                                success += 1
                            except Exception as e:
                                msg = str(e)
                                if not msg:
                                    msg = traceback.format_exc()
                                failure_reasons.setdefault(msg, 0)
                                failure_reasons[msg] += 1
                                failures += 1
                                sane_file_name = "".join(
                                    [
                                        c
                                        for c in file_name
                                        if c.isalpha() or c.isdigit() or c == " "
                                    ]
                                ).rstrip()
                                path = f"./error_format/{resource_type}/{self._game.GameIdentifier}/{forge_name}/{data_file_id:X}/{file_id:X}{sane_file_name}.bin"
                                os.makedirs(os.path.dirname(path), exist_ok=True)
                                try:
                                    self._game.get_file(
                                        file_id, forge_name, data_file_id, path
                                    )
                                except:
                                    pass
                                if failures >= 5000:
                                    time.sleep(0.1)
                                    for reason, count in sorted(
                                        failure_reasons.items(),
                                        key=lambda x: x[1],
                                        reverse=True,
                                    ):
                                        print(reason, count)
                                    raise Exception(
                                        f"{resource_type:08X}: Success {success}, Failure {failures}, {100*success/(success+failures)}%"
                                    )
            time.sleep(0.1)
            for reason, count in sorted(
                failure_reasons.items(), key=lambda x: x[1], reverse=True
            ):
                print(reason, count)
            msg = f"{resource_type:08X}: Success {success}, Failure {failures}, {100*success/(success+failures)}%"
            if failures:
                raise Exception(msg)
            else:
                print(msg)

        @unittest.skip
        def test_entity(self):
            self._test_file(0x0984415E)

        @unittest.skip
        def test_mesh(self):
            self._test_file(0x415D9568)

        @unittest.skip
        def test_lod_selector(self):
            self._test_file(0x51DC6B80)

        @unittest.skip
        def test_texture_map(self):
            self._test_file(0xA2B7E917)

        @unittest.skip
        def test_data_block(self):
            self._test_file(0xAC2BBF68)

        def test_get_file_counts(self):
            files = {}
            for forge_file in self._game.forge_files.values():
                for data_file in forge_file.data_files.values():
                    for resource_type, _ in data_file.files.values():
                        files.setdefault(resource_type, 0)
                        files[resource_type] += 1
            for resource_type, count in sorted(files.items(), key=lambda x: x[1], reverse=True):
                try:
                    cls = self._game.get_parser(resource_type)
                except:
                    print(f"{resource_type:08X}", count)
                else:
                    print(f"{resource_type:08X}", cls.__name__, count)

        @unittest.skip
        def test_decompress(self):
            start_time = time.time()
            for forge_file in self._game.forge_files.values():
                for data_file_id in forge_file.data_file_ids:
                    forge_file.get_decompressed_files(data_file_id)
                log.info(f"Finished decompressing {forge_file.file_name}")
            log.info(
                f"Finished decompressing all forge files in {round(time.time()-start_time)} seconds"
            )
