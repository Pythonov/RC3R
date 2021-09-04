import re


def parse_guide_page(html):
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
