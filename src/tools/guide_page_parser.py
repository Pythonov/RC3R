import re


def parse_guide_page(html):
    domain = "http://zakupki.rosatom.ru/"
    reg = r"<td width=\"210\" class=\"ms-formlabel\">Наименование организации</td>[\n\s]*<td class=\"ms-formbody\">[\n\s]*<a href=\"(.*)\">"
    # print(domain + re.findall(reg, html)[0])
    return domain + re.findall(reg, html)[0]
