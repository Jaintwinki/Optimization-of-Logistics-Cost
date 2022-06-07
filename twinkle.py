#############################################################

from scipy.optimize import linprog

hsd_rate1 = 68
hsd_rate2 = 90
total_demand = 58000
network_cons = 1.5
road_len = 17
demand_per_day = (total_demand/(road_len*2))*network_cons

def diesel_price(base_rate, rate1, rate2):
	price_per_km_per_ton = base_rate + base_rate*0.5*(rate2-rate1)/rate1
	return price_per_km_per_ton


s1_price = 330
s1_avg_dist = 95
s1_cap = 1000
s1_base_rate = 3
s1_per_km_per_ton_price = diesel_price(s1_base_rate,hsd_rate1,hsd_rate2)


s2_price = 260
s2_avg_dist = 140
s2_cap = 1000
s2_base_rate = 2.9
s2_per_km_per_ton_price = diesel_price(s2_base_rate,hsd_rate1,hsd_rate2)

st1_cap = 32000
st1_load_cost = 11
st1_first_km_cost = 14
st1_after_first_km_cost = 7

st1_price = 230
st1_avg_dist = 140
st1_base_rate = 2.45
hsd_rate2_st1 = 71
st1_per_km_per_ton_price = diesel_price(st1_base_rate,hsd_rate1,hsd_rate2_st1)


def dis_cost_finder(loc1, loc2, first_km_cost, per_km_cost):

	if abs(loc2-loc1)<1:
		return first_km_cost
	else:
		return first_km_cost + per_km_cost*(abs(loc2-loc1)-1)


def cost_optmizer(obj, lhs_eq, rhs_eq, bnd):

	opt = linprog(c=obj,A_eq=lhs_eq, b_eq=rhs_eq, bounds=bnd, 
				method="revised simplex")
	return opt

start = -9
end = 8.25
i = start
net_st1 = st1_cap

count = 1
day_wise_requirement = []
day_wise_cost = []
s2_bound = 0


while i < end:

	if count == 23:

		adder = 0.5

	else:

		adder = 0.75

	s1_avg_dist = s1_avg_dist+adder
	s2_avg_dist = s2_avg_dist+adder
	cost_s1_coeff = (s1_price + s1_avg_dist*s1_per_km_per_ton_price)
	cost_s2_coeff = (s2_price + s2_avg_dist*s2_per_km_per_ton_price)

	original_cost = st1_price + st1_avg_dist*st1_per_km_per_ton_price
	working_cap_cost = original_cost + original_cost*0.33

	if count == 23:
		cost_st1_coeff = working_cap_cost + st1_load_cost + dis_cost_finder(0,8, st1_first_km_cost, st1_after_first_km_cost)
	else:
		cost_st1_coeff = working_cap_cost + st1_load_cost + dis_cost_finder(0,i, st1_first_km_cost, st1_after_first_km_cost)

	objective = [cost_s1_coeff, cost_s2_coeff, cost_st1_coeff]

	if count == 9:
		s2_bound = s2_cap

	bnd = [(s1_cap, s1_cap),  # Bounds of S1
		(0, s2_bound),     # Bounds of s2
		(0, net_st1)]   # Bounds of st1

	lhs_eq = [[1 , 1, 1]]
	rhs_eq = [total_demand/(road_len*2)*network_cons]

	if count == 23:
		rhs_eq = [total_demand/(road_len*2)*network_cons*(2/3)]

	opt = cost_optmizer(objective,lhs_eq, rhs_eq, bnd)

	day_wise_requirement.append(opt.x)
	day_wise_cost.append(objective)

	count +=1
	net_st1 = net_st1 - opt.x[2]
	i += network_cons/2


S1_cost = []
S1_total_cost = 0
S1_total_mat = 0
S2_cost = []
S2_total_cost = 0
S2_total_mat = 0
St1_cost = []
St1_total_cost = 0
St1_total_mat = 0

total_cost = 0

for i in range(len(day_wise_requirement)):

	print("Day %d"%(i+1), " requirement", " S1 : ", day_wise_requirement[i][0], " S2 : ", day_wise_requirement[i][1], " St1 : ", day_wise_requirement[i][2])
	total_cost += day_wise_requirement[i][0]*day_wise_cost[i][0] + day_wise_requirement[i][1]*day_wise_cost[i][1] + day_wise_requirement[i][2]*day_wise_cost[i][2]

	S1_cost.append(day_wise_requirement[i][0]*day_wise_cost[i][0])
	S1_total_mat += day_wise_requirement[i][0]
	S1_total_cost += day_wise_requirement[i][0]*day_wise_cost[i][0]

	S2_cost.append(day_wise_requirement[i][1]*day_wise_cost[i][1])
	S2_total_mat += day_wise_requirement[i][1]
	S2_total_cost += day_wise_requirement[i][1]*day_wise_cost[i][1]

	St1_cost.append(day_wise_requirement[i][2]*day_wise_cost[i][2])
	St1_total_mat += day_wise_requirement[i][2]
	St1_total_cost += day_wise_requirement[i][2]*day_wise_cost[i][2]





rent = 600000

print("Total material from S1 : ", S1_total_mat, " Total cost from S1 : ", S1_total_cost,  " Total cost from S1 (per ton): ", S1_total_cost/S1_total_mat)

print("Total material from S2 : ", S2_total_mat, " Total cost from S2 : ", S2_total_cost,  " Total cost from S2 (per ton): ", S2_total_cost/S2_total_mat)

print("Total material from Stock : ", St1_total_mat, " Total cost from Stock : ", St1_total_cost,  " Total cost from Stock (per ton): ", (St1_total_cost + rent)/St1_total_mat)


total_cost = total_cost + rent

print("Stock left : ",net_st1)
print("Total cost : ", total_cost)
print("Total cost per ton : ", total_cost/total_demand)
