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
from nltk.corpus import stopwords
import wikipedia
from api.functions import wikiLink, getStopWord, firstMaj
from langdetect import detect


@api_view(["POST"])
def firstWikiLink(article_json):
    try:
        embedly_url=json.loads(article_json.body.decode('utf-8'))
        
        page_url = ''
        page_links = ''
        page_sum = ''
        page_title = ''
        str_final_keyword = ''
        page_categories = ''
        check = True
        wikiKeywords = ''
        lst_wikiKeywords = []
        lst_youtubeKeywords = []
        checkLanguage = True
        
        contenu = embedly_url['content']
        
        description = embedly_url['description']
        title = embedly_url['title']
        org_url = embedly_url['original_url']
        
        if contenu is None:
            check = False
            
        if check == True:
            
            lang = detect(contenu)
            
            print('La langue est : ' + lang)
            
            if lang == 'fr' or lang == 'en':
                
                print('Le titre : ' + title)
                print('La description : ' + description)
                
                description = str.replace(description, '...', '.')
                title = str.replace(title, '...', '.')

                lst_keyword = []
                tokenizer = RegexpTokenizer(r'\w+')

                #Titre Majuscule
                tokens = tokenizer.tokenize(title)
                
                lst_word_no_take = []
                
                #######################delete words after dots for description and title#####################
                
                
                ############Description
                word_split_dot = description.split('.')

                word_split_space = description.split(' ')
                lst_word_no_take.append(word_split_space[0])
                
                count_word_split_dot = 0
                lenDes = len(description)

                m = 0
                
                for h in description:
                    m += 1
                    if h == ".":
                        if m != lenDes:
                            word_split_space = word_split_dot[count_word_split_dot + 1].split(' ')
                            count_word_split_dot += 1
                            lst_word_no_take.append(word_split_space[1])
                
                ############title
                word_split_dot = title.split('.')
                
                word_split_space = title.split(' ')
                lst_word_no_take.append(word_split_space[0])
                
                count_word_split_dot = 0
                lenDes = len(title)
                
                m = 0
                
                for h in title:
                    m += 1
                    if h == ".":
                        if m != title:
                            word_split_space = word_split_dot[count_word_split_dot + 1].split(' ')
                            count_word_split_dot += 1
                            lst_word_no_take.append(word_split_space[1])
                
                
                ##############################

                if lang == 'fr':
                    fr_stop = getStopWord(lang)
                    language = 'fr'
                else:
                    fr_stop = getStopWord(lang)
                    language = 'en'

                stopped_tokens_title = [i for i in tokens if not i in fr_stop]
                
                i = len(stopped_tokens_title)

                counter = 0
                word_found = False

                #Title Majuscule
                while counter != (i -1):
                    for k in stopped_tokens_title[counter]:
                        if k.lower() != k:
                            for g in stopped_tokens_title[counter + 1]:
                                if g.lower() != g:
                                    lst_keyword.append(stopped_tokens_title[counter] + ' ' + stopped_tokens_title[counter + 1] + ';')
                                    break
                                else:
                                    for wordFirstMaj in lst_word_no_take:
                                        if stopped_tokens_title[counter] == wordFirstMaj:
                                                word_found = True
                                    if word_found == False:
                                        lst_keyword.append(stopped_tokens_title[counter] + ';')
                                        break
                    counter = counter + 1
                    word_found = False

                counter = 0
                word_found = False

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
                                    break
                                else:
                                    for wordFistMaj in lst_word_no_take:
                                        if stopped_tokens[counter] == wordFistMaj:
                                                word_found = True
                                    if word_found == False:
                                        print('Le mot a rajouter est 1: ' + stopped_tokens[counter])
                                        lst_keyword.append(stopped_tokens[counter] + ';')
                                        break
                                    word_found = False
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
                            break
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
                    
                print('La nouvelle liste de keyword est : ' + str(lst_keyword))

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
                    lst_youtubeKeywords = keyword
                else:
                    str_final_keyword = str(final_keyword)
                    lst_youtubeKeywords = final_keyword


                page_url = ''
                page_links = ''
                page_sum = ''
                page_title = ''
                page_categories = ''

                if first_research != '':
                    print('LA PREMIERE RECHERCHE EST: ' + str(first_research))
                    wikiKeywords = first_research
                    lst_wikiKeywords = lst_wordMostRepeat
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
                        lst_wikiKeywords = lst_youtubeKeywords
                        wikiLinkResponse = wikiLink(str_final_keyword, language)
                        page_url = wikiLinkResponse[0]
                        page_sum = wikiLinkResponse[1]
                        page_title = wikiLinkResponse[3]
                        page_categories = wikiLinkResponse[4]


                if page_url == "":
                    if most_repeat != 0:
                        print('LA TROISIEME RECHERCHE EST: ' + str(lst_wordMostRepeat))
                        #wikiKeywords = str_final_keyword
                        wikiKeywords = str(lst_wordMostRepeat)
                        lst_wikiKeywords = lst_youtubeKeywords
                        wikiLinkResponse = wikiLink(wikiKeywords, language)
                        page_url = wikiLinkResponse[0]
                        page_sum = wikiLinkResponse[1]
                        page_title = wikiLinkResponse[3]
                        page_categories = wikiLinkResponse[4]


        page_sum = page_sum[:410]

        json_to_dumps = {'url': org_url, 'youtubeKeywords': lst_youtubeKeywords, 'wikiKeywords': lst_wikiKeywords,'wikiURL': page_url, 'wikiSummary': page_sum, 'wikiSuggestion': page_links, 'wikiTitle': page_title, 'category': page_categories }

        print(json_to_dumps)

        json_file = json.dumps(json_to_dumps)

        return JsonResponse(json_file,safe=False)

    except ValueError as e:
        return Response(e.args[0],status.HTTP_400_BAD_REQUEST)
