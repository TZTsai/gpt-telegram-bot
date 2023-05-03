import os
import sys
import bs4
import json
import requests
import argparse

import quart
import quart_cors
from quart import request

os.chdir(os.path.dirname(__file__))

# Note: Setting CORS to allow chat.openapi.com is only required when running a localhost plugin
app = quart_cors.cors(quart.Quart(__name__), 
                      allow_origin=["https://chat.openai.com", "localhost"])


@app.post("/")
async def get():
    url = await request.get_data(as_text=True)
    response = requests.get(url).text
    return quart.Response(response=response, status=200)


def compress_html(html: str, maxlen: int=4096):
    soup = bs4.BeautifulSoup(html, "html.parser")
    for el in soup.find_all('a'):
        el.replace_with(f"[{el.text.strip()}]({el['href']})")
    for el in soup.find_all("script,meta,style,button,img,canvas,data,details,embed,footer,form,input,video,source,s,del,audio,iframe".split(',')):
        pass  # TODO
    return soup.text[:maxlen]


@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("ai-plugin.json") as f:
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
