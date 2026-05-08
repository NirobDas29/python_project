#!/usr/bin/env python
import config
from utils import get_weather

print('WEATHER_API_KEY:', repr(config.WEATHER_API_KEY))
print('Calling get_weather...')
result = get_weather(language='en', city='Dhaka')
print('Result:', result)
