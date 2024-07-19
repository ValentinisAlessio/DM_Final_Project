import psycopg2
import pandas as pd
import re


query_10 = """
SELECT
    c_custkey,
    c_name,
    SUM(l_extendedprice * (1 - l_discount)) AS revenue,
    c_acctbal,
    n_name,
    c_address,
    c_phone,
    c_comment
FROM
    part_lineitem_order
    JOIN customer c ON c.c_custkey = o_custkey
    JOIN nation n ON c.c_nationkey = n.n_nationkey
WHERE
    o_orderdate >= DATE '1993-10-01'
    AND o_orderdate < DATE '1993-10-01' + INTERVAL '3' MONTH
    AND l_returnflag = 'R'
GROUP BY
    c_custkey,
    c_name,
    c_acctbal,
    c_phone,
    n_name,
    c_address,
    c_comment
ORDER BY
    revenue DESC;
"""

query_14 = """
SELECT
    100.00 * SUM(CASE
        WHEN p_type_prefix LIKE 'PROMO'
        THEN l_extendedprice * (1 - l_discount)
        ELSE 0
    END) / SUM(l_extendedprice * (1 - l_discount)) AS promo_revenue
FROM
    part_lineitem_order
WHERE
    l_shipdate >= DATE '1995-09-01'
    AND l_shipdate < DATE '1995-09-01' + INTERVAL '1' MONTH;
"""

query_17 = """
SELECT
    SUM(l_extendedprice) / 7.0 AS avg_yearly
FROM
    part_lineitem_order
WHERE
    p_brand = 'Brand#23'
    AND p_container = 'MED BOX'
    AND l_quantity < avg_quantity;
"""


def explain_analyze(query, conn, analyze = True):
    conn.rollback()
    with conn.cursor() as cur:
        if analyze:
            cur.execute(f"EXPLAIN ANALYZE {query}")
        else:
            cur.execute(f"EXPLAIN {query}")
        explain = cur.fetchall()
    return explain


if __name__ == "__main__":
    
    conn = psycopg2.connect(
        dbname = "dw_cs", 
        user = "postgres", 
        host= 'localhost',
        # host = '172.30.160.1',
        password = "postgres",
        port = 5432
    )

    conn.rollback()
    with conn.cursor() as cur:
        cur.execute("SET enable_seqscan = off;")
        cur.execute("SET enable_indexscan = on;")
        cur.execute("SET enable_bitmapscan = on;")
        cur.execute("SET enable_indexonlyscan = off;")
        cur.execute("SET enable_tidscan = off;")
        cur.execute("SET enable_material = on;")
        cur.execute("SET enable_nestloop = on;")
        cur.execute("SET enable_mergejoin = on;")
        cur.execute("SET enable_hashjoin = off;")
        cur.execute("SET enable_hashagg = on;")
        cur.execute("SET enable_sort = on;")
        cur.execute("SET enable_partition_pruning = off;")
        cur.execute("SET enable_partitionwise_join = off;")
        cur.execute("SET enable_partitionwise_aggregate = off;")
        conn.commit()

    query_list = [10,14,17]

    df = pd.DataFrame(columns = ["query", "Execution Rime [ms]"])

    pattern = re.compile(r"Execution Time: (\d+\.\d+) ms")

    for i in range(5):
        for query in query_list:
            query_name = f"query_{query}"

            print(f"Executing {query_name}")
            
            explain = explain_analyze(eval(query_name), conn)

            match = pattern.search(str(explain))

            df.loc[len(df)] = [query , float(match.group(1))]
            print(f"Execution Time: {match.group(1)} ms")

    df.sort_values("query", inplace = True)

    df.to_csv("times/materialize_index_benchmark.csv", index = False)


    conn.close()