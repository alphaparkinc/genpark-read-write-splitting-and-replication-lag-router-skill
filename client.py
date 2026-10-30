"""Read-Write Splitting & Replication Lag Router.
100% Python Standard Library.
"""

class ReadWriteSplittingLagRouter:
    """Routes queries to replicas or master based on SQL AST token classification and replica lag thresholds."""

    WRITE_KEYWORDS = {"INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE", "REPLACE", "BEGIN", "COMMIT"}

    @classmethod
    def route_query(cls, sql_statement: str, replicas: list, max_allowed_lag_ms: float = 200.0,
                    force_master: bool = False) -> dict:
        normalized_sql = sql_statement.strip().upper()
        first_token = normalized_sql.split()[0] if normalized_sql.split() else "SELECT"

        is_write = (first_token in cls.WRITE_KEYWORDS) or force_master

        if is_write:
            return {
                "route_target": "MASTER",
                "target_node_id": "master-primary-01",
                "query_classification": "WRITE_OPERATION" if not force_master else "FORCED_MASTER_READ",
                "replication_lag_ms": 0.0,
                "reason": "Write queries and forced master queries must route to primary"
            }

        viable_replicas = []
        for rep in replicas:
            if rep.get("is_healthy", True) and rep.get("lag_ms", 0.0) <= max_allowed_lag_ms:
                viable_replicas.append(rep)

        if not viable_replicas:
            return {
                "route_target": "MASTER",
                "target_node_id": "master-primary-01",
                "query_classification": "READ_OPERATION_FALLBACK",
                "replication_lag_ms": 0.0,
                "reason": "All read replicas exceeded replication lag threshold or unhealthy; routed to master"
            }

        best_replica = min(viable_replicas, key=lambda x: x.get("lag_ms", 0.0))
        return {
            "route_target": "REPLICA",
            "target_node_id": best_replica.get("node_id"),
            "query_classification": "READ_OPERATION",
            "replication_lag_ms": best_replica.get("lag_ms", 0.0),
            "reason": f"Routed to lowest-lag healthy replica ({best_replica.get('node_id')})"
        }
