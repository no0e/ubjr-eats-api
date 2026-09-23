import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from .AdministratorController import administrator_router
from .CustomerController import customer_router
from .DeliveryDriverController import deliverydriver_router
from .UserController import user_router


def run_app(reset_db=False):
    app = FastAPI(
        title="Ub’EJR Eats",
        description="This API allows you to be connected as a user to the ENSAI Junior Restaurant app.<br>"
        "- As a customer you can create a cart by choosing items from the menu. You can then order it.<br>"
        "- As a delivery driver you can see the pendant orders. You will be provided a map with the itinerary.<br>"
        "- As an administrator, you can manage user accounts and items in the menus.",
    )

    app.include_router(user_router)
    app.include_router(customer_router)
    app.include_router(deliverydriver_router)
    app.include_router(administrator_router)

    @app.get("/", include_in_schema=False)
    async def redirect_to_docs():
        """Redirect to the API documentation"""
        return RedirectResponse(url="/docs")

    uvicorn.run(app, port=8000, host="0.0.0.0", root_path="/proxy/8000")
