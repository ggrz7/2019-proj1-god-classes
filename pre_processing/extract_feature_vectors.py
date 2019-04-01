import os, sys, datetime
sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
import pandas as pd
import numpy as np
import javalang as jl

from pre_processing.find_god_classes import find_god_classes
from utils.misc import write_df_to_csv, sort_column_labels

DEF_FVS_DIR = "./res/feature_vectors"
FV_DIR = DEF_FVS_DIR + '/' + str(int(datetime.datetime.now().timestamp()*1000))


def extract_feature_vectors(god_classes):

	class_names = god_classes.class_name.tolist()
	all_feat_vectors = {}
	for src_path in god_classes.path_to_source.tolist():
		with(open(src_path, 'r')) as jsc:
			tree = jl.parse.parse(jsc.read())

			for path, node in tree.filter(jl.parser.tree.ClassDeclaration):
				if node.name in class_names:
					all_feat_vectors[node.name] = generate_all(node)
					write_df_to_csv(FV_DIR, all_feat_vectors[node.name], node.name)

	return all_feat_vectors


def generate_all(node):
	fields = get_fields(node)
	methods = get_methods(node)

	fv_dict = {}

	for method in node.methods:
		fv = generate_feat_vector(method, fields, methods)
		add_vector(fv, fv_dict)

	df = fv_dict_to_df(fv_dict)

	return df


def get_fields(node):
	return [field.declarators[len(field.declarators) - 1].name for field in node.fields]


def get_methods(node):
	return np.unique([method.name for method in node.methods])


def generate_feat_vector(method, fields, methods):
	row = {'method_name': method.name}

	acc_fields = get_fields_accessed_by_method(method, fields)
	acc_methods = get_methods_accessed_by_method(method, methods)

	for field in list(acc_fields)+list(acc_methods):
		row[field] = 1

	return row


def get_fields_accessed_by_method(method, fields):
	return np.unique([node.member for path, node in method.filter(jl.parser.tree.MemberReference) if node.member in fields])


def get_methods_accessed_by_method(method, methods):
	return np.unique([node.member for path, node in method.filter(jl.parser.tree.MethodInvocation) if node.member in methods])


def add_vector(fv, fv_dict):
	if fv['method_name'] in fv_dict:
		fv_dict[fv['method_name']].update(fv)
	else:
		fv_dict[fv['method_name']] = fv


def fv_dict_to_df(vec_dict):
	df = pd.DataFrame([vec_dict.get(k) for k in vec_dict.keys()])
	df = df.reindex(columns=sort_column_labels(df.columns.tolist()))
	df = df.fillna(0)
	df[[col for col in df.columns if col != 'method_name']] = df[
		[col for col in df.columns if col != 'method_name']].astype('int')

	return df


if __name__ == '__main__':

	if len(sys.argv) < 2:
		print("Enter a the path to a program source code...")
		sys.exit(0)

	gc = find_god_classes(sys.argv[1])
	extract_feature_vectors(gc)