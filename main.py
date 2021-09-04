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
app = FastAPI(title="RC3R App")

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
    agent_dicts_list = []
    unique_agents_list = []
    for guid_url in guid_list:
        guid_html_text = parse_page(guid_url)
        agents_list.append(parse_guide_page(guid_html_text))
    for agent_url in agents_list.copy():
        new_url = agent_url.split("%")
        if new_url[0] in unique_agents_list:
            agents_list.pop(agents_list.index(agent_url))
        else:
            unique_agents_list.append(new_url[0])
    for agent_url in agents_list:
        agent_html_text = parse_page(agent_url)
        agent_dicts_list.append(parse_agent_page(agent_html_text))
    return {"status": status, "agent_list": agent_dicts_list}


def parse_guide_page(html):
    domain = "http://zakupki.rosatom.ru/"
    reg = r"<td width=\"210\" class=\"ms-formlabel\">Наименование организации</td>[\n\s]*<td class=\"ms-formbody\">[\n\s]*<a href=\"(.*)\">"
    return domain + re.findall(reg, html)[0]


def parse_agent_page(html):
    # Контактные лица
    fields = {
        "Официальное наименование": "full_name",
        "Короткое наименование": "alias",
        "Фамилия руководителя": "surname",
        "Имя руководителя": "name",
        "Отчество руководителя": "middle_name",
        "Должность руководителя": "position",
        "ИНН": "INN",
        "КПП": "KPP",
        "ОКПО": "OKPO",
        "Почтовый адрес": "mail_adress",
        "Юридический адрес": "doc_adress",
        "Фактический адрес": "real_adress",
        "Телефон": "phone",
        "Адрес электронной почты": "email",
        "Домашняя страница": "web_page",
        "Расчетный счет": "payment_acc",
        "Корреспондентский счет": "corresp_acc",
        "БИК": "BIK",
        "Название банка": "bank_name",
        "Почтовый адрес банка": "bank_adress",
    }

    data = {}
    reg = r'<td width="210" class="ms-formlabel">{}<\/td>[\W]*?<td class="ms-formbody">(.*?)<\/td>'
    reg_contacts = r"<td width=\"210\" class=\"ms-formlabel\">Контактные лица<\/td>[\W]*?<td class=\"ms-formbody\">([\w\s\W]*?)</td>"

    for key in fields:
        try:
            data[fields[key]] = re.findall(reg.format(key), html)[0]
        except IndexError:
            data[fields[key]] = ""

    try:
        data["contacts"] = re.findall(reg_contacts, html)[0]
    except IndexError:
        data["contacts"] = ""

    return data


if __name__ == "__main__":
    uvicorn.run(app)
