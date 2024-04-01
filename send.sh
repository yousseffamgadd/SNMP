#!/bin/bash

recipient="youssefamgad462@gmail.com"
subject="Threshold exceeded"

body="Subject: $subject\n\n"
body+="Please take rest and return soon.\n\nRegards,\nManager"

echo -e "$body" | ssmtp "$recipient"

