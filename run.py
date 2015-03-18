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

        url1 = "http://www.konfliktinteresa.me/new/evid_funkc/funkcioneri/EvidencijaFun.php?txtNaziv=&VR_FUN=%i" % fid

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

        br1.open(url1)
        for link in br1.links():
            if link.url.startswith('EvidFunPrijave.php?ID='):

                official_id = link.url\
                    .replace('EvidFunPrijave.php?ID=', '')\
                    .replace(',,','')

                url2 = 'http://www.konfliktinteresa.me/new/evid_funkc/funkcioneri/EvidFunPrijave.php?ID=%s' % official_id
                resp2 = br2.open(url2)

                html_str2 = resp2.read()
                table_soup2 = BeautifulSoup(html_str2)

                result_table2 = table_soup2.find('table', attrs={"class": "t2 table-striped2"})

                table_content_soup2 = result_table2
                anchors2 = table_content_soup2.findAll('a', href=lambda x: x and x.startswith('EvidFunPrijavePrikaz.php?ID='))

                for anchor2 in anchors2:
                    url3 = 'http://www.konfliktinteresa.me/new/evid_funkc/funkcioneri/%s' % anchor2['href']
                    resp3 = br3.open(url3)

                    html_str3 = resp3.read()
                    table_soup3 = BeautifulSoup(html_str3)

                    personal_info_table = table_soup3.find("table", attrs={"width":"688", "border":"0", "cellpadding":"2", "cellspacing":"0", "class":"table"})
                    pi_key_pairs = personal_info_table.findAll("font")

                    for pi_kp in pi_key_pairs:
                        print pi_kp.text

                    details_table = table_soup3.find("table", attrs={"width":"90%", "border":"0", "cellspacing":"0", "cellpadding":"1", "class":"t2 table-striped2"})
                    d_key_pairs = details_table.findAll("font")

                    for d_kp in d_key_pairs:
                        print d_kp.text


scrape()
