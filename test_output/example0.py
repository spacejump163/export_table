# -*- coding: utf-8 -*-
from wrapper import DataDescription
_reload_all = True

_Keys = {
	"""""":
		5,
	"""treasure_info""":
		3,
	"""misc""":
		4,
	"""int3""":
		2,
	"""position""":
		1,
	"""Id""":
		0,
}
_Data = {
	1:
		(
			0, #Id:Id
			(
				1,
				2,
				3,
			), #position:地点
			(
				1,
				2,
				3,
			), #int3:三个整数
			(
				(
					0.1,
					0,
				),
				(
					0.2,
					2,
				),
				(
					0.7,
					3,
				),
			), #treasure_info:宝箱信息
			(
				3,
				3.3,
				'\xe5\x93\x88\xe5\x93\x88\xe5\x93\x88',
			), #misc:杂项
			None, #:注释
		),
	2:
		(
			1, #Id:Id
			(
				1.0,
				-4,
				3,
			), #position:地点
			(
				2,
				3,
				4,
			), #int3:三个整数
			(
				(
					0.1,
					0,
				),
				(
					0.2,
					2,
				),
				(
					0.7,
					3,
				),
				(
					0.5,
					6,
				),
			), #treasure_info:宝箱信息
			(
				3,
				3.3,
				'MMsf',
			), #misc:杂项
			None, #:注释
		),
	3:
		(
			2, #Id:Id
			(
				1.0,
				-4,
				3.0,
			), #position:地点
			(
				4,
				5,
				6,
			), #int3:三个整数
			(
			), #treasure_info:宝箱信息
			(
				3,
				3,
				'\xe4\xbd\xa0\xe7\x9a\x84',
			), #misc:杂项
			None, #:注释
		),
}
ata = DataDescription.DataDict(_Keys, _Data)
