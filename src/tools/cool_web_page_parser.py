from bs4 import BeautifulSoup
import re


def parse_cool_page(html):
    soup = BeautifulSoup(html, 'lxml')
    
    try:
        reliab_lvl = soup.find("a", {'data-goal': 'reliability_button_ul'}).string
    except AttributeError:
        reliab_lvl = ''

    try:
        status = soup.find("div", {'class': 'company-status'}).string
    except AttributeError:
        status = ''
    
    try:
        capital = soup.find("dt", {'class': 'company-info__title'}, text=re.compile('Уставный капитал')).parent.dd.span.string
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
            state_oreders_list.append('{0} ({1} {2})'. format(state_order.div.a.span.string, state_order.dl.dt.string, state_order.dl.dd.string))
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
