select 
	s_name,count(*) as numwait 
from 
	supplier,
	nation,
	(
		select
			sq12.l_suppkey as ls
		from
			(
				select
					sq1.l_orderkey, sq1.l_suppkey
				from
					(
						select 
							l_orderkey, l_suppkey 
						from 
							lineitem, 
							orders 
						where 
							o_orderkey = l_orderkey 
							and l_receiptdate > l_commitdate 
						 	and o_orderstatus = 'F'
					) sq1,
					(
						select 
							l_orderkey, count_distinct(l_suppkey) as count_suppkey, max(l_suppkey) as max_suppkey
						from   
							lineitem 
						group by 
							l_orderkey
					) sq2
					where
						sq1.l_orderkey = sq2.l_orderkey
					and ((sq2.count_suppkey > 1) 
					     or ((sq2.count_suppkey=1) and (sq1.l_suppkey <> sq2.max_suppkey)))
            ) sq12
            left outer join
	    (
		select  
			l_orderkey, count_distinct(l_suppkey) as count_suppkey, max(l_suppkey) as max_suppkey 
		from  
			lineitem 
		where  
			l_receiptdate > l_commitdate 
		group by 
			l_orderkey
	    ) sq3
            on
				sq12.l_orderkey = sq3.l_orderkey
		where
			(sq3.count_suppkey is null) 
			 or ((sq3.count_suppkey=1) and (sq12.l_suppkey = sq3.max_suppkey))
	) complex
where
	s_suppkey = complex.ls 
	and s_nationkey = n_nationkey 
	and n_name = 'IRAQ' 
group by 
	s_name 
order by
	numwait desc, s_name;