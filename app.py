from flask import Blueprint , jsonify , request,Flask
from flask_cors import CORS,cross_origin
import numpy as np
import pandas as pd
from neo4j import GraphDatabase
import sklearn
from sklearn.neighbors import NearestNeighbors

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/recomm',methods=['POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def recomm():
    fetch_json= request.get_json()
    name=fetch_json['name']
    city=fetch_json['city']
    # importing data
    uri = "bolt://localhost:7687"
    userName = "neo4j"
    password = "0000"
    user = []
    airline = []
    airline_sentiment = []
    airline_sentiment_confidence = []
    negativereason = []
    negativereason_confidence = []
    retweet_count = []
    adresse = []
    graphDB_Driver  = GraphDatabase.driver(uri, auth=(userName, password))
    cql = 'Match (t)-[:tweetsrc]->(p), (t)-[:tweetdest]->(a) return t.trusted_judgments as trusted_judgments, t.airline_sentiment as airline_sentiment, t.airline_sentiment_confidence as airline_sentiment_confidence, t.negativereason as negativereason, t.negativereason_confidence as negativereason_confidence, t.retweet_count as retweet_count, p.name as user, a.name as airline, p.adresse as adresse'
    with graphDB_Driver.session() as graphDB_Session:
        nodes = graphDB_Session.run(cql)
        for node in nodes:
            user.append(node['user'])
            airline.append(node['airline'])
            airline_sentiment.append(node['airline_sentiment'])
            airline_sentiment_confidence.append(float(node['airline_sentiment_confidence']))
            negativereason.append(node['negativereason'])
            negativereason_confidence.append(node['negativereason_confidence'])
            retweet_count.append(float(node['retweet_count']))
            adresse.append(node['adresse'])
    df = pd.DataFrame()
    df['user'] = user
    df['airline'] = airline
    df['airline_sentiment'] = airline_sentiment
    df['airline_sentiment_confidence'] = airline_sentiment_confidence
    df['negativereason'] = negativereason
    df['negativereason_confidence'] = negativereason_confidence
    df['retweet_count'] = retweet_count
    df['adresse'] = adresse

    # adresse
    for i in df.index:
        if df['adresse'][i] == None:
            df['adresse'][i] = 'Yew York'
        if df['adresse'][i] == 'Lets Play':
            df['adresse'][i] = 'Los Angeles'

    # rating
    rate = []
    for i in df.index:
        score = 0
        if df['airline_sentiment'][i] == 'neutral':
            score = 2*df['airline_sentiment_confidence'][i]*(df['retweet_count'][i]+1)
        if df['airline_sentiment'][i] == 'positive':
            score = 5*df['airline_sentiment_confidence'][i]*(df['retweet_count'][i]+1)
        if df['negativereason'][i] == "Can't Tell":
            score = 1*float(df['negativereason_confidence'][i])*df['airline_sentiment_confidence'][i]*(1/(df['retweet_count'][i]+1))
        if df['negativereason'][i] == "Flight Booking Problems":
            score = 0.9*float(df['negativereason_confidence'][i])*df['airline_sentiment_confidence'][i]*(1/(df['retweet_count'][i]+1))
        if df['negativereason'][i] == "Late Flight":
            score = 0.8*float(df['negativereason_confidence'][i])*df['airline_sentiment_confidence'][i]*(1/(df['retweet_count'][i]+1))
        if df['negativereason'][i] == "Bad Flight":
            score = 0.7*float(df['negativereason_confidence'][i])*df['airline_sentiment_confidence'][i]*(1/(df['retweet_count'][i]+1))
        if df['negativereason'][i] == "Customer Service Issue":
            score = 0.6*float(df['negativereason_confidence'][i])*df['airline_sentiment_confidence'][i]*(1/(df['retweet_count'][i]+1))
        if df['negativereason'][i] == "longlines":
            score = 0.5*float(df['negativereason_confidence'][i])*df['airline_sentiment_confidence'][i]*(1/(df['retweet_count'][i]+1))
        if df['negativereason'][i] == "Damaged Luggage":
            score = 0.4*float(df['negativereason_confidence'][i])*df['airline_sentiment_confidence'][i]*(1/(df['retweet_count'][i]+1))
        if df['negativereason'][i] == "Lost Luggage":
            score = 0.3*float(df['negativereason_confidence'][i])*df['airline_sentiment_confidence'][i]*(1/(df['retweet_count'][i]+1))
        if df['negativereason'][i] == "Flight Attendant Complaints":
            score = 0.2*float(df['negativereason_confidence'][i])*df['airline_sentiment_confidence'][i]*(1/(df['retweet_count'][i]+1))
        if df['negativereason'][i] == "Cancelled Flight":
            score = 0.1*float(df['negativereason_confidence'][i])*df['airline_sentiment_confidence'][i]*(1/(df['retweet_count'][i]+1))
        rate.append(score)
    df['Rating'] = rate

    # build the rating matrix
    sentiment = pd.DataFrame()
    sentiment['user'] = df['user']
    sentiment['airline'] = df['airline']
    sentiment['rating'] = df['Rating']
    ratings = pd.pivot_table(sentiment,values='rating',columns='user',index='airline')
    ratings = ratings.fillna(0)

    #recommandation
    # find the nearest neighbors using NearestNeighbors(n_neighbors=3)
    d= ratings.copy()
    number_neighbors = 3
    knn = NearestNeighbors(metric='cosine', algorithm='brute')
    knn.fit(d.values)
    distances, indices = knn.kneighbors(d.values, n_neighbors=number_neighbors)
    # convert user_name to user_index
    user_index = d.columns.tolist().index(name)
    # t: airline, m: the row number of t in d
    for m,t in list(enumerate(d.index)): 
        # find airlines without ratings by user
        if d.iloc[m, user_index] == 0:
            sim_airlines = indices[m].tolist()
            airline_distances = distances[m].tolist()    
        if m in sim_airlines:
            id_airline = sim_airlines.index(m)
            sim_airlines.remove(m)
            airline_distances.pop(id_airline) 
        # However, if the percentage of ratings in the dataset is very low, there are too many 0s in the dataset. 
        # Some airlines have all 0 ratings and the airlines with all 0s are considered the same airlines by NearestNeighbors(). 
        # Then,even the airline itself cannot be included in the indices. 
        else:
            sim_airlines = sim_airlines[:number_neighbors-1]
            airline_distances = airline_distances[:number_neighbors-1]       
        # airline_similarty = 1 - airline_distance    
        airline_similarity = [1-x for x in airline_distances]
        airline_similarity_copy = airline_similarity.copy()
        nominator = 0
        # for each similar airline
        for s in range(0, len(airline_similarity)):  
            # check if the rating of a similar airline is zero
            if d.iloc[sim_airlines[s], user_index] == 0:
                # if the rating is zero, ignore the rating and the similarity in calculating the predicted rating
                if len(airline_similarity_copy) == (number_neighbors - 1):
                    airline_similarity_copy.pop(s)         
                else:
                    airline_similarity_copy.pop(s-(len(airline_similarity)-len(airline_similarity_copy)))
            # if the rating is not zero, use the rating and similarity in the calculation
            else:
                nominator = nominator + airline_similarity[s]*d.iloc[sim_airlines[s],user_index]
        # check if the number of the ratings with non-zero is positive
        if len(airline_similarity_copy) > 0:   
            # check if the sum of the ratings of the similar airlines is positive.
            if sum(airline_similarity_copy) > 0:
                predicted_r = nominator/sum(airline_similarity_copy)
            else:
                predicted_r = 0
        # if all the ratings of the similar airlines are zero, then predicted rating should be zero
        else:
            predicted_r = 0
        # place the predicted rating into the dataframe
        d.iloc[m,user_index] = predicted_r

    #final result
    r = []
    air = []
    for m,t in list(enumerate(d.index)):
        r.append(df.iloc[m, user_index])
        air.append(t)
    a= pd.DataFrame()
    a['airline'] = air
    a['rating'] = r
    maxa = a["rating"].max()
    a = a.sort_values(by='rating', ascending=False).head(1)
    a= a.set_index('rating')
    predicted_airline = a['airline'][maxa]
    countries = []
    cities = []
    graphDB_Driver  = GraphDatabase.driver(uri, auth=(userName, password))
    cql = 'Match (p)-[:to]->(dest), (p)-[:from]->(src), (p)-[:by]->(air) where src.city="' + city + '" and air.name="' + predicted_airline + '" return dest.name as name, dest.country as country, dest.city as city'
    with graphDB_Driver.session() as graphDB_Session:
        nodes = graphDB_Session.run(cql)
        for node in nodes:
            countries.append(node['country'])
            cities.append(node['city'])
    json = []
    df = pd.DataFrame()
    df['country'] = countries
    df['city'] = cities
    print(predicted_airline)
    for i in df.index:
        dict = {'airline': predicted_airline, 'country': df['country'][i], 'city': df['city'][i]}
        json.append(dict)
    return jsonify(json)

@app.route('/country',methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def getCountry():
    uri = "bolt://localhost:7687"
    userName = "neo4j"
    password = "0000"
    countries = []
    graphDB_Driver  = GraphDatabase.driver(uri, auth=(userName, password))
    cql = 'MATCH (n:Airport) RETURN distinct(n.country) as country'
    with graphDB_Driver.session() as graphDB_Session:
        nodes = graphDB_Session.run(cql)
        for node in nodes:
            countries.append(node['country'])
    json = []
    for i in countries:
        dict = {'country': i}
        json.append(dict)
    return jsonify(json)

@app.route('/city/<string:country>',methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def getCity(country):
    uri = "bolt://localhost:7687"
    userName = "neo4j"
    password = "0000"
    cities = []
    graphDB_Driver  = GraphDatabase.driver(uri, auth=(userName, password))
    cql = 'MATCH (n:Airport) where n.country="' + country + '" RETURN distinct(n.city) as city'
    with graphDB_Driver.session() as graphDB_Session:
        nodes = graphDB_Session.run(cql)
        for node in nodes:
            cities.append(node['city'])
    json = []
    for i in cities:
        dict = {'city': i}
        json.append(dict)
    return jsonify(json)

@app.route('/destination',methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def getTopDest():
    uri = "bolt://localhost:7687"
    userName = "neo4j"
    password = "0000"
    destinations = []
    countries = []
    cities = []
    graphDB_Driver  = GraphDatabase.driver(uri, auth=(userName, password))
    cql = 'Match (p)-[:to]->(dest) return dest.name as name, dest.country as country, dest.city as city'
    with graphDB_Driver.session() as graphDB_Session:
        nodes = graphDB_Session.run(cql)
        for node in nodes:
            destinations.append(node['name'])
            countries.append(node['country'])
            cities.append(node['city'])
    df = pd.DataFrame()
    df['name']= destinations
    df['country'] = countries
    df['city'] = cities
    d= df.groupby('name').count()
    d= d.sort_values(by='country', ascending=False).head(10)
    json = []
    graphDB_Driver  = GraphDatabase.driver(uri, auth=(userName, password))
    for i in d.index:
        cql = 'Match (p)-[:to]->(dest) where dest.name="' + i + '" return dest.name as name, dest.country as country, dest.city as city'
        with graphDB_Driver.session() as graphDB_Session:
            nodes = graphDB_Session.run(cql)
            for node in nodes:
                dict = {'country': node['country'], 'city': node['city']}
        json.append(dict)
    return jsonify(json)

@app.route('/airline',methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def getTopAirline():
    uri = "bolt://localhost:7687"
    userName = "neo4j"
    password = "0000"
    airlines = []
    countries = []
    graphDB_Driver  = GraphDatabase.driver(uri, auth=(userName, password))
    cql = 'Match (p)-[:by]->(air) return air.name as name, air.country as country'
    with graphDB_Driver.session() as graphDB_Session:
        nodes = graphDB_Session.run(cql)
        for node in nodes:
            airlines.append(node['name'])
            countries.append(node['country'])
    df = pd.DataFrame()
    df['name']= airlines
    df['country'] = countries
    d= df.groupby('name').count()
    d= d.sort_values(by='country', ascending=False).head(10)
    json = []
    graphDB_Driver  = GraphDatabase.driver(uri, auth=(userName, password))
    for i in d.index:
        cql = 'Match (p)-[:by]->(air) where air.name="' + i + '" return air.name as name, air.country as country'
        with graphDB_Driver.session() as graphDB_Session:
            nodes = graphDB_Session.run(cql)
            for node in nodes:
                dict = {'name': node['name'], 'country': node['country']}
        json.append(dict)
    return jsonify(json)