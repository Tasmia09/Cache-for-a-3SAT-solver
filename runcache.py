#! python3
import sys
import os
import subprocess
import os.path


current_dir = os.getcwd();
input_file = sys.argv[1];
variable_list = open("variable.txt","a+");
output_file_name = "";
output_string = "";
line2 = ""
output_file_list = [];
final_set = {};

def setenv():
	print("Setting up the environment...\n")
	env_directory = os.path.join(current_dir, 'jhjr_math');
	os.environ["LD_LIBRARY_PATH"] = env_directory;

def runsat(problem_file, output_file_name,file):
	#subprocess.call(["./3sat -i %s"%(problem_file)],shell=True);
	subprocess.call(["./3sat -i %s"%(problem_file),">>","result/%s"%(output_file_name)],shell=True, stdout=file);
	parse_output(output_file_name);
	


def check_variable():
	with open(input_file) as fp:
		for line in fp:
			if "cnf" in line:
				variable = line.split()[2];
				if not check_variable_exists(variable):
					variable_list.write(variable+"\n");
					#...it will no longer need to look in the cache so send a flag to find_each_problem() so it does not look into the cache

def check_variable_exists(var):
	check = 0;
	for line in variable_list:
		if var in line:
			check+=1;
	if check > 0:
 		return True;
	else:
		return False;

def create_output_file(variable,problem_clause):
	make_result_directory(); #create the directory first
	current_dir = os.getcwd();
	output_file_name = variable + " "+ problem_clause+".txt";
	#listing the output file name so that I can intersect between them later
	output_directory = os.path.join(current_dir,'result/%s'%(output_file_name));
	file = open(output_directory,"w"); 
	runsat("clause_problem.cnf", output_file_name,file);

def make_result_directory():
	current_dir = os.getcwd();
	directory = os.path.join(current_dir, 'result');
	if not os.path.exists(directory):
		os.makedirs(directory);

def find_each_problem():
	with open(input_file) as fp:
		for line in fp:
			if "cnf" in line:
				cnf_line = "p cnf "+ line.split()[2] +" 1\n"
				variable = line.split()[2]
				for line in fp:
					problem_clause = line.replace('\n','');
					file = variable + " "+ problem_clause+".txt";
					output_file_list.append(file);
					if os.path.exists("result/%s"%file):
						print("Cache Hit...No need to compute\n");
					else:
						print("Cache Miss...Solving for the problem %s ..."%(problem_clause));
						#before solving the clause the tool will look into the cache. If it is in the cache, it wont't solve the problem. skip
						create_clause_file(cnf_line,line);
						create_output_file(variable,problem_clause);		
			
def create_clause_file(cnf_line,line):
	clause_file = open("clause_problem.cnf", "w");
	clause_file.write(cnf_line+line);
	

def parse_output(output_file_name):
	newline = "";
	fp = open("result/%s"%output_file_name, "r+");
	for i, line in enumerate(fp):
		if i >= 2 and "getrusage" not in line:
			newline = newline+line.split()[4]+"\n";
	fp.seek(0);
	fp.write(newline);
	fp.truncate();
	fp.close();
	

def instersect(file1):
	global final_set;
	f1 = set(open("result/%s"%file1).read().split());
	if len(final_set) == 0:
		final_set = f1;	
	final_set = set.intersection(f1, final_set);
	

if not os.path.exists("3sat.o"):
	subprocess.call("make");
setenv();
check_variable();
find_each_problem();

for i in range(len(output_file_list)):
	instersect(output_file_list[i])
	
final_set = sorted(final_set);

for i in range (len(final_set)):	
	print ("solve(): [SOLUTION] s = "+final_set[i]);
	
	
