#!/usr/bin/bash

cat /data8/network_mount/S/FHIR_json/Mapped_Files/demographic_data.json | jq -c '.[]' > /data8/network_mount/S/FHIR_json/send/demographic_data.ndjson

