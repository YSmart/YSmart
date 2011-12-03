select 
	c_name,c_custkey,o_orderkey,o_orderdate,o_totalprice,sum(l_quantity)
from 
	(
		select 
			o_custkey,o_orderkey,o_orderdate,o_totalprice,l_quantity,t_sum_quantity
		from
			(
				select 
					o_custkey,o_orderkey,o_orderdate,o_totalprice,l_quantity
				from
					orders oo,
					lineitem l
				where 
					l.l_orderkey = oo.o_orderkey
			) tt1,
			(
				select 
					l_orderkey,sum(l_quantity) as t_sum_quantity
				from 
					lineitem
				group by 
					l_orderkey
			) tt2
		where
			tt1.o_orderkey = tt2.l_orderkey 
			and tt2.t_sum_quantity > 300
	) p, 
	customer cc
where 
	cc.c_custkey = p.o_custkey
group by 
	c_name,c_custkey,o_orderkey,o_orderdate,o_totalprice
order by 
	o_totalprice desc, o_orderdate;