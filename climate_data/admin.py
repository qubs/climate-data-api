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


from django.contrib import admin
from climate_data.models import *


@admin.register(DataType)
class DataTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ("name", "decimals", "data_type")


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ("name", "goes_id")


@admin.register(StationSensorLink)
class StationSensorLinkAdmin(admin.ModelAdmin):
    list_display = ("station", "sensor", "read_frequency", "station_order")
    ordering = ["station", "station_order"]


@admin.register(Reading)
class ReadingAdmin(admin.ModelAdmin):
    list_display = ("read_time", "station", "sensor", "decimal_value_str", "data_source", "qc_processed", "invalid")
    list_filter = ("station", "qc_processed")
    ordering = ["-read_time", "station", "sensor"]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("arrival_time", "goes_id", "data_quality", "data_source", "signal_strength",
                    "recorded_message_length")
    ordering = ["-arrival_time"]
    pass
