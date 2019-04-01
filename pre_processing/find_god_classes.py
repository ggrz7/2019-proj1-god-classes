import os, sys
import javalang as jl
import pandas as pd


def find_god_classes(dir_name):
	df = pd.DataFrame(columns=['class_name', 'method_num', 'path_to_source'])

	for root, dirs, files in os.walk(dir_name, topdown=False):
		for name in files:
			if name.endswith(".java"):
				with(open(root + "/" + name, 'r')) as jsc:

					tree = jl.parse.parse(jsc.read())

					for path, node in tree.filter(jl.parser.tree.ClassDeclaration):
						df = df.append({
							'class_name': node.name,
							'path_to_source': root + '/' + node.name + '.java',
							'method_num': len(node.methods)
						}, ignore_index=True, sort=-1)

	return filter_all_classes(df)


def filter_all_classes(all_classes):
	all_classes.sort_values('method_num', ascending=False, inplace=True)
	all_classes.reset_index(drop=True, inplace=True)

	cond = all_classes.method_num.mean() + 6 * all_classes.method_num.std()
	return all_classes.query('method_num > @cond')


if __name__ == '__main__':
	if len(sys.argv) < 2:
		print("Enter a the path to a program source code...")
		sys.exit(0)

	print(find_god_classes(sys.argv[1]))