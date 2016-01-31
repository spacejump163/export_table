
# -*- encoding: utf-8 -*-

columns = {'Id': 0,
 'custom_delimit': 5,
 'int3': 2,
 'misc': 4,
 'position': 1,
 'treasure_info': 3}
index = {0: 0, 1: 1, 2: 2}
table = (
	(
		0,#Id:Id
		(
			1.0,
			2.0,
			3.0,
		),#position:地点
		(
			1,
			2,
			3,
		),#int3:三个整数
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
		),#treasure_info:宝箱信息
		(
			3,
			3.3,
			"""哈哈哈""",
		),#misc:杂项
		(
			"""我的;;;""",
			"""你的""",
		),#custom_delimit:自定义分隔符
	),#0
	(
		1,#Id:Id
		(
			1.0,
			-4.0,
			3.0,
		),#position:地点
		(
			2,
			3,
			4,
		),#int3:三个整数
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
				0.0,
				4,
			),
			(
				100.0,
				34,
			),
		),#treasure_info:宝箱信息
		(
			3,
			3.3,
			"""MMsf""",
		),#misc:杂项
		(
			"""大富;翁""",
			""";好的""",
		),#custom_delimit:自定义分隔符
	),#1
	(
		2,#Id:Id
		(
			1.0,
			-4.0,
			3.0,
		),#position:地点
		(
			3,
			4,
			5,
		),#int3:三个整数
		None,#treasure_info:宝箱信息
		(
			3,
			3.0,
			"""你的\"\"\"""",
		),#misc:杂项
		(
			""";工信处""",
			"""女部长;""",
		),#custom_delimit:自定义分隔符
	),#2
)