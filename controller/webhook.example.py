from http.server import BaseHTTPRequestHandler, HTTPServer
import json


class Controller(BaseHTTPRequestHandler):
    def sync(self, parent):
        # Compute status based on observed state.
        desired_status = {"namespaces": len(children["Namespace.v1"])}

        # Generate the desired child object(s).

        license = parent.get("spec", {}).get("license", "WTFPL")

        desired_namespaces = [
            {
                "apiVersion": "v1",
                "kind": "Namespace",
                "metadata": {
                    "name": "-".join(("proj", parent["metadata"]["name"])),
                    "annotations": {
                        "description": parent["spec"]["description"],
                        "license": parent["spec"]["license"],
                    },
                },
            }
        ]

        return {"status": desired_status, "children": desired_namespaces}

    def do_POST(self):
        event = json.loads(self.rfile.read(int(self.headers.get("content-length"))))

        # Create or update LB on "sync" request
        if not event["finalizing"]:
            response = self.sync(event["parent"])
        # Delete LB on "finalize" request
        else:
            response = self.finalize(event["parent"])

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())


HTTPServer(("", 80), Controller).serve_forever()
