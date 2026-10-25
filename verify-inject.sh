#!/bin/bash
# verify hosted page injects a usable key against live endpoints (no var assignments: redaction-safe)
set -u
B=https://bible.e8digitalmedia.com
rm -f /tmp/vk.txt
curl -4 -s --max-time 20 $B/ | grep -o 'HB_DEFAULT_KEY = "[0-9a-f]\{64\}"' | cut -d'"' -f2 > /tmp/vk.txt
echo "extracted key len: $(tr -d '\n' < /tmp/vk.txt | wc -c)"
echo "placeholder left in page (want 0): $(curl -4 -s --max-time 20 $B/ | grep -c '__HB_KEY__')"
echo "voices  w/ key: $(curl -4 -s -o /dev/null -w '%{http_code}' --max-time 15 "$B/voices?key=$(cat /tmp/vk.txt)")"
echo "api     w/ key: $(curl -4 -s -o /dev/null -w '%{http_code}' --max-time 15 "$B/api/data/web/GEN/1?key=$(cat /tmp/vk.txt)")"
echo "tts     w/ key: $(curl -4 -s -o /dev/null -w '%{http_code} %{size_download}B' --max-time 60 "$B/tts?text=Verify%20injection&key=$(cat /tmp/vk.txt)")"
echo "voices  no key: $(curl -4 -s -o /dev/null -w '%{http_code}' --max-time 15 $B/voices)"
rm -f /tmp/vk.txt
