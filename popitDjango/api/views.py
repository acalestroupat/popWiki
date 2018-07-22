from django.shortcuts import render
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.core import serializers
from django.conf import settings
import json
import requests
import json
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
from nltk.tokenize import RegexpTokenizer
#from stopwords import get_stopwords
from nltk.corpus import stopwords
import wikipedia
from api.functions import wikiLink, getStopWord


@api_view(["POST"])
def firstWikiLink(article_json):
    try:
        embedly_url=json.loads(article_json.body)
        #r = str(embedly_url)
        
        page_url = ''
        page_links = ''
        page_sum = ''
        page_title = ''
        str_final_keyword = ''
        page_categories = ''
        check = True
        wikiKeywords = ''
        
        contenu = embedly_url['content']
        description = embedly_url['description']
        title = embedly_url['title']
        org_url = embedly_url['original_url']
        
        if contenu is None:
            check = False
            
        if check == True:

            print('Le titre : ' + title)
            print('La description : ' + description)

            lst_keyword = []
            tokenizer = RegexpTokenizer(r'\w+')

            #Titre Majuscule
            tokens = tokenizer.tokenize(title)
            lang = 'English'

            if lang == 'French':
                fr_stop = getStopWord(lang)
                language = 'fr'
            else:
                fr_stop = getStopWord(lang)
                language = 'en'

            stopped_tokens_title = [i for i in tokens if not i in fr_stop]

            i = len(stopped_tokens_title)

            counter = 0

            #Title Majuscule
            while counter != (i -1):
                for k in stopped_tokens_title[counter]:
                    if k.lower() != k:
                        for g in stopped_tokens_title[counter + 1]:
                            if g.lower() != g:
                                lst_keyword.append(stopped_tokens_title[counter] + ' ' + stopped_tokens_title[counter + 1] + ';')
                counter = counter + 1

            counter = 0

            #Description Majuscule
            tokens = tokenizer.tokenize(description)
            #fr_stop = set(stopwords.words('french'))

            stopped_tokens = [i for i in tokens if not i in fr_stop]

            i = len(stopped_tokens)

            while counter != (i -1):
                for k in stopped_tokens[counter]:
                    if k.lower() != k:
                        for g in stopped_tokens[counter + 1]:
                            if g.lower() != g:
                                lst_keyword.append(stopped_tokens[counter] + ' ' + stopped_tokens[counter + 1] + ';')
                counter = counter + 1

            #repetition
            i = len(stopped_tokens)
            j = len(stopped_tokens_title)
            counter = 0
            counter_bis = 0

            while counter != (i - 1):
                while counter_bis != (j - 1):
                    if stopped_tokens[counter] == stopped_tokens_title[counter_bis]:
                        lst_keyword.append(stopped_tokens_title[counter_bis] + ';')
                    counter_bis = counter_bis + 1
                counter_bis = 0
                counter = counter + 1

            keyword = ''

            #Remove iterration
            i = len(lst_keyword)
            counter = 0

            if i > 0:
                while counter < (i - 1):
                    remove = 0
                    x = lst_keyword[counter]
                    for o in lst_keyword:
                        if o == x:
                            remove += 1
                            if remove > 1:
                                del lst_keyword[counter]
                                i = len(lst_keyword)
                    counter += 1

            for sentence in lst_keyword:
                keyword = keyword + sentence

            #Beautiful soup : compare into the content
            cleanKeyword = ''
            cleanKeyword = str.replace(keyword, ";", "")

            counter = 0
            count = 0

            if contenu is None:
                contenu = ''

            html = contenu.lower()

            soup = BeautifulSoup(html, 'html.parser')

            word_split = keyword.split(';')
            final_keyword = []

            u = len(word_split)

            counter = 0
            most_repeat = 0
            lst_wordMostRepeat = []
            lst_nbMostRepeat = []
            n = 0
            first_research = ''

            while n != (u - 1):
                count = 0
                counter_final_split = 0
                searched_word_bis = word_split[n]

                word_split_final = searched_word_bis.split(' ')
                j = len(word_split_final)

                while counter_final_split != j:

                    searched_word = word_split_final[counter_final_split]

                    searched_word = searched_word.lower()

                    results = soup.find_all(string=re.compile(searched_word), recursive=True)
                    results = str(results)

                    tokens = tokenizer.tokenize(results)

                    stopped_tokens = [i for i in tokens if not i in fr_stop]

                    for content in stopped_tokens:

                        content = content.lower()
                        words = content.split()

                        for index, word in enumerate(words):
                            # If the content contains the search word twice or more this will fire for each occurence
                            searched_word = searched_word.lower()
                            word = word.lower()

                            if word == searched_word:
                                count = count + 1
                    print ('The keyword : "{0}", has been repeated: {1}'.format(searched_word, count))
                    if count > most_repeat:
                        if len(lst_wordMostRepeat) > 0:
                            del lst_wordMostRepeat[0]
                        if j > 1:

                            print(j)
                            print(str(word_split_final))
                            if counter_final_split == 0:
                                searched_word = searched_word + ' ' + word_split_final[1]
                            if counter_final_split == 1:
                                searched_word = word_split_final[0] + ' ' + searched_word
                            print('NOUVELLE REGLE: ' + searched_word)
                            first_research = searched_word
                        lst_wordMostRepeat.append(searched_word)
                        most_repeat = count


                    counter_final_split = counter_final_split + 1
                    if count > 0:
                        final_keyword.append(searched_word)
                n+=1
                counter = counter + 1

            i = len(final_keyword)

            f = 0

            #remove iteration
            if i > 0:
                counter = 0
                while counter < (i - 1):
                    remove = 0
                    x = final_keyword[counter]
                    for o in final_keyword:
                        if o == x:
                            remove += 1
                            if remove > 1:
                                del final_keyword[counter]
                                i = len(final_keyword)
                    counter += 1

            if most_repeat == 0:
                str_final_keyword = str(keyword)
            else:
                str_final_keyword = str(final_keyword)


            page_url = ''
            page_links = ''
            page_sum = ''
            page_title = ''
            page_categories = ''

            if first_research != '':
                print('LA PREMIERE RECHERCHE EST: ' + str(first_research))
                wikiKeywords = first_research
                #first_research = str(first_research)
                wikiLinkResponse = wikiLink(first_research, language)
                page_url = wikiLinkResponse[0]
                page_sum = wikiLinkResponse[1]
                page_title = wikiLinkResponse[3]
                page_categories = wikiLinkResponse[4]

            #Wikipedia
            if page_url == "":
                if str_final_keyword != "":
                    print('LA DEUXIEME RECHERCHE EST: ' + str_final_keyword)
                    wikiKeywords = str_final_keyword
                    wikiLinkResponse = wikiLink(str_final_keyword, language)
                    page_url = wikiLinkResponse[0]
                    page_sum = wikiLinkResponse[1]
                    page_title = wikiLinkResponse[3]
                    page_categories = wikiLinkResponse[4]


            if page_url == "":
                if most_repeat != 0:
                    print('LA TROISIEME RECHERCHE EST: ' + str_final_keyword)
                    wikiKeywords = str_final_keyword
                    str_final_keyword = str(final_keyword)
                    wikiLinkResponse = wikiLink(str_final_keyword, language)
                    page_url = wikiLinkResponse[0]
                    page_sum = wikiLinkResponse[1]
                    page_title = wikiLinkResponse[3]
                    page_categories = wikiLinkResponse[4]


        page_sum = page_sum[:550]

        json_to_dumps = {'url': org_url, 'youtubeKeywords': str_final_keyword, 'wikiKeywords': wikiKeywords,'wikiURL': page_url, 'wikiSummary': page_sum, 'wikiSuggestion': page_links, 'wikiTitle': page_title, 'category': page_categories }

        print(json_to_dumps)

        json_file = json.dumps(json_to_dumps)

        return JsonResponse("The result is:" + json_file,safe=False)

    except ValueError as e:
        return Response(e.args[0],status.HTTP_400_BAD_REQUEST)