"""MCP server for Read-Write Splitting & Replication Lag Router."""
import sys
import json
from client import ReadWriteSplittingLagRouter

def handle_request(req):
    method = req.get("method")
    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "route_query",
                    "description": "Route SQL query to master or healthy replica based on AST type and replication lag",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "sql_statement": {"type": "string"},
                            "replicas": {"type": "array"},
                            "max_allowed_lag_ms": {"type": "number", "default": 200.0},
                            "force_master": {"type": "boolean", "default": False}
                        },
                        "required": ["sql_statement", "replicas"]
                    }
                }
            ]
        }
    elif method == "tools/call":
        params = req.get("params", {})
        name = params.get("name")
        args = params.get("arguments", {})
        if name == "route_query":
            out = ReadWriteSplittingLagRouter.route_query(
                args.get("sql_statement", ""),
                args.get("replicas", []),
                float(args.get("max_allowed_lag_ms", 200.0)),
                bool(args.get("force_master", False))
            )
            return {"content": [{"type": "text", "text": json.dumps(out, indent=2)}]}
    return {"error": "Unsupported method or tool"}

if __name__ == "__main__":
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            res = handle_request(req)
            print(json.dumps({"id": req.get("id"), "result": res}))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()
