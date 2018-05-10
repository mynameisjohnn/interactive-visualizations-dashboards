# Dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
from flask import Flask, jsonify, render_template, request
import csv

# Flask setup
app = Flask(__name__)

# Connect to sqlite database
engine = create_engine("sqlite:///belly_button_biodiversity.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
session = Session(engine)

# Storing tables
Otu = Base.classes.otu
Samples = Base.classes.samples
Samples_Metadata = Base.classes.samples_metadata

# Return the dashboard homepage
@app.route("/")
def home():
    return render_template("index.html")

# Return list of sample names
@app.route("/names")
def names():
    sample_ids = []
    results = session.query(Samples_Metadata.SAMPLEID)
    for result in results:
        sample_ids.append("BB_" + str(result[0]))
    return jsonify(sample_ids)

# Return a list of OTU descriptions
@app.route("/otu")
def otu():
    otu_desc = [] 
    results = session.query(Otu.lowest_taxonomic_unit_found)
    for result in results:
        otu_desc.append(result[0])
    return jsonify(otu_desc)

# Return a json of sample metadata
@app.route("/metadata/<sample>")
def metadata(sample):   
    sample_id = int(sample.split("_")[1])
    sample_metadata = {}
    samples = session.query(Samples_Metadata)
    for info in samples:
        if (sample_id == info.SAMPLEID):
            sample_metadata["AGE"] = info.AGE
            sample_metadata["BBTYPE"] = info.BBTYPE
            sample_metadata["ETHNICITY"] = info.ETHNICITY
            sample_metadata["GENDER"] = info.GENDER
            sample_metadata["LOCATION"] = info.LOCATION
            sample_metadata["SAMPLEID"] = info.SAMPLEID
    return jsonify(sample_metadata)

# Return an integer value for the washing frequency
@app.route("/wfreq/<sample>")
def wfreq(sample):
    sample_id = int(sample.split("_")[1])
    results = session.query(Samples_Metadata)
    for result in results:
        if (sample_id == result.SAMPLEID):
            wfreq = result.WFREQ
    return jsonify(wfreq)

# Return a list of dictionaries containing sorted lists for 'otu_ids' and 'sample_values'
@app.route("/samples/<sample>")
def samples(sample):
    sample_query = "Samples." + sample
    samples_info = {}
    otu_ids = []
    sample_values = []
    results = session.query(Samples.otu_id, sample_query).order_by(desc(sample_query))
    for result in results:
        otu_ids.append(result[0])
        sample_values.append(result[1])
    samples_info = {
        "otu_ids": otu_ids,
        "sample_values": sample_values
    }
    return jsonify(samples_info) 
if __name__ == "__main__":
    app.run(debug=True)