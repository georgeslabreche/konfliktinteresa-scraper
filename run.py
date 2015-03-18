# -*- coding: utf-8 -*-
from pymongo import MongoClient
from BeautifulSoup import BeautifulSoup

import requests

import mechanize

# Connect to defualt local instance of MongoClient
client = MongoClient()

# Get database and collection
db = client.konfliktinteresa
col = db.scraped

def scrape():

    col.remove({})

    # Categories of stuff we want to scrape.
    # [id, name, to scrape or not to scrape]
    vrsta_funkcionera = [
        [13, "Svi funkcioneri", False],
        [12, "Lica koja nijesu na spisku j. funkcionera", False],
        [11, "Opštinski funkcioneri", False],
        [10, "Sudije za prekršaje", False],
        [9, "Vladini funkcioneri", False],
        [7, "Drugi javni funkcioneri Skupštine Crne Gore", False],
        [6, "Državni tužioci", False],
        [5, "Sudije", False],
        [4, "Ustavni sud", False],
        [3, "Vlada", True],
        [2, "Poslanici Crne Gore", False],
        [1, "Predsjednik Crne Gore", False]
    ]

    for funkcioner in vrsta_funkcionera:
        fid = funkcioner[0]

        url = "http://www.konfliktinteresa.me/new/evid_funkc/funkcioneri/EvidencijaFun.php?txtNaziv=&VR_FUN=%i" % fid

        '''
        page = requests.get('https://api.github.com/user', auth=('user', 'pass'))

        if page.status_code == 200:
            tree = html.fromstring(page.text)
            results = tree.xpath("//a[@href=starts-with(name(), 'EvidFunPrijave.php?')]/text()")

            print results

        else:
            print "%i - Surrogate input contrary to established facts." % (page.status_code) # Logan's Run reference.
        '''

        # First level scraping browser.
        br1 = mechanize.Browser()
        br1.set_handle_robots(False)   # ignore robots
        br1.set_handle_refresh(False)  # can sometimes hang without this
        br1.addheaders = [('User-agent', 'Firefox')]

        # Second level scraping browser.
        br2 = mechanize.Browser()
        br2.set_handle_robots(False)   # ignore robots
        br2.set_handle_refresh(False)  # can sometimes hang without this
        br2.addheaders = [('User-agent', 'Firefox')]

        # Third level scraping browser.
        br3 = mechanize.Browser()
        br3.set_handle_robots(False)   # ignore robots
        br3.set_handle_refresh(False)  # can sometimes hang without this
        br3.addheaders = [('User-agent', 'Firefox')]

        br1.open(url)
        for link in br1.links():
            if link.url.startswith('EvidFunPrijave.php?ID='):

                name_split = link.text.split(' ')
                official = {}
                official['full_name'] = link.text
                official['_id'] = link.url\
                    .replace('EvidFunPrijave.php?ID=', '')\
                    .replace(',,','')

                if len(name_split) == 3:
                    official['designation'] = name_split[0]
                    official['first_name'] = name_split[1]
                    official['last_name'] = name_split[2]
                else:
                    official['first_name'] = name_split[0]
                    official['last_name'] = name_split[1]


                url2 = 'http://www.konfliktinteresa.me/new/evid_funkc/funkcioneri/EvidFunPrijave.php?ID=' + official['_id']
                resp2 = br2.open(url2)

                html_str2 = resp2.read()
                table_soup2 = BeautifulSoup(html_str2)

                result_table2 = table_soup2.find('table', attrs={"class": "t2 table-striped2"})

                table_content_soup2 = BeautifulSoup(str(result_table2))
                anchors2 = table_content_soup2.findAll('a', href=lambda x: x and x.startswith('EvidFunPrijavePrikaz.php?ID='))

                for anchor2 in anchors2:
                    url3 = 'http://www.konfliktinteresa.me/new/evid_funkc/funkcioneri/%s' % anchor2['href']
                    resp3 = br3.open(url3)

                    html_str3 = resp3.read()
                    table_soup3 = BeautifulSoup(html_str3)

                    id_table = table_soup3.find("table", attrs={"width":"688", "border":"0", "cellpadding":"2", "cellspacing":"0", "class":"table"})
                    data_table = table_soup3.find("table", attrs={"valign":"top"})

                   //d_table_content = BeautifulSoup(str(id_table))

scrape()
