import re
html = open('pr_page.html', encoding='utf-8').read()
links = re.findall(r'href=[\"\'](/Press_Release/[^\"\']*?\.pdf)[\"\']', html)
for link in links:
    print(link)
