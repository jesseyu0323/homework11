import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func
from flask import Flask, jsonify

#################################################
# Reflect Tables into SQLAlchemy ORM
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# We can view all of the classes that automap found
Base.classes.keys()

#Inpsector
inspector = inspect(engine)
inspector.get_table_names()

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
year_ago = dt.date(2017, 10, 5) - dt.timedelta(days=365)
active_station = session.query(Measurement.station, func.count(Measurement.tobs)).group_by(Measurement.station).order_by(func.count(Measurement.tobs).desc()).all()
most_active = active_station[0][0]

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
      
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
      
    )
#########################################################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of precipitation for last year"""
# Query for the dates and temperature observations from the last year.
# Convert the query results to a Dictionary using date as the key and tobs as the value.
# Return the JSON representation of your dictionary.
    
    year_ago = dt.date(2017, 10, 5) - dt.timedelta(days=365)
    session = Session(engine)
    score = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > year_ago).order_by(Measurement.date).all()
    return jsonify(score)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of station for last year"""
#  Return a JSON list of stations from the dataset.
    session = Session(engine)
    active_station = session.query(Measurement.station, func.count(Measurement.tobs)).group_by(Measurement.station).order_by(func.count(Measurement.tobs).desc()).all()
    most_active = active_station[0][0]   
    return jsonify(active_station)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperatures for last year"""
#  Return a JSON list of Temperature Observations (tobs) for the previous year.
    session = Session(engine)
    temp_obsv = session.query(Measurement.station, Measurement.date, Measurement.tobs).filter(Measurement.station == most_active).filter(Measurement.date > year_ago).order_by(Measurement.date).all()
    return jsonify(temp_obsv)

#########################################################################################
@app.route("/api/v1.0/average/<start>")
def startdate(start):

 # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    session = Session(engine)
 
    temp_list = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
    
    return jsonify(temp_list)

#########################################################################################
@app.route("/api/v1.0/average/<start>/<end>")
def startdateenddate(start,end):

  # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range. 
    session = Session(engine)
   
    
    temp_list = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
   
    return jsonify(temp_list)


if __name__ == "__main__":
    app.run(debug=True)