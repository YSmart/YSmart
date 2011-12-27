select	
	sum(l_extendedprice) / 7.0 as avg_yearly
from
	(
		select 
			l_partkey, l_quantity, l_extendedprice
		from 
			lineitem,
			part
		where 
			p_partkey = l_partkey
			and p_brand = 'Brand#34'
			and p_container = 'MED PACK'
	)touter,
	(
		select 
			l_partkey as lp, 0.2 * avg(l_quantity) as lq
		from 
			lineitem
		group by 
			l_partkey
	) tinner
where
	touter.l_partkey = tinner.lp
	and touter.l_quantity < tinner.lq;