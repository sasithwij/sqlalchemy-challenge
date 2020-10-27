import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


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
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for the dates and precipitation values
    results = session.query(measurement.date, measurement.prcp).\
        order_by(measurement.date).all()

    # Convert to list of dictionaries to jsonify
    prcp_date_list = []

    for date, prcp in results:
        new_dict = {}
        new_dict[date] = prcp
        prcp_date_list.append(new_dict)

    session.close()

    return jsonify(prcp_date_list)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    station_list = {}
    
    # Query all stations
    results = session.query(station.station, station.name).all()

    for s,name in results:
        station_list[s] = name

    session.close()

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #Get date from one year ago
    last_date = session.query(measurement.date).order_by((measurement.date).desc()).first()
    last_year_date = (dt.datetime.strptime(last_date[0],'%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')
    
    # Query all dates and temps
    results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= last_year_date).\
        order_by(measurement.date).all()

    # Convert to list of dictionaries to jsonify
    tobs_date_list = []

    for date, tobs in results:
        new_dict = {}
        new_dict[date] = tobs
        tobs_date_list.append(new_dict)

    session.close()

    return jsonify(tobs_date_list)

def temprange_start(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #Covert inputed date in to yyyy-mm-dd format
    start_dt = dt.datetime.strptime(start, '%Y-%m-%d')

    temprange_startdate_list = []
    
    # Query all dates from start date and find max min and average temperatures
    results =   session.query(measurement.date,\
                            func.min(measurement.tobs), \
                            func.avg(measurement.tobs), \
                            func.max(measurement.tobs)).\
                            filter(measurement.date >= start_dt).\
                            group_by(measurement.date).all()

    for date, min, avg, max in results:
        new_dict = {}
        new_dict["Date"] = date
        new_dict["TMIN"] = min
        new_dict["TAVG"] = avg
        new_dict["TMAX"] = max
        return_list.append(new_dict)

    session.close()    

    return jsonify(temprange_startdate_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start,end):

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #Covert inputed dates in to yyyy-mm-dd format
    start_dt = dt.datetime.strptime(start, '%Y-%m-%d')
    end_dt = dt.datetime.strptime(end, "%Y-%m-%d")

    temprange_startenddate_list = []
    
    # Query all dates from start date to end date and find max min and average temperatures
    results =   session.query(  measurement.date,\
                                func.min(measurement.tobs), \
                                func.avg(measurement.tobs), \
                                func.max(measurement.tobs)).\
                            filter(and_(measurement.date >= start_dt, measurement.date <= end_dt)).\
                            group_by(measurement.date).all()

    for date, min, avg, max in results:
        new_dict = {}
        new_dict["Date"] = date
        new_dict["TMIN"] = min
        new_dict["TAVG"] = avg
        new_dict["TMAX"] = max
        return_list.append(new_dict)

    session.close()    

    return jsonify(temprange_startenddate_list)



if __name__ == '__main__':
    app.run(debug=True)