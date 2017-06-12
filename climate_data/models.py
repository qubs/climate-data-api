# Copyright 2016 the Queen's University Biological Station

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from django.db import models
from django.contrib.postgres.fields import ArrayField


class DataType(models.Model):
    """
    A model of reading's data type. There may be multiple sensors which share a single data type; for example,
    temperature.
    """

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=20, db_index=True)  # For downloaded data, the full name would be unwieldy

    unit = models.CharField(max_length=40)  # Example: celcius.

    def __repr__(self):
        return "<DataType {} ({})>".format(self.name, self.short_name)

    def __str__(self):
        return self.name


class Sensor(models.Model):
    """
    A model of a specific class of sensor attached to various stations. Many stations share similar sensors. This model 
    is used to keep track of data format, since sensors may return different formats for the same data type.
    
    A data type for the sensor to refer to should exist before sensor creation. The foreign key is nullable for
    backwards compatibility reasons.
    """

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=100)
    data_id = models.CharField(max_length=20)  # DEPRECATED

    decimals = models.PositiveSmallIntegerField()  # Data points are sent without decimals; they need to be adjusted.

    # Foreign Keys
    data_type = models.ForeignKey(DataType, on_delete=models.CASCADE, null=True)

    def __repr__(self):
        return "<Sensor {}>".format(self.name)

    def __str__(self):
        return self.name


class Station(models.Model):
    """
    A model representing a climate_data station. Climate stations are effectively a list of sensors with an attached GOES ID.
    """

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=100)
    goes_id = models.CharField(max_length=8)

    # Foreign keys
    sensors = models.ManyToManyField(Sensor, through="StationSensorLink", related_name="stations")

    def __repr__(self):
        return "<Station {} | GOES ID: {}>".format(self.name, self.goes_id)

    def __str__(self):
        return self.name


class StationSensorLink(models.Model):
    """
    A model representing many-to-many links between stations and common sensor classes.
    """

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    station_order = models.PositiveSmallIntegerField()  # Need to keep an order for sensors to parse message data.
    read_frequency = models.PositiveSmallIntegerField(default=4)  # Default to 4 times per message.

    # Foreign Keys
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)

    def __repr__(self):
        return "<Link | Station: {}, Sensor: {}>".format(self.station, self.sensor)

    def __str__(self):
        return "Link between station {} and sensor {}".format(self.station, self.sensor)

    class Meta:
        ordering = ("station_order",)


class Reading(models.Model):
    """
    A model representing an individual point of data from a specific station, sensor, and with a specific read time.
    """

    FROM_GOES = "G"
    FROM_DEVICE_LOG = "L"

    DATA_SOURCE_CHOICES = (
        (FROM_GOES, "Retrieved from GOES satellite message"),
        (FROM_DEVICE_LOG, "Retrieved from station data log"),
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    read_time = models.DateTimeField(db_index=True)
    data_source = models.CharField(max_length=1, choices=DATA_SOURCE_CHOICES, default=FROM_GOES)

    value = models.IntegerField(null=True)

    qc_processed = models.BooleanField(default=False)
    invalid = models.BooleanField(default=False)

    # Foreign keys
    sensor = models.ForeignKey("Sensor", on_delete=models.SET_NULL, null=True)  # We can get data type from sensor.
    station = models.ForeignKey("Station", on_delete=models.SET_NULL, null=True)
    message = models.ForeignKey("Message", on_delete=models.SET_NULL, null=True)

    def __repr__(self):
        return "<Reading | Value: {}, Time: {}, Station: {}>".format(self.value, self.read_time, self.station)

    def __str__(self):
        return "Reading '{}' at {} from station {}".format(self.value, self.read_time, self.station)


class Message(models.Model):
    """
    A model representing a DCP message retrieved from a GOES satellite.
    See http://eddn.usgs.gov/dcpformat.html for format details.
    """

    NORMAL = "N"

    LOW = "L"
    HIGH = "H"

    FAIR = "F"
    POOR = "P"

    EAST = "E"
    WEST = "W"

    MODULATION_INDEX_CHOICES = (
        (NORMAL, "Normal (60 degrees +/- 5)"),
        (LOW, "Low (50 degrees)"),
        (HIGH, "High (70 degrees)"),
    )

    DATA_QUALITY_CHOICES = (
        (NORMAL, "Normal (error rate < 10^-6)"),
        (FAIR, "Fair (10^-6 < error rate < 10^-4)"),
        (POOR, "Poor (error rate > 10^-4)"),
    )

    GOES_SPACECRAFT_CHOICES = (
        (EAST, "East"),
        (WEST, "West"),
    )

    # From http://eddn.usgs.gov/dataSourceCodes.html
    DATA_SOURCE_CHOICES = (
        ("LE", "Cincinnati East; USACE LRD Cincinnati"),
        ("d1", "NIFC West Boise ID - Unit 1; NIFC Boise"),
        ("d2", "NIFC West Boise ID - Unit 2; NIFC Boise"),
        ("OW", "Omaha West; USACE NWO"),
        ("RE", "Rock Island East; USACE MVR"),
        ("RW", "Rock Island West; USACE MVR"),
        ("SF", "West Palm Beach East; SFWMD"),
        ("UB", "Ucom Backup @ WCDA; NOAA Wallops CDA"),
        ("UP", "Ucom Primary @ WCDA; NOAA Wallops CDA"),
        ("XE", "Sioux Falls, East; USGS EROS"),
        ("XW", "Sioux Falls, West; USGS EROS"),
        ("XL", "Sioux Falls, LRIT; USGS EROS"),
        ("RL", "Reston, LRIT; Reston, Virginia"),
        ("FF", "Unknown 1"),
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    goes_id = models.CharField(max_length=8, db_index=True)
    goes_channel = models.PositiveSmallIntegerField()
    goes_spacecraft = models.CharField(max_length=1, choices=GOES_SPACECRAFT_CHOICES, default=EAST)

    arrival_time = models.DateTimeField()
    failure_code = models.CharField(max_length=1)

    signal_strength = models.PositiveSmallIntegerField()
    frequency_offset = models.CharField(max_length=2)
    modulation_index = models.CharField(max_length=1, choices=MODULATION_INDEX_CHOICES, default=NORMAL)

    data_quality = models.CharField(max_length=1, choices=DATA_QUALITY_CHOICES, default=NORMAL)
    data_source = models.CharField(max_length=2, choices=DATA_SOURCE_CHOICES)

    recorded_message_length = models.PositiveSmallIntegerField()

    values = ArrayField(models.IntegerField(null=True))
    message_text = models.TextField()

    # Foreign keys
    station = models.ForeignKey("Station", on_delete=models.SET_NULL, null=True)

    def __repr__(self):
        return "<Message | GOES ID: {}, Arrival Time: {}>".format(self.goes_id, self.arrival_time)

    def __str__(self):
        return "Message from {} at {}".format(self.goes_id, self.arrival_time)


class Setting(models.Model):
    """
    A model for storing key-value setting pairs.
    """

    updated = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=63)
    value = models.TextField()
