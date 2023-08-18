from fastapi import FastAPI

from lib.external_api import ExternalAPI

app = FastAPI()

app.external_api = ExternalAPI()
app.kube_client = None  # TODO


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/sync")
def post_sync(event: dict) -> dict:
    loadbalancer = event.get("parent", {})

    response = {"desired_status": True, "actual_status": loadbalancer.spec.ready}

    # Remote LB already exists, skipping
    if loadbalancer.spec.ready:
        return response

    try:
        lb_address = app.external_api.create_lb(
            name=loadbalancer.metadata.name,
            listen_port=loadbalancer.spec.port.port,
            target_svc_selector=f"{loadbalancer.spec.service.name}.{loadbalancer.spec.service.namespace}.svc",
            target_svc_port=loadbalancer.spec.service.port,
        )
    except Exception as e:
        return {"message": "Could not create LoadBalancer via remote API", "error": e}

    loadbalancer.spec.ready = bool(lb_address)
    loadbalancer.spec.ready = lb_address

    try:
        app.kube_client.update_loadbalancer(new_spec=loadbalancer)
    except Exception as e:
        return {"message": "Could not update in-cluster LoadBalancer object", "error": e}

    return response


@app.post("/finalize")
def post_finalize(event: dict) -> dict:
    loadbalancer = event.get("parent", {})

    response = {"desired_status": False, "actual_status": loadbalancer.spec.ready}

    # No remote LB associated, nothing to cleanup
    if not loadbalancer.spec.ready:
        return response

    try:
        app.external_api.delete_lb(
            name=loadbalancer.metadata.name,
        )
    except Exception as e:
        return {"message": "Could not delete LoadBalancer via remote API", "error": e}

    return response
