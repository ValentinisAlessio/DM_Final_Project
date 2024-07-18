import psycopg2
import pandas as pd
import re

query_1 = """
SELECT
    l_returnflag,
    l_linestatus,
    SUM(l_quantity) AS sum_qty,
    SUM(l_extendedprice) AS sum_base_price,
    SUM(l_extendedprice * (1 - l_discount)) AS sum_disc_price,
    SUM(l_extendedprice * (1 - l_discount) * (1 + l_tax)) AS sum_charge,
    AVG(l_quantity) AS avg_qty,
    AVG(l_extendedprice) AS avg_price,
    AVG(l_discount) AS avg_disc,
    COUNT(*) AS count_order
FROM
    lineitem
WHERE
    l_shipdate <= DATE '1998-12-01' - INTERVAL '90' DAY
GROUP BY
    l_returnflag,
    l_linestatus
ORDER BY
    l_returnflag,
    l_linestatus;
"""

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
    customer,
    orders,
    lineitem,
    nation
WHERE
    c_custkey = o_custkey
    AND l_orderkey = o_orderkey
    AND o_orderdate >= DATE '1993-10-01'
    AND o_orderdate < DATE '1993-10-01' + INTERVAL '3' MONTH
    AND l_returnflag = 'R'
    AND c_nationkey = n_nationkey
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
        WHEN p_type LIKE 'PROMO%'
        THEN l_extendedprice * (1 - l_discount)
        ELSE 0
    END) / SUM(l_extendedprice * (1 - l_discount)) AS promo_revenue
FROM
    lineitem,
    part
WHERE
    l_partkey = p_partkey
    AND l_shipdate >= DATE '1995-09-01'
    AND l_shipdate < DATE '1995-09-01' + INTERVAL '1' MONTH;

"""

query_17 = """
SELECT
    SUM(l_extendedprice) / 7.0 AS avg_yearly
FROM
    lineitem,
    part
WHERE
    l_partkey = p_partkey
    AND p_brand = 'Brand#23'
    AND p_container = 'MED BOX'
    AND l_quantity < (
        SELECT
            0.2 * AVG(l_quantity)
        FROM
            lineitem
        WHERE
            p_partkey = l_partkey
    );
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
        cur.execute("SET enable_indexonlyscan = on;")
        cur.execute("SET enable_tidscan = off;")
        cur.execute("SET enable_material = off;")
        cur.execute("SET enable_nestloop = on;")
        cur.execute("SET enable_mergejoin = on;")
        cur.execute("SET enable_hashjoin = off;")
        cur.execute("SET enable_sort = on;")
        cur.execute("SET enable_partition_pruning = off;")
        cur.execute("SET enable_partitionwise_join = off;")
        cur.execute("SET enable_partitionwise_aggregate = off;")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_l_shipdate ON lineitem (l_shipdate);")
<<<<<<< HEAD
        cur.execute("CREATE INDEX IF NOT EXISTS idx_o_orderdate ON orders (o_orderdate);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_l_partkey ON lineitem (l_partkey);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_p_container ON part USING hash (p_container);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_p_brand ON part USING hash (p_brand);")    
=======
        cur.execute("CREATE INDEX IF NOT EXISTS idx_l_returnflag ON lineitem (l_returnflag);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_l_partkey ON lineitem (l_partkey);")    
>>>>>>> b659fa1dbaeb1a0b2b0e3ad5016254be96779001
        conn.commit()

    query_list = [1,10,14,17]

    df = pd.DataFrame(columns = ["query", "Execution Rime [ms]"])

    pattern = re.compile(r"Execution Time: (\d+\.\d+) ms")

    for i in range(5):
        for query in query_list:
            query_name = f"query_{query}"

            print(f"Executing {query_name}")
            if query == 10:
                with conn.cursor() as cur:
                    cur.execute("SET enable_bitmapscan = off;")
                    conn.commit()
            else:
                with conn.cursor() as cur:
                    cur.execute("SET enable_bitmapscan = on;")
                    conn.commit()
            
            explain = explain_analyze(eval(query_name), conn)

            match = pattern.search(str(explain))

            df.loc[len(df)] = [query , float(match.group(1))]
            print(f"Execution Time: {match.group(1)} ms")

    df.sort_values("query", inplace = True)

    df.to_csv("times/index_benchmark.csv", index = False)

    with conn.cursor() as cur:
        cur.execute("DROP INDEX IF EXISTS idx_l_shipdate;")
        cur.execute("DROP INDEX IF EXISTS idx_o_orderdate;")
        cur.execute("DROP INDEX IF EXISTS idx_l_partkey;")
        cur.execute("DROP INDEX IF EXISTS idx_p_container;")
        cur.execute("DROP INDEX IF EXISTS idx_p_brand;")
        cur.execute("DROP INDEX IF EXISTS idx_l_partkey;")
        cur.execute("DROP INDEX IF EXISTS idx_l_returnflag;")
        conn.commit()
    
    conn.close()