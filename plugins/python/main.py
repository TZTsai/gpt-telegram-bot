import os
import json
import argparse

import quart
import quart_cors
from quart import request

os.chdir(os.path.dirname(__file__))

from console import Console
console = Console()

# Note: Setting CORS to allow chat.openapi.com is only required when running a localhost plugin
app = quart_cors.cors(quart.Quart(__name__), 
                      allow_origin=["https://chat.openai.com", "localhost"])


@app.post("/")
async def run():
    code = await request.get_data(as_text=True)
    response = console.run(code)
    return quart.Response(response=json.dumps(response), status=200)


@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open(".well-known/ai-plugin.json") as f:
        text = f.read()
        # This is a trick we do to populate the PLUGIN_HOSTNAME constant in the manifest
        text = text.replace("PLUGIN_HOSTNAME", f"https://{host}")
        return quart.Response(text, mimetype="text/json")


@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        # This is a trick we do to populate the PLUGIN_HOSTNAME constant in the OpenAPI spec
        text = text.replace("PLUGIN_HOSTNAME", f"https://{host}")
        return quart.Response(text, mimetype="text/yaml")


parser = argparse.ArgumentParser()
parser.add_argument("--host", default="localhost")
parser.add_argument("--port", type=int)
opts = parser.parse_args()


if __name__ == "__main__":
    app.run(debug=True, host=opts.host, port=opts.port)
