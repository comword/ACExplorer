import json
import os


class Config:
	def __init__(self):
		try:
			with open(f"{os.path.dirname(__file__)}/../config.json") as f:
				self.CONFIG = json.load(f)
		except:
			self.CONFIG = {}

		default_config = {
			"missingNo": "resources/missingNo.png",

			"gameFolders": {
				"ACU": "",
				"R6S": "",
			},
			"loadedGame": "ACU",

			"dumpFolder": "output",

			"tempFilesMaxMemoryMB": 2048,
			"writeToDisk": False,
			"dev": False
		}

		for key, val in default_config.items():
			if key not in self.CONFIG:
				self.CONFIG[key] = val

		for key, val in default_config["gameFolders"].items():
			if key not in self.CONFIG["gameFolders"]:
				self.CONFIG["gameFolders"][key] = val

	@property
	def raw(self):
		return self.CONFIG

	def get(self, item, default=None):
		if item == 'dumpFolder':
			path = self.CONFIG.get(item, default)
			if path != '' and not os.path.isdir(path):
				os.makedirs(path)
			return path
		return self.CONFIG.get(item, default)

	def __setitem__(self, key, value):
		self.CONFIG[key] = value

	def game_folder(self, identifier):
		return self.CONFIG.get('gameFolders', {}).get(identifier, ".")

	def save(self):
		with open(f"{os.path.dirname(__file__)}/../config.json", 'w') as f:
			json.dump(self.raw, f, indent=4)


CONFIG = Config()
