import cherrypy
import json
from catalog import catalog

# Load persistent users from file at startup
try:
    with open("users.json") as f:
        catalog["users"] = json.load(f)
except FileNotFoundError:
    catalog["users"] = {}

class UVAlertCatalogue:

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def config(self):
        return catalog["config"]

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def users(self):
        return list(catalog["users"].keys())

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

        try:
            with open("users.json", "r") as f:
                users = json.load(f)
        except FileNotFoundError:
            users = {}

        if user in users:
            return {"status": "User already exists", "user": user}

        users[user] = {
            "chat_id": chat_id,
            "city": city,
            "thingspeak_key": "",  # Leave empty, manually assign later
            "thingspeak_channel": ""
        }

        with open("users.json", "w") as f:
            json.dump(users, f, indent=2)

        return {"status": "User registered", "user": user}

    @cherrypy.expose
    def dashboard(self):
        users = catalog["users"]
        rows = ""
        for user_id, info in users.items():
            link = info.get("thingspeak_channel", "#")
            rows += f"""
            <tr>
                <td>{user_id}</td>
                <td>{info['chat_id']}</td>
                <td>{info['city']}</td>
                <td><a href="{link}" target="_blank">📊 View Chart</a></td>
            </tr>
            """
        # Load HTML from file
        with open("templates/dashboard.html", "r", encoding="utf-8") as file:
            html = file.read()

        # Replace placeholder with actual table rows
        html = html.replace("{{ rows }}", rows)
        cherrypy.response.headers['Content-Type'] = 'text/html'
        return html.encode("utf-8")

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("/dashboard")

if __name__ == '__main__':
    conf = {
        "/": {
            "tools.sessions.on": True,
            "tools.response_headers.on": True,
            "tools.response_headers.headers": [('Content-Type', 'application/json')]
        }
    }

    cherrypy.config.update({
        "server.socket_host": "127.0.0.1",
        "server.socket_port": 8081
    })

    cherrypy.quickstart(UVAlertCatalogue(), "/", conf)
