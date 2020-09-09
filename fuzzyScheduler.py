# It's like painting a runway with different paints

from cspProblem import CSP, Constraint
from display import Displayable
import sys
from collections import defaultdict
def time_transfor(time):		##time format change
    if time % 24 != 0:
        if int(time % 24) > 12:
            ans = str(day_num_reverse[str(time // 24)]) + " " + str((time % 24)-12) + 'pm'
        elif int(time % 24) <12:
            ans = str(day_num_reverse[str(time // 24)]) + " " + str(time % 24) + 'am'
        else:
            ans = str(day_num_reverse[str(time // 24)]) + " " + str(time % 24)  + 'pm'
    return ans
######construct the fuzzyScheduler object######
class CSP_1(CSP):
	def __init__(self, domains, constraints,task):
		"""pass cost and duration information to CSP
        """
		self.variables = set(domains)
		self.domains = domains
		self.constraints = constraints
		self.task = task			
		self.var_to_const = {var: set() for var in self.variables}
		for con in constraints:
			for var in con.scope:
				self.var_to_const[var].add(con)
###########csp to search#########
class Con_solver(Displayable):
	"""Solves a CSP with arc consistency and domain splitting
    """

	def __init__(self, csp, **kwargs):
		"""a CSP solver that uses arc consistency
        * csp is the CSP to be solved
        * kwargs is the keyword arguments for Displayable superclass
        """
		self.csp = csp
		super().__init__(**kwargs)  # Or Displayable.__init__(self,**kwargs)

	def make_arc_consistent(self, orig_domains=None, to_do=None):
		"""Makes this CSP arc-consistent using generalized arc consistency
        orig_domains is the original domains
        to_do is a set of (variable,constraint) pairs
        returns the reduced domains (an arc-consistent variable:domain dictionary)
        """
		if orig_domains is None:
			orig_domains = self.csp.domains
		if to_do is None:
			to_do = {(var, const) for const in self.csp.constraints
					 for var in const.scope}
		else:
			to_do = to_do.copy()  # use a copy of to_do
		domains = orig_domains.copy()
		self.display(2, "Performing AC with domains", domains)
		while to_do:
			var, const = self.select_arc(to_do)

			self.display(3, "Processing arc (", var, ",", const, ")")
			other_vars = [ov for ov in const.scope if ov != var]
			work_time = self.csp.task[other_vars[0]]['duration']
			new_domain = {val for val in domains[var]
						  if self.any_holds(domains, const, {var: val}, other_vars)}
			if new_domain != domains[var]:
				self.display(4, "Arc: (", var, ",", const, ") is inconsistent")
				self.display(3, "Domain pruned", "dom(", var, ") =", new_domain,
							 " due to ", const)
				domains[var] = new_domain
				add_to_do = self.new_to_do(var, const) - to_do
				to_do |= add_to_do  # set union
				self.display(3, "  adding", add_to_do if add_to_do else "nothing", "to to_do.")
			self.display(4, "Arc: (", var, ",", const, ") now consistent")
		self.display(2, "AC done. Reduced domains", domains)
		return domains

	def new_to_do(self, var, const):
		"""returns new elements to be added to to_do after assigning
        variable var in constraint const.
        """
		return {(nvar, nconst) for nconst in self.csp.var_to_const[var]
				if nconst != const
				for nvar in nconst.scope
				if nvar != var}

	def select_arc(self, to_do):
		"""Selects the arc to be taken from to_do .
        * to_do is a set of arcs, where an arc is a (variable,constraint) pair
        the element selected must be removed from to_do.
        """
		return to_do.pop()

	def any_holds(self, domains, const, env, other_vars, ind=0):
		"""returns True if Constraint const holds for an assignment
        that extends env with the variables in other_vars[ind:]
        env is a dictionary
        Warning: this has side effects and changes the elements of env
        """
		work_time = self.csp.task[other_vars[0]]['duration'] #### let the task be processed in sequential
		if ind == len(other_vars):
			return const.holds(env)
		else:
			var = other_vars[ind]
			for val in domains[var]:
				# env = dict_union(env,{var:val})  # no side effects!
				env[var] = val + work_time
				if self.any_holds(domains, const, env, other_vars, ind + 1):
					return True
			return False

	def solve_one(self, domains=None, to_do=None):
		"""return a solution to the current CSP or False if there are no solutions
        to_do is the list of arcs to check
        """
		if domains is None:
			domains = self.csp.domains
		new_domains = self.make_arc_consistent(domains, to_do)
		if any(len(new_domains[var]) == 0 for var in domains):
			return False
		elif all(len(new_domains[var]) == 1 for var in domains):
			self.display(2, "solution:", {var: select(
				new_domains[var]) for var in new_domains})
			return {var: select(new_domains[var]) for var in domains}
		else:
			var = self.select_var(x for x in self.csp.variables if len(new_domains[x]) > 1)
			if var:
				dom1, dom2 = partition_domain(new_domains[var])
				self.display(3, "...splitting", var, "into", dom1, "and", dom2)
				new_doms1 = copy_with_assign(new_domains, var, dom1)
				new_doms2 = copy_with_assign(new_domains, var, dom2)
				to_do = self.new_to_do(var, None)
				self.display(3, " adding", to_do if to_do else "nothing", "to to_do.")
				return self.solve_one(new_doms1, to_do) or self.solve_one(new_doms2, to_do)

	def select_var(self, iter_vars):
		"""return the next variable to split"""
		return select(iter_vars)


def partition_domain(dom):
	"""partitions domain dom into two.
    """
	split = len(dom) // 2
	dom1 = set(list(dom)[:split])
	dom2 = dom - dom1		#find out all possible combination for task domains
	return dom1, dom2


def copy_with_assign(domains, var=None, new_domain={True, False}):
	"""create a copy of the domains with an assignment var=new_domain
    if var==None then it is just a copy.
    """
	newdoms = domains.copy()
	if var is not None:
		newdoms[var] = new_domain
	return newdoms


def select(iterable):
	"""select an element of iterable. Returns None if there is no such element.

    This implementation just picks the first element.
    For many of the uses, which element is selected does not affect correctness,
    but may affect efficiency.
    """
	for e in iterable:
		return e  # returns first element found


######Get the domain and constraint for task from input file#######

input_file = sys.argv[1]

task = defaultdict(dict)
domain_fs= defaultdict(dict)

a=[]            				##stand for information for input file
cons=[]         				#To store constraint
test_cons=[]					#sample test
start_time = 0					#assume we have a time line, start at mon 00:00
Cost={}							#cost information for soft domain
time_list=[]					#all of the available timetable
for day_list in range(0,5):
	for cur in range(9, 18):
		time_list.append(cur+day_list*24)
day_num={'mon':0, 'tue':24, 'wed':48, 'thu':72 ,'fri':96}
day_num_reverse={'0':'mon', '1':'tue', '2':'wed', '3':'thu' ,'4':'fri'}
condition_1=['starts-before','starts-after','ends-before']
condition_2=['ends-after','starts-in','starts-before']
condition_3=['ends-before','starts-after','ends-after']


def before(x,y):
	if x<=y:
		return 1
	return 0
def same_day(x,y):
	if (x<=24 and y<=24) \
	or (x<=24*2 and y<=24*2)\
	or (x<=24*3 and y<=24*3)\
	or (x<=24*4 and y<=24*4)\
	or (x<=24*5 and y<=24*5):
		return 1
	return 0
def after(x,y):
	if x>=y:
		return 1
	return 0
def starts_at(x,y):
	if y == x:
		return 1
	return 0
def starts_before_1(day,time):
	if time[-2:] == 'am' or time[:-2]=='12':
		x = day_num[day]+int(time[:-2])
	else:
		x = day_num[day] + int(time[:-2])+12
	return x
def starts_after_1(day,time):
	if time[-2:] == 'am' or time[:-2]=='12':
		x = day_num[day] + int(time[:-2])
	else:
		x = day_num[day] + int(time[:-2]) + 12
	return x
def ends_before_1(day,time):
	if time[-2:] == 'am' or time[:-2]=='12':
		x = day_num[day] + int(time[:-2])
	else:
		x = day_num[day] + int(time[:-2]) + 12
	return x
def ends_after_1(day,time):
	if time[-2:] == 'am' or time[:-2]=='12':
		x = day_num[day] + int(time[:-2])
	else:
		x = day_num[day] + int(time[:-2]) + 12
	return x
def starts_in(day1,time1,day2,time2):
	if time1[-2:]=='am' or time1[:-2]=='12':
		x=day_num[day1] + int(time1[:-2])
		if time2[-2:]=='am' or time2[:-2]=='12':
			y = day_num[day2] + int(time2[:-2])
		elif time2[-2:]=='pm':
			y = day_num[day2] + int(time2[:-2]) + 12
	elif time1[-2:]=='pm':
		x = day_num[day1]+ int(time1[:-2])
		if time2[-2:]=="am" or time2[:-2]=='12':
			y = day_num[day2] + int(time2[:-2])
		else:
			y = day_num[day2] + int(time2[:-2])+12
	list=[x,y]
	return list
def ends_in(day1,time1,day2,time2):
	if time1[-2:]=='am' or time1[:-2]=='12':
		x=day_num[day1] + int(time1[:-2])
		if time2[-2:]=='am' or time2[:-2]=='12':
			y = day_num[day2] + int(time2[:-2])
		else:
			y = day_num[day2] + int(time2[:-2])+12
	elif time1[-2:]=='pm':
		x = day_num[day1]+ int(time1[:-2])
		if time2[-2:]=="am" or time2[:-2]=='12':
			y = day_num[day2] + int(time2[:-2])
		else:
			y = day_num[day2] + int(time2[:-2])+12
	list=[x,y]
	return list
def starts_before(time):
	list=[]
	if time[-2:]=="am" or time[:-2]=='12':
		x = int(time[:-2])
	else:
		x = int(time[:-2])+12
	for i in day_num:
		list.append(x+day_num[i])
	return list
def ends_before(time):
	list = []
	if time[-2:]=="am" or time[:-2]=='12':
		x = int(time[:-2])
	else:
		x = int(time[:-2])+12
	for i in day_num:
		list.append(x+day_num[i])
	return list
def starts_after(time):
	list = []
	if time[-2:]=="am" or time[:-2]=='12':
		x = int(time[:-2])
	else:
		x = int(time[:-2])+12
	for i in day_num:
		list.append(x + day_num[i])
	return list
def ends_after(time):
	list=[]
	if time[-2:]=="am" or time[:-2]=='12':
		x = int(time[:-2])
	else:
		x = int(time[:-2])+12
	for i in day_num:
		ans=x + day_num[i]
		list.append(ans)
	return list
def compute_time(time):
	list = []
	if time[-2:]=="am" or time[:-2]=='12':
		x = int(time[:-2])
	else:
		x = int(time[:-2])+12
	for i in day_num:
		list.append(x+day_num[i])
	return list
#####in order to extract useful information#####
file = open(f'{input_file}', "r")
for eachline in file:
	a.append(eachline.strip("\n").split(","))
for i in a:

	cur_list = time_list.copy()
	if(i[0]=='task'):
		b=i[1].strip(" ").split(" ")
		for i in range(1,len(b)):
			task[b[0]]['duration']=int(b[i])
			domain_fs[b[0]]=set(cur_list)
	elif(i[0]=='domain'):
		b=i[1].strip(" ").split(" ")

		if b[1]=='ends-by':
			cost = b[-1]
			context = " ".join(b[1:-1])
			Cost[b[0]] = int(cost)
			if context!=' ':	
				# task[b[0]]['soft']=context.strip("ends-by")
				if context.strip("ends-by").split(" ")[1]:
					day = context.strip("ends-by").split(" ")[1]
				if context.strip("ends-by").split(" ")[2]:
					time = context.strip("ends-by").split(" ")[2]
				if context.strip("ends-by").split(" ")[1] in day_num:
					if len(time.split('am'))==2:
						task[b[0]]['soft'] = start_time + day_num[day]+int(time.strip('am'))
					else:
						task[b[0]]['soft'] = start_time + day_num[day]+int(time.strip('pm'))+12
		elif b[1]=='starts-before' and len(b)>3:
			del_list=[]
			day,time = b[2],b[3]
			if domain_fs[b[0]]:
				cur = list(domain_fs[b[0]])
				neck = starts_before_1(day,time)
				for plan in cur:
					if plan >= neck:
						del_list.append(plan)
				for d in del_list:
					if d in cur:
						cur.remove(d)
			domain_fs[b[0]] = set(cur)
			
		elif b[1]=='starts-after' and len(b)>3:
			del_list=[]
			day,time = b[2],b[3]
			if domain_fs[b[0]]:
				cur = list(domain_fs[b[0]])
				neck = starts_after_1(day,time)
				for plan in cur:
					if plan <= neck:
						del_list.append(plan)
				for d in del_list:
					if d in cur:
						cur.remove(d)
			domain_fs[b[0]] = set(cur)
			
		elif b[1]=='ends-before' and len(b)>3:
			del_list=[]
			day,time = b[2],b[3]
			if domain_fs[b[0]]:
				cur = list(domain_fs[b[0]])
				neck = ends_before_1(day,time)
				for plan in cur:
					if plan + task[b[0]]['duration']>= neck:
						del_list.append(plan)
				for d in del_list:
					if d in cur:
						cur.remove(d)
			domain_fs[b[0]] = set(cur)
			
		elif b[1]=='ends-after' and len(b)>3:
			del_list=[]
			day,time = b[2],b[3]
			if domain_fs[b[0]]:
				cur = list(domain_fs[b[0]])
				neck = ends_after_1(day,time)
				for plan in cur:
					if plan +task[b[0]]['duration']<= neck:
						del_list.append(plan)
				for d in del_list:
					if d in cur:
						cur.remove(d)
			domain_fs[b[0]] = set(cur)
		elif b[1]=='starts-in':
			day1,time1,day2,time2 = b[2],b[3].split("-")[0],b[3].split("-")[1],b[4]
			if domain_fs[b[0]]:
				del_list=[]
				cur = list(domain_fs[b[0]])
				time_range = starts_in(day1,time1,day2,time2)
				for plan in cur:
					if plan <= time_range[0] or plan >= time_range[1]:
						del_list.append(plan)
				for d in del_list:
					if d in cur:
						cur.remove(d)
			domain_fs[b[0]]=set(cur)
			
		elif b[1]=="ends-in":
			day1, time1, day2, time2 = b[2], b[3].split("-")[0], b[3].split("-")[1], b[4]
			if domain_fs[b[0]]:
				del_list=[]
				cur = list(domain_fs[b[0]])
				time_range = ends_in(day1,time1,day2,time2)
				for plan in cur:
					if plan +task[b[0]]['duration']<= time_range[0] or plan+task[b[0]]['duration'] <= time_range[1]:
						del_list.append(plan)
				for d in del_list:
					if d in cur:
						cur.remove(d)
			domain_fs[b[0]] = set(cur)
			
		elif b[1]=="starts-before" and len(b)==3:
			time = b[2]
			if domain_fs[b[0]]:
				del_list=[]
				cur = list(domain_fs[b[0]])
				time_range = starts_before(time)
				for plan in cur:
					if plan<=17:
						if plan>=time_range[0]:
							del_list.append(plan)
					if plan<=41:
						if plan>=time_range[1]:
							del_list.append(plan)
					if plan<=65:
						if plan>=time_range[2]:
							del_list.append(plan)
					if plan<=89:
						if plan>=time_range[3]:
							del_list.append(plan)
					if plan<=113:
						if plan>=time_range[4]:
							del_list.append(plan)
				for d in del_list:
					if d in cur:
						cur.remove(d)
			domain_fs[b[0]] = set(cur)
			
		elif b[1]=="ends-before" and len(b)==3:
			time = b[2]
			if domain_fs[b[0]]:
				del_list=[]
				cur = list(domain_fs[b[0]])
				time_range = ends_before(time)
				for plan in cur:
					if plan<=17:
						if plan+task[b[0]]['duration']>=time_range[0]:
							del_list.append(plan)
					if plan<=41:
						if plan+task[b[0]]['duration']>=time_range[1]:
							del_list.append(plan)
					if plan<=65:
						if plan+task[b[0]]['duration']>=time_range[2]:
							del_list.append(plan)
					if plan<=89:
						if plan+task[b[0]]['duration']>time_range[3]:
							del_list.append(plan)
					if plan<=113:
						if plan+task[b[0]]['duration']>=time_range[4]:
							del_list.append(plan)
				for d in del_list:
					if d in cur:
						cur.remove(d)
			domain_fs[b[0]] = set(cur)
			
		elif b[1]=="starts-after" and len(b)==3:
			del_list=[]
			time = b[2]
			if domain_fs[b[0]]:
				cur = list(domain_fs[b[0]])
				time_range = starts_after(time)
				for plan in cur:
					if plan<=17:
						if plan<=time_range[0]:
							del_list.append(plan)
					if plan<=41:
						if plan<=time_range[1]:
							del_list.append(plan)
					if plan<=65:
						if plan<=time_range[2]:
							del_list.append(plan)
					if plan<=89:
						if plan<=time_range[3]:
							del_list.append(plan)
					if plan<=113:
						if plan<=time_range[4]:
							del_list.append(plan)
				for d in del_list:
					if d in cur:
						cur.remove(d)
			domain_fs[b[0]] = set(cur)
			
		elif b[1]=="ends-after" and len(b)==3:
			del_list=[]
			time = b[2]
			if domain_fs[b[0]]:
				cur = list(domain_fs[b[0]])
				time_range = ends_after(time)
				for plan in cur:
					if plan<=17:
						if plan+task[b[0]]['duration']>=time_range[0]:
							del_list.append(plan)
					if plan<=41:
						if plan+task[b[0]]['duration']<=time_range[1]:
							del_list.append(plan)
					if plan<=65:
						if plan+task[b[0]]['duration']<=time_range[2]:
							del_list.append(plan)
					if plan<=89:
						if plan+task[b[0]]['duration']<=time_range[3]:
							del_list.append(plan)
					if plan<=113:
						if plan+task[b[0]]['duration']<=time_range[4]:
							del_list.append(plan)
				for d in del_list:
					if d in cur:
						cur.remove(d)
			domain_fs[b[0]] = set(cur)
			
		else:
			if b[1]=="mon":
				del_list = []
				if domain_fs[b[0]]:
					cur = list(domain_fs[b[0]])
					for plan in cur:
						if plan>day_num[b[1]]+24:
							del_list.append(plan)
					for d in del_list:
						if d in cur:
							cur.remove(d)
				domain_fs[b[0]] = set(cur)
				
			if b[1]=="tue" or b[1]=="wed" or b[1]=="thu" or b[1]=="fri" :
				del_list = []
				if domain_fs[b[0]]:
					cur = list(domain_fs[b[0]])
					for plan in cur:
						if plan >=day_num[b[1]]+24 or plan <=day_num[b[1]]:
							del_list.append(plan)
					for d in del_list:
						if d in cur:
							cur.remove(d)
				domain_fs[b[0]] = set(cur)
				
			elif b[1][-2:]=='am' or b[1][-2:]=="pm":
				del_list_mon = []
				del_list_tue = []
				del_list_wed = []
				del_list_thu = []
				del_list_fri = []
				time = b[1]
				if domain_fs[b[0]]:
					cur = list(domain_fs[b[0]])
					time_range = compute_time(b[1])

					for plan in cur:
						if plan!=time_range[0] and plan<=17:
								del_list_mon.append(plan)
						if plan!=time_range[1] and 17<plan<=41:
								del_list_tue.append(plan)
						if plan!=time_range[2] and 41<plan<=65:
								del_list_wed.append(plan)
						if plan!=time_range[3] and 65<plan<=89:
								del_list_thu.append(plan)
						if plan!=time_range[4] and 89<plan<=113:
								del_list_fri.append(plan)

					for d in del_list_mon:
						if d in cur:
							cur.remove(d)
					for d in del_list_tue:
						if d in cur:
							cur.remove(d)
					for d in del_list_wed:
						if d in cur:
							cur.remove(d)
					for d in del_list_thu:
						if d in cur:
							cur.remove(d)
					for d in del_list_fri:
						if d in cur:
							cur.remove(d)
				domain_fs[b[0]] = set(cur)
				
	elif(i[0]=='constraint'):
		b=i[1].strip(" ").split(" ")
		test_cons.append(((b[0],b[-1]),before))
		if b[1]=='before':
			cons.append(Constraint((b[0],b[-1]),before))
		if b[1]=='same-day':
			cons.append(Constraint((b[0],b[-1]),same_day))
		if b[1]=='after':
			cons.append(Constraint((b[0],b[-1]),after))
		if b[1]=='starts-at':
			cons.append(Constraint((b[0],b[-1]),starts_at))



fuzzyScheduler = CSP_1(domain_fs,cons,task)
solution=Con_solver(fuzzyScheduler).solve_one()

if solution:
	cost = 0
	for i in solution:
		if 'soft' in task[i]:
			if solution[i]+task[i]['duration']<task[i]['soft']:
				cost = cost +0
			else:
				cost = (solution[i]+task[i]['duration']-task[i]['soft'])*Cost[i]+cost
		else:
			cost=cost+0
		x = time_transfor(solution[i])
		print(i,end=":")
		print(x)
	print(f"cost:{cost}")
else:
	print('No solution')
