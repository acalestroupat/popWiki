import requests
import json
import wikipedia
from urllib.request import urlopen
from django.http import Http404
from nltk.tokenize import RegexpTokenizer
#from stopwords import get_stopwords
from nltk.corpus import stopwords

def wikiLink(keyword, lang):
    
    lst_res = []
    page_url = ''
    page_sum = ''
    page_links = ''
    page_title = ''
    page_categories = ''
    keywordSearch = str(keyword)
    langSearch = str(lang)
    
    wikipedia.set_lang(langSearch)
    wiki_search = wikipedia.search(keywordSearch)
    try:
        page = wikipedia.page(keywordSearch)
        page_url = page.url
        page_title = page.title
        page_categories = ""
        #page_categories = page.categories
        if page_url != '':
            page_sum = page.summary
    except wikipedia.exceptions.DisambiguationError as e:
        page_url = e.options
    except wikipedia.exceptions.PageError as a:
        page_url = ""
        page_links = ""
        page_sum = ""
        page_title = ""
        page_categories = ""
    except wikipedia.exceptions.WikipediaException:
        page_url = ""
        page_links = ""
        page_sum = ""
        page_title = ""
        page_categories = ""
    
    
    
    lst_res.append(page_url)
    lst_res.append(page_sum)
    lst_res.append(page_links)
    lst_res.append(page_title)
    lst_res.append(page_categories)
    
    return lst_res

def getStopWord(lang):
    
    if lang == 'fr':
        fr_stop = set(stopwords.words('french'))
        fr_stop = set("une comme la les un a en de du le est dans et au que d c pour des très Le s l L à Les il Il Ce ce qui Qui quoi Quoi As as Je je Tu il Il nous Nous vous Vous Ils ils de De Le le La la Je je".split())
        
    else:
        fr_stop = set(stopwords.words('english'))
        fr_stop = set("The the is Is are Are do Do and And in In Why What what why Which which with With To to A a On on Of of s d t When when Even even Some some Can can That that January February March April May June July August September October November December Monday Tuesday Wednesday Thirsday Friday Saturday Sunday our my me mine could be for by he He We we did As as your you Your You In in How how".split())
    
    return fr_stop