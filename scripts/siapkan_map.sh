#!/bin/bash
# Gunakan: bash scripts/siapkan_map.sh /path/map.osm [--with-tls]
# --with-tls: tambah traffic light otomatis di persimpangan besar

OSM_FILE="$1"
ADD_TLS="${2:-}"

if [ -z "$OSM_FILE" ]; then
    echo "Gunakan: bash scripts/siapkan_map.sh /path/map.osm [--with-tls]"
    exit 1
fi

PROJECT_DIR="$(dirname "$(dirname "$(readlink -f "$0")")")"
OUT_DIR="$PROJECT_DIR/sim/$(basename "$OSM_FILE" .osm)"

mkdir -p "$OUT_DIR"

echo "1. Convert OSM ke SUMO network..."
netconvert --osm-files "$OSM_FILE" \
    -o "$OUT_DIR/network.net.xml" \
    --geometry.remove \
    --roundabouts.guess \
    --ramps.guess \
    --junctions.join \
    --tls.guess-signals \
    --tls.discard-simple \
    --tls.default-type actuated

if [ "$ADD_TLS" = "--with-tls" ]; then
    echo "   Tambah traffic light otomatis di persimpangan besar..."
    python3 "$PROJECT_DIR/scripts/add_tls_to_network.py" "$OUT_DIR/network.net.xml"
fi

echo "2. Generate rute kendaraan random..."
RANDOM_TRIPS="/usr/share/sumo/tools/randomTrips.py"
if [ ! -f "$RANDOM_TRIPS" ]; then
    # Cari alternative path
    RANDOM_TRIPS="$(python3 -c "
import traci, os
p = os.path.dirname(os.path.dirname(traci.__file__))
print(os.path.join(p, 'tools', 'randomTrips.py'))
" 2>/dev/null)"
fi

python3 "$RANDOM_TRIPS" \
    -n "$OUT_DIR/network.net.xml" \
    -o "$OUT_DIR/trips.xml" \
    -r "$OUT_DIR/routes.xml" \
    --begin 0 --end 1800 --period 1.0 \
    --validate

echo "3. Buat config simulasi..."
cat > "$OUT_DIR/test.sumocfg" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <input>
        <net-file value="network.net.xml"/>
        <route-files value="routes.xml"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="1800"/>
    </time>
    <processing>
        <time-to-teleport value="120"/>
    </processing>
</configuration>
EOF

echo ""
echo "✅ Selesai! Buka app, pilih map '$OUT_DIR' dari dropdown."
echo "   Atau Browse langsung ke: $OUT_DIR/test.sumocfg"
