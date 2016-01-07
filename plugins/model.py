# -*- coding: UTF-8 -*-
# 自动填表脚本，用于自动从messiah仓库中读取原本需要策划填写在excel中的数据
import os
from xml.dom.minidom import parse
import xml.dom.minidom
# 提取给定的package路径下的
type_list = ("Model", )
packages = {} #{"DM35/0001":{"Model":{}}}

def pares_str(x):
	if isinstance(x, unicode):
		x = x.encode('utf-8')
	else:
		x = str(x)
	return x

# 仓库名，package名，然后提取出package下所有是type类型的路径
def gather_data(repository, package_path, id):
	dt = xml.dom.minidom.parse("../../../Resource/Package/Repository/" + repository + "/resource.repository")
	collection = dt.documentElement
	items = collection.getElementsByTagName("Item")
	print items.length
	for item in items:
		res_type = item.getElementsByTagName("Type")[0].childNodes[0].data
		res_package = item.getElementsByTagName("Package")[0].childNodes[0].data
		if res_type == type_list[id] and res_package == package_path:
			print package_path + "/" + item.getElementsByTagName("Name")[0].childNodes[0].data
	print "-------------"

def gather_by_path(path, id):
	repository_index = path.index("/")
	repository = path[0 : repository_index]
	package_path = path[repository_index+1 : len(path)]
	gather_data(repository, package_path, id)

def gather_all_data(repository):
	dt = xml.dom.minidom.parse("../../../Resource/Package/Repository/" + repository + "/resource.repository")
	collection = dt.documentElement
	items = collection.getElementsByTagName("Item")
	for item in items:
		res_type = item.getElementsByTagName("Type")[0].childNodes[0].data
		res_package = item.getElementsByTagName("Package")[0].childNodes[0].data
		if not item.getElementsByTagName("Name")[0].childNodes:
			continue
		name = item.getElementsByTagName("Name")[0].childNodes[0].data
		if not packages.has_key(res_package):
			packages[res_package] = {}
		if not packages[res_package].has_key(res_type):
			packages[res_package][res_type] = []
		packages[res_package][res_type].append(pares_str(res_package + "/" + name))
		#print res_type +"--"+res_package + "/" + name


# 全局遍历一遍，找到所有的仓库，并对package进行归类存储
def checkout_all_rep():
	for file in os.listdir("../../../Resource/Package/Repository/"):
		path = os.path.join("../../../Resource/Package/Repository/", file)
		if os.path.isdir(path):
			gather_all_data(file)

def fun(cell_value):
    pass

if __name__ == '__main__':
	#gather_data("DM35_jianmin.local", "DM35_Char/0001", 0)
	#gather_by_path("DM35_jianmin.local/DM35_Char/0001", 0)
	#checkout_all_rep()
	gather_all_data("DM35_jianmin.local")