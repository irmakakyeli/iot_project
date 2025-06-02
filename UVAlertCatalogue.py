#123456Aa

import cherrypy
import json
from datetime import datetime
from catalog import catalog

class UVAlertCatalogue:
    @cherrypy.expose
    def index(self):
        return "📘 UV Alert Catalog is running."

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def users(self):
        return list(catalog["users"].keys())

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def services(self):
        return catalog["services"]

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def config(self):
        return catalog["config"]

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def topics(self, user=None):
        if user not in catalog["users"]:
            return {"error": "User not found"}
        return {
            "location_topic": f"UVAlert/{user}/location",
            "uv_topic": f"UVAlert/{user}/uv",
            "reminder_topic": f"UVAlert/{user}/reminder"
        }

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def register_user(self):
        input_data = cherrypy.request.json
        user = input_data.get("user")
        chat_id = input_data.get("chat_id")
        city = input_data.get("city", "Unknown")

        if not user or not chat_id:
            return {"error": "Missing user or chat_id"}

        catalog["users"][user] = {"chat_id": chat_id, "city": city}
        return {"status": "User registered", "user": user}


if __name__ == '__main__':
    conf = {
        "/": {
            "request.dispatch": cherrypy.dispatch.MethodDispatcher(),
            "tools.sessions.on": True,
            "tools.response_headers.on": True,
            "tools.response_headers.headers": [('Content-Type', 'application/json')]
        }
    }

    cherrypy.config.update({
        "server.socket_host": "127.0.0.1",
        "server.socket_port": 8080
    })

    cherrypy.quickstart(UVAlertCatalogue(), "/", conf)
