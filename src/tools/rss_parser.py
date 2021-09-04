import re


def rss_parser(search):

    with open('src/tools/rss_data.txt', 'r', encoding="utf-8") as f:
        data = f.read()
    split_by_item = r"(\s*<item>[\w\W]*?<title>[\w\W]*?</title>[\w\W]*?<guid>[\w\W]*?</guid>[\w\W]*?</item>)"
    get_guide = r"\s*<item>[\w\W]*?<title>[\w\W]*?</title>[\w\W]*?<guid>([\w\W]*?)</guid>[\w\W]*?</item>"
    lst = []
    
    for item in re.findall(split_by_item, data):
        if re.search(search, item) is not None:
            lst.append(re.findall(get_guide, item)[0])
    
    #print(lst)
    return lst


# rss_parser('лифт')
#\s*<item>[\w\W]*?<title>[\w\W]*?Паутина[\w\W]*?</title>[\w\W]*?<guid>([\w\W]*?)</guid>[\w\W]*?</item>