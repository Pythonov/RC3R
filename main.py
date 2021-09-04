from fastapi.middleware.cors import CORSMiddleware
from src.tools.rss_parser import rss_parser
from fastapi import FastAPI
import uvicorn
import re
from parse import parse_page
from bs4 import BeautifulSoup
from fastapi import Body
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


@app.post("/okpd2_looking", name="Поиск по ОКПД-2")
async def okpd2_looking(item: Item = Body(...)):
    OKPD_DOMAIN = "https://www.rusprofile.ru/codes/"
    data = item.data
    f = {"0": 3, "1": 1}
    numbers = str(f["0"]) + str(f["1"])
    url = OKPD_DOMAIN + numbers
    if f["0"] < 10:
        url = url + "0"*(5-len(numbers))
    else:
        url = url + "0"*(6-len(numbers))


@app.post("/look_for", name="Поиск")
async def look_for(num_of_items: int = 6, item: Item = Body(...)):
    ROSATOM_DOMAIN = "http://zakupki.rosatom.ru/"
    data = item.data
    status = "Ok"
    request = f"http://zakupki.rosatom.ru/Web.aspx?node=archiveorders&ot={data}&tso=1&tsl=0&sbflag=0&pricemon=0&ostate=F&pform=a&nocontract=0&orderresult=1"
    print("INFO: connecting to zakupki.rosatom.ru...")
    html_base = await parse_page(request)
    print("INFO: connected successfully")
    soup = BeautifulSoup(html_base, 'html.parser')
    table = soup.find('div', {'id': 'table-lots-list'})
    table = table.find_all('tr')
    valid_trs = []
    guid_list = []

    for tr in table[1:]:
        if "description" not in tr.attrs.get("class"):
            valid_trs.append(tr)

    for tr in valid_trs:
        a_tag = tr.find_all("a")[0]
        if not a_tag.string.startswith("Право заключения"):
            guid_list.append(ROSATOM_DOMAIN + a_tag.get("href"))
    agents_list = []
    agent_dicts_list = []
    unique_agents_list = []

    guid_list = guid_list[0:num_of_items]
    for i, guid_url in enumerate(guid_list):
        guid_html_text = await parse_page(guid_url)
        agent = await parse_guid_page(guid_html_text)
        if agent:
            agents_list.append(agent)
        print(f"INFO: Parsed {i+1} of {len(guid_list)}")

    for agent_url in agents_list.copy():
        new_url = agent_url.split("%")
        if new_url[0] in unique_agents_list:
            agents_list.pop(agents_list.index(agent_url))
        else:
            unique_agents_list.append(new_url[0])

    for agent_url in agents_list:
        agent_html_text = await parse_page(agent_url)
        agent_dicts_list.append(await parse_agent_page(agent_html_text))

    final_agent_list = []
    for i, inn_agent in enumerate(agent_dicts_list):
        if inn_agent.get("INN"):
            inn = inn_agent.get("INN")
            super_info_html = await parse_page(f"https://www.rusprofile.ru/search?query={inn}%27&type=ul")
            cool_dict = parse_cool_page(super_info_html)
            final_dict = {**inn_agent, **cool_dict}
            final_agent_list.append(final_dict)

        else:
            print("wtf where is your INN mf")
        print(f"INFO: parsed {i+1} of {len(agent_dicts_list)}")

    return {"status": status, "agent_list": final_agent_list}


async def parse_guid_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    domain = "http://zakupki.rosatom.ru"
    tables = soup.find_all("table")
    for tab in tables:
        td_str = tab.tr.td.string
        if td_str == "Наименование поставщика":
            url = domain + tab.tr.a.get("href")
            return url
    return None


async def parse_agent_page(html):
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


def parse_cool_page(html):
    soup = BeautifulSoup(html, 'html.parser')

    try:
        reliab_lvl = soup.find("a", {'data-goal': 'reliability_button_ul'}).string
    except AttributeError:
        reliab_lvl = ''

    try:
        status = soup.find("div", {'class': 'company-status'}).string
    except AttributeError:
        status = ''

    try:
        capital = soup.find("dt", {'class': 'company-info__title'},
                            text=re.compile('Уставный капитал')).parent.dd.span.string
    except AttributeError:
        capital = ''

    try:
        concurents_block = soup.find("a", text=re.compile('Конкуренты')).parent.parent
        concurents = concurents_block.find_all('a', {'class': 'link-arrow gtm_f_list'})
        concurents_list = []
        for concurent in concurents:
            concurents_list.append(concurent.span.string)
    except AttributeError:
        concurents_list = ''

    try:
        state_oreders_block = soup.find("a", text=re.compile("Госзакупки")).parent.parent.parent
        state_oreders = state_oreders_block.find_all('div', {'class': 'founder-item'})
        state_oreders_list = []
        for state_order in state_oreders:
            state_oreders_list.append('{0} ({1} {2})'.format(state_order.div.a.span.string, state_order.dl.dt.string,
                                                             state_order.dl.dd.string))
    except AttributeError:
        state_oreders_list = ''

    data = {'reliab_lvl': reliab_lvl,
            'status': status,
            'capital': capital,
            'concurents_list': concurents_list,
            'state_oreders_list': state_oreders_list
            }

    return data


'''
reliab_lvl : уровень надёжности
status : статус (действует, не действует)
capital : уставной капитал
concurents_list : список конкурентов
state_oreders_list : список госзаказов
'''

if __name__ == "__main__":
    uvicorn.run(app)
