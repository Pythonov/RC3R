from fastapi.middleware.cors import CORSMiddleware
from src.tools.rss_parser import rss_parser
from fastapi import FastAPI
import uvicorn
import re
from parse import parse_page
from tortoise import Tortoise
from fastapi import Body
from tortoise.contrib.fastapi import register_tortoise
from pydantic import BaseModel

# Initial config
app = FastAPI(title='RC3R App')

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Item(BaseModel):
    data: str


@app.post("/look_for", name="Поиск")
async def look_for(num_of_items=5, item: Item = Body(...)):

    data = item.data
    status = "Ok"
    guid_list = rss_parser(data)
    agents_list = []
    for guid_url in guid_list:
        guid_html_text = parse_page(guid_url)
        agents_list.append(parse_guide_page(guid_html_text))
    for agent_url in agents_list:
        agent_html_text = parse_page(agent_url)
    return {"status": status, "list": agent_html_text}


def parse_guide_page(html):
    domain = "http://zakupki.rosatom.ru/"
    reg = r"<td width=\"210\" class=\"ms-formlabel\">Наименование организации</td>[\n\s]*<td class=\"ms-formbody\">[\n\s]*<a href=\"(.*)\">"
    # print(domain + re.findall(reg, html)[0])
    return domain + re.findall(reg, html)[0]

if __name__ == '__main__':
    uvicorn.run(app)
