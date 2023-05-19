#!/usr/bin/env python3
"""
Copyright (C) 2023 alchimista alchimistawp@gmail.com
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import pywikibot
from pywikibot import pagegenerators
import re
from datetime import datetime
from pywikibot import Timestamp
import pageviewapi
import pageviewapi.period
import requests
import json

site = pywikibot.Site('pt', 'wikipedia')
request_page = pywikibot.Page(site, "Usuária:Aleth Bot/Articles report").get()


links = []
lr = re.compile(
    '\:Aleth Bot\/\_Article reports\|\s*(?P<pagina>.*)\}\}', re.I | re.M | re.U)
_links = lr.findall(request_page)
print (_links)


def generate_list():
    af = pywikibot.Page(site, "Predefinição:Música Portuguesa").getReferences(namespaces=1)

    articles = dict()
    revid_last = dict()

    for i in af:
        tit = i.title(with_ns=False)
        artigo = pywikibot.Page(site, tit)

        first = artigo.oldest_revision
        last = artigo.revisions()
        revid = list(last)[0]["revid"]
        print(tit, revid)

        articles[tit] = {'revid_first': first['revid'], 'user': first['user'], 'timestamp': first['timestamp'],
                         'anon': first['anon'], 'revid_last': revid}
        revid_last[tit] = revid

    return (articles, revid_last)
def getOres(lista, articles):
    def chunks(lst, n):
        """ From https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks """
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    lst = list(lista.values())
    print("--", lista)

    nlist = chunks(lst, 10)
    for chunk in list(nlist):
        print("chunck: ", chunk, )

        ids = ""
        ids_list = list()
        for id in chunk:
            if ids == "":
                ids = str(id)
            else:
                ids = ids + "|" + str(id)
                ids_list.append(id)
        print(ids)

        base_url = "https://ores.wikimedia.org/v3/scores/ptwiki?models=articlequality&revids={}".format(ids)
        print(base_url)
        s = json.loads(requests.get(base_url).text)
        print("ids!", ids_list)
        print(s['ptwiki']['scores'])
        for line in s['ptwiki']['scores']:
            print("**", line, s['ptwiki']['scores'][line]['articlequality']['score']['prediction'])
            for i in lista:
                print(i, lista[i])
                print(i, articles[i])
                print(line, lista[i], i, articles[i])
                if int(line) == int(lista[i]):
                    print("\n\nooooujçhç li +oi\n\n")
                    articles[i]['ores'] = s['ptwiki']['scores'][line]['articlequality']['score']['prediction']

    return articles


def main():

    for i in _links:
        print(i)
        ttl = "Usuário(a):Aleth Bot/{}".format(i)
        report_page = pywikibot.Page(site, ttl)


        articles, revid_last = generate_list()
        lista = getOres(revid_last, articles)

        wikitable = """
            {| class="wikitable sortable"
            |-
            ! Data !! Nome !! Criada por !! Pageviews (ultimos 30 dias) || Avaliação ORES"""

        revid_last = list()

        for i in lista:
            line = lista[i]
            print(i, line['revid_last'])

            try:
                s = pageviewapi.period.sum_last('pt.wikipedia', i, last=30,
                                                access='all-access', agent='all-agents')
            except:
                s = "sem dados"
            print(line['timestamp'], i, line['user'], s)
            if line['anon']:
                usr = "{{ip|%s}}" % line['user']
            else:
                usr = "[[User:%s]]" % line['user']
            time = line['timestamp'].strftime("%d-%m-%Y")
            nline = """\n|-\n| %s || [[%s]] || %s || %s || %s""" % (time, i, usr, s, line['ores'])
            print(nline)
            wikitable = wikitable + nline
            print(line['timestamp'].strftime("%d-%m-%Y"))

        wikitable = wikitable + """\n|-\n|}"""
        print(wikitable)
        report_page.text = wikitable
        report_page.save(summary="[[WP:BOT]] - actualização da informação")

main()
