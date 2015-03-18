# -*- coding: utf-8 -*-
from pymongo import MongoClient
from BeautifulSoup import BeautifulSoup
from slugify import slugify

import mechanize

# Connect to defualt local instance of MongoClient
client = MongoClient()

# Get database and collection
db = client.konfliktinteresa

def scrape():

    db.scraped.remove({})

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

        # When we click on a search result, it leads us to this website.
        url1 = "http://www.konfliktinteresa.me/new/evid_funkc/funkcioneri/EvidencijaFun.php?txtNaziv=&VR_FUN=%i" % fid

        # The depth of the scraping is 3.
        # First level scraping.
        br1 = mechanize.Browser()
        br1.set_handle_robots(False)   # ignore robots
        br1.set_handle_refresh(False)  # can sometimes hang without this
        br1.addheaders = [('User-agent', 'Firefox')]

        # Second level scraping.
        br2 = mechanize.Browser()
        br2.set_handle_robots(False)   # ignore robots
        br2.set_handle_refresh(False)  # can sometimes hang without this
        br2.addheaders = [('User-agent', 'Firefox')]

        # Third level scraping.
        br3 = mechanize.Browser()
        br3.set_handle_robots(False)   # ignore robots
        br3.set_handle_refresh(False)  # can sometimes hang without this
        br3.addheaders = [('User-agent', 'Firefox')]

        # For this experiment, we will only scrape data from the search result's first page.
        # To scrape everything we would have to loop through all the search result pages.
        br1.open(url1)

        # Get all the links for each year that we have a report on the official
        for link in br1.links():
            if link.url.startswith('EvidFunPrijave.php?ID='):

                official_id = link.url\
                    .replace('EvidFunPrijave.php?ID=', '')\
                    .replace(',,','')

                # On to the next page.
                url2 = 'http://www.konfliktinteresa.me/new/evid_funkc/funkcioneri/EvidFunPrijave.php?ID=%s' % official_id
                resp2 = br2.open(url2)

                # Grabbing data we need to build the final url.
                html_str2 = resp2.read()
                table_soup2 = BeautifulSoup(html_str2)

                result_table2 = table_soup2.find('table', attrs={"class": "t2 table-striped2"})

                table_content_soup2 = result_table2
                anchors2 = table_content_soup2.findAll('a', href=lambda x: x and x.startswith('EvidFunPrijavePrikaz.php?ID='))

                for anchor2 in anchors2:

                    # The is the document we are building.
                    # It contains all the info of the current person for a given year.
                    doc = {}

                    # Fetch the final page! The one with all the data we want.
                    url3 = 'http://www.konfliktinteresa.me/new/evid_funkc/funkcioneri/%s' % anchor2['href']
                    resp3 = br3.open(url3)

                    # use BeautifulSoup to fetch data
                    html_str3 = resp3.read()
                    table_soup3 = BeautifulSoup(html_str3)

                    # Get the current official's persona/summary data, we will refer to these properties and their values to "key/value" pairs.
                    personal_info_table = table_soup3.find("table", attrs={"width":"688", "border":"0", "cellpadding":"2", "cellspacing":"0", "class":"table"})
                    pi_key_pairs = personal_info_table.findAll("font")

                    pi_prop_key = None
                    for idx, pi_k_or_p in enumerate(pi_key_pairs):
                        if idx % 2 == 0:
                            pi_prop_key = slugify(pi_k_or_p.text)
                        else:
                            if pi_prop_key != None and pi_prop_key != '':
                                doc[pi_prop_key] = pi_k_or_p.text

                                # Reset the json object key, for the next iteration.
                                pi_prop_key = None

                    # We do the same thing for the second table, the one with all the details
                    details_table = table_soup3.find("table", attrs={"width":"90%", "border":"0", "cellspacing":"0", "cellpadding":"1", "class":"t2 table-striped2"})

                    rows = details_table.findAll("tr", attrs={"valign":"top"})

                    for row in rows:

                        d_key_pairs = row.findAll('font')

                        prop = d_key_pairs[0].text
                        slug = slugify(prop)
                        value = d_key_pairs[1].text

                        doc[slug] = {
                            'prop': prop,
                            'value': value
                        }

                    # Finally, we insert the scraped data into our database.
                    db.scraped.insert(doc)


scrape()
