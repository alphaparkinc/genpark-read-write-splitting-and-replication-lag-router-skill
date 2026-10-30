"""Example usage for Read-Write Splitting & Replication Lag Router."""
from client import ReadWriteSplittingLagRouter

if __name__ == "__main__":
    replicas = [
        {"node_id": "replica-east-1", "lag_ms": 25.0, "is_healthy": True},
        {"node_id": "replica-west-1", "lag_ms": 150.0, "is_healthy": True}
    ]
    route = ReadWriteSplittingLagRouter.route_query("SELECT id, name FROM users WHERE id=42", replicas)
    print("Read Route:", route)

    write_route = ReadWriteSplittingLagRouter.route_query("UPDATE users SET status='ACTIVE' WHERE id=42", replicas)
    print("Write Route:", write_route)
