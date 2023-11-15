# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine  = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
m = Base.classes.measurement
s = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
#create homepage with available routes listed
def home():
    
    #print the routes
    return (f'Welcome!<br/>'
            f'Available Routes:<br/>'
            f'Precipitation Totals for Previous Year: /api/v1.0/precipitation<br/>'
            f'List of Stations: /api/v1.0/stations<br/>'
            f'Temperature Observations from USC00519281 for Previous Year   : /api/v1.0/tobs<br/>'
            f'Minimum, Average and Maximum Temperature for Date through 2017-08-23: /api/v1.0/YYYY-MM-DD<br/>'
            f"Minimum, Average and Maximum Temperature for Date Range: /api/v1.0/YYYY-MM-DD/YYYY-MM-DD")


@app.route("/api/v1.0/precipitation")
#create route that returns a jsonified dictionary of precipitation totals for the previous year
def prcp():
    
    #create db connection
    session = Session(engine)
    #query the db to gather data
    results = session.query(m.date, \
    m.prcp).filter(m.date >\
    '2016-08-22').order_by(m.date).all()
    #end db connection
    session.close()

    #create empty list to store data
    last_year = []
    #for loop to collect date and corresponding precipitation total and append to empty list
    for date, prcp in results:
         prcp_dict = {}
         prcp_dict[date]=prcp
         last_year.append(prcp_dict)

    #jsonify and print the list 
    return jsonify(last_year)

    
@app.route("/api/v1.0/stations")
#create a route that returns a jsonified list of all stations in the dataset
def stat():
    
    #create db connection
    session = Session(engine)
    #query db to gather data 
    station_q = session.query(s.station).all()
    #end db connection
    session.close()
    
    #format data into a list
    stations_list = list(np.ravel(station_q))

    #jsonify and print the list
    return jsonify(stations_list)
        

@app.route("/api/v1.0/tobs")
#create a route that returns a jsonified list of previous year temperatures 
#from the busiest station.
def tobs_q():
    
    #create db connection
    session = Session(engine)
    #assign station id variable
    station_id = 'USC00519281'
    #query the db to gather data
    tobs_data = session.query(m.tobs).filter\
    (m.date > '2016-08-18').filter\
    (m.station == station_id).all()
    #end db connection
    session.close()
    
    #format data into a list
    tobs_list = list(np.ravel(tobs_data))
    
    #jsonify and print the list
    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
#create variable route that returns a jsonified list of min, avg and max temp 
#for the input start date through the end of the dataset
def temp(start):

    #create db connection
    session = Session(engine)
    #query the db to gather data
    sel = [func.min(m.tobs), func.avg(m.tobs), func.max(m.tobs)]
    query_result = session.query(*sel)\
    .filter(m.date >= start).all()
    #end db connection
    session.close()

    #format data into a list    
    temp_list = list(np.ravel(query_result))

    #print the jsonified list if dates available, otherwise error
    if temp_list[0]:
        return jsonify(temp_list)
    else:
        return jsonify({"error": f"Date {start} outside of range or formatted incorrectly."}), 404



@app.route("/api/v1.0/<start>/<end>")
#create variable route that returns a jsonified list of min, avg and max temp 
#for the input start date through the end of the dataset
def s_e_temp(start, end):
    
    #create db connection
    session = Session(engine)
    #query the db to gather data
    sel = [func.min(m.tobs), func.avg(m.tobs), func.max(m.tobs)]
    s_e_q = session.query(*sel)\
    .filter(m.date >= start)\
    .filter(m.date <= end).all()
    #end db connection
    session.close()
    
    #format data into a list
    temp1_list = list(np.ravel(s_e_q))

    #print jsonified list if dates available, otherwise error
    if end <= '2017-08-23' and start >= '2010-01-01':
        return jsonify(temp1_list)
    else:
        return jsonify({"error": f"Dates {start}/{end} outside of range or formatted incorrectly."}), 404

#run the app
if __name__ == '__main__':
    app.run()