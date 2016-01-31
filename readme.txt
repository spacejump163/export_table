+导表工具使用说明
++使用方法
使用 python main.py来运行脚本
+++参数说明
* --input dir 指定输入目录，输入目录就是存excel的地方
* --output dir 指定输出目录，所有的输出py文件都放在这里
* --rules dir 指定额外rule文件目录，如果需要使用原来的map功能则需要建立相应的py文件，参考
* --comment 是否在输出的数据文件里给每个加列加注释
* -v 是否输出更多的信息，用于调试定位错误
+++使用范例
参考test_input/example.py和rule/example.py
+++mapper
* 可以用row_mapper来修改默认的解析行为，改变每一行的数据：包括改变数据值，加列减列
* 如果想改列名或加列减列，要用column_mapper,输出列表头（包括程序名和策划列名）
+++emitter
* 即原来的reducer，只是改了个我认为更易懂的名字。emitter可以把一份数据输出到多个文件（比如同一个表的不同列被导到服务器和客户端分用的2个数据文件
++文件组成
* xlrd是的第三方的excel读入工具
* main.py是工具入口