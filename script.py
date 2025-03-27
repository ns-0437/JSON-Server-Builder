import json
import os
from collections import defaultdict, deque

# --- Helper functions ---
def load_config(json_file):
    """Load the JSON configuration from file."""
    with open(json_file, "r") as f:
        return json.load(f)

def build_graph(nodes):
    """
    Build a mapping from node id to its corresponding node data
    and a children mapping using the node 'target' field.
    """
    node_map = {}
    children = defaultdict(list)
    
    for node in nodes:
        node_map[node["id"]] = node
        target = node.get("target")
        if target:
            if isinstance(target, list):
                for tid in target:
                    children[node["id"]].append(tid)
            else:
                children[node["id"]].append(target)
    return node_map, children

def traverse_graph(node_map, children):
    """
    Traverse the graph from entry nodes (source == None or type 'entry') and collect route info.
    Propagate middleware flags along each path and override them if a route explicitly sets them.
    """
    routes = {}
    global_flags = {"cors": False, "logging": False}

    # Find entry nodes (source is None or properties type 'entry')
    entry_nodes = [node for node in node_map.values() if node.get("source") is None or (node.get("properties", {}).get("type") == "entry")]

    # We'll use a deque for BFS; each entry is (node_id, middleware_flags)
    # middleware_flags: dictionary with keys: auth, admin.
    queue = deque()
    for node in entry_nodes:
        queue.append((node["id"], {"auth": False, "admin": False}))

    while queue:
        cur_id, flags = queue.popleft()
        node = node_map[cur_id]
        props = node.get("properties", {})

        # Update global flags if this node specifies CORS or logging
        if "allowed_origins" in props:
            global_flags["cors"] = True
        if props.get("log_requests"):
            global_flags["logging"] = True

        # If the node explicitly defines auth or admin requirements, override the flags.
        # This applies even if the parent's flag was set to True.
        if "auth_required" in props:
            flags["auth"] = props["auth_required"]
        if "admin_required" in props:
            flags["admin"] = props["admin_required"]

        # If this node defines a route (has an 'endpoint' and 'method')
        if "endpoint" in props and "method" in props:
            endpoint = props["endpoint"]
            method = props["method"].lower()  # e.g., 'get' or 'post'
            name = node.get("name", "Unnamed Route")
            # For authentication endpoints (e.g., login, signup, signout) we force public access.
            if endpoint in ["/login", "/signup", "/signout"]:
                applied_flags = {"auth": False, "admin": False}
            else:
                # Use explicit property values if defined, otherwise inherit.
                applied_flags = {
                    "auth": props.get("auth_required", flags["auth"]),
                    "admin": props.get("admin_required", flags["admin"])
                }
            # Merge if the same endpoint is reached from multiple paths.
            if endpoint in routes:
                routes[endpoint]["auth"] = routes[endpoint]["auth"] or applied_flags["auth"]
                routes[endpoint]["admin"] = routes[endpoint]["admin"] or applied_flags["admin"]
            else:
                routes[endpoint] = {"method": method, "name": name, "auth": applied_flags["auth"], "admin": applied_flags["admin"]}
        
        # Enqueue children nodes
        for child_id in children.get(cur_id, []):
            # Copy flags so each branch gets its own
            queue.append((child_id, flags.copy()))
    
    return routes, global_flags

def generate_server_js(routes, global_flags, output_file="server.js"):
    """
    Generate a Node.js/Express server file based on collected route data and global middleware flags.
    """
    lines = []
    lines.append('// Auto-generated server implementation')
    lines.append('const express = require("express");')
    if global_flags["cors"]:
        lines.append('const cors = require("cors");')
    lines.append('const app = express();')
    lines.append('')
    
    # Global middleware
    if global_flags["cors"]:
        lines.append('app.use(cors({ origin: "*" }));')
    lines.append('app.use(express.json());')
    lines.append('')

    # Define auth middleware if needed
    any_auth = any(route["auth"] for route in routes.values())
    if any_auth:
        lines.append('const authMiddleware = (req, res, next) => {')
        lines.append('  if (!req.headers.authorization) {')
        lines.append('    return res.status(401).json({ message: "Unauthorized" });')
        lines.append('  }')
        lines.append('  next();')
        lines.append('};')
        lines.append('')
    
    # Define admin middleware if needed
    any_admin = any(route["admin"] for route in routes.values())
    if any_admin:
        lines.append('const adminMiddleware = (req, res, next) => {')
        lines.append('  if (req.headers.authorization !== "admin") {')
        lines.append('    return res.status(403).json({ message: "Forbidden" });')
        lines.append('  }')
        lines.append('  next();')
        lines.append('};')
        lines.append('')
    
    # Generate route handlers
    for endpoint, info in routes.items():
        method = info["method"]
        name = info["name"]
        middlewares = []
        if info["auth"]:
            middlewares.append("authMiddleware")
        if info["admin"]:
            middlewares.append("adminMiddleware")
        mws_str = ""
        if middlewares:
            mws_str = ", ".join(middlewares) + ", "
        # Determine a simple response message
        if endpoint == "/login":
            message = "Login successful"
        elif endpoint == "/signup":
            message = "Signup successful"
        elif endpoint == "/signout":
            message = "Signout successful"
        elif endpoint == "/user":
            message = "User data"
        elif endpoint == "/admin":
            message = "Admin data"
        elif endpoint == "/home":
            message = "Welcome to Home Page"
        elif endpoint == "/about":
            message = "About us"
        elif endpoint == "/news":
            message = "Latest news"
        elif endpoint == "/blogs":
            message = "Blogs list"
        else:
            message = f"Response from {name}"
        lines.append(f'app.{method}("{endpoint}", {mws_str}(req, res) => res.json({{ message: "{message}" }}));')
    lines.append('')
    lines.append('app.listen(3000, () => console.log("Server running on port 3000"));')
    
    with open(output_file, "w") as f:
        f.write("\n".join(lines))
    print(f"Generated {output_file} successfully.")

def main():
    config_file = "./config.json"
    if not os.path.exists(config_file):
        print(f"Error: {config_file} does not exist.")
        return
    
    config = load_config(config_file)
    nodes = config.get("nodes", [])
    if not nodes:
        print("No nodes found in the configuration.")
        return
    
    node_map, children = build_graph(nodes)
    routes, global_flags = traverse_graph(node_map, children)
    generate_server_js(routes, global_flags,output_file="./server.js")

if __name__ == "__main__":
    main()
