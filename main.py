import cherrypy
import json
from datetime import datetime

# TODO replace with actual users
user_data = {
    "user123": {"uv": 6.5, "last_reminder": "2024-06-01T12:00:00"},
    "user456": {"uv": 3.2, "last_reminder": "2024-06-01T09:00:00"},
}

class UVApi:
    @cherrypy.expose
    def index(self):
        return "🌞 UV Alert REST API is running."

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def users(self):
        return list(user_data.keys())

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def uv(self, user=None):
        if user in user_data:
            return {"user": user, "uv": user_data[user]["uv"]}
        return {"error": "User not found"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def reminders(self, user=None):
        if user in user_data:
            return {"user": user, "last_reminder": user_data[user]["last_reminder"]}
        return {"error": "User not found"}

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
        "server.socket_port": 8081
    })

    cherrypy.quickstart(UVApi(), "/", conf)
