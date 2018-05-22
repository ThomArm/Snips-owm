#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import ConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
from snipsowm.snipsowm import SnipsOWM
import io
import math
import datetime as dt
from dateutil.parser import parse

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

class SnipsConfigParser(ConfigParser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, ConfigParser.Error) as e:
        return dict()

def subscribe_intent_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper(hermes, intentMessage, conf)


def action_wrapper(hermes, intentMessage, conf):
    """ Write the body of the function that will be executed once the intent is recognized. 
    In your scope, you have the following objects : 
    - intentMessage : an object that represents the recognized intent
    - hermes : an object with methods to communicate with the MQTT bus following the hermes protocol. 
    - conf : a dictionary that holds the skills parameters you defined 

    Refer to the documentation for further details. 
    """ 
      # Determine datetime
    datetime = None
    if snips.intent.forecast_start_datetime:
    	datetime = snips.intent.forecast_start_datetime[0]

    if isinstance(datetime, snips.types.InstantTime):
    	datetime = (datetime.datetime).replace(tzinfo=None)
    elif isinstance(datetime, snips.types.TimeInterval):
        datetime = (datetime.end).replace(tzinfo=None)

    # Determine granularity
   	granularity = None
   	if datetime:  # We have an information about the date.
   		now = dt.datetime.now().replace(tzinfo=None)
        delta_days = abs((datetime - now).days)
        if delta_days > 10: # There a week difference between today and the date we want the forecast.
        	granularity = 2 # Give the day of the forecast date, plus the number of the day in the month.
        elif delta_days > 5: # There a 10-day difference between today and the date we want the forecast.
          	granularity = 1 # Give the full date
        else:
          	granularity = 0 # Just give the day of the week
   	else:
   		granularity = 0

    locality = None
    try:
    	locality = snips.intent.forecast_locality \
    		or snips.intent.forecast_country \
        	or snips.intent.forecast_region \
          	or snips.intent.forecast_geographical_poi

        if locality:
        	locality = locality[0]
    except Exception:
    	pass

   	snips.skill.speak_temperature(snips, locality, datetime, granularity)

    current_session_id = intentMessage.session_id
    hermes.publish_end_session(current_session_id, result_sentence)


if __name__ == "__main__":
    with Hermes("localhost:1883") as h:
        h.subscribe_intent("searchWeatherForecastTemperature", subscribe_intent_callback) \
.start()
