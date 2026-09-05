#!/bin/bash
# uso: render.sh 901 902 ...  (lee urls/<n>.voz y urls/<n>.hook, deja out/<id>.mp4 y out/log.txt)
cd /home/user
for n in "$@"; do
  id=$(python3 -c "import json;print([p['id'] for p in json.load(open('piezas.json')) if p['id'].startswith('$n')][0])")
  mkdir -p w/$n && cd w/$n
  curl -sf -o voz.mp3 "$(cat ../../urls/$n.voz)" || { echo "$n: fallo voz" >> ../../out/log.txt; cd ../..; continue; }
  curl -sf -o hook.png "$(cat ../../urls/$n.hook)" || { echo "$n: fallo hook" >> ../../out/log.txt; cd ../..; continue; }
  python3 -c "
import json; P=json.load(open('../../piezas.json')); p=[x for x in P if x['id']=='$id'][0]; p['voz']='voz.mp3'; p['hook']='hook.png'; json.dump(p,open('pieza.json','w'),ensure_ascii=False)"
  if python3 ../../motor.py pieza.json ../../out/$id.mp4 >> ../../out/log.txt 2>&1; then echo "$n: OK $(ffprobe -v error -show_entries format=duration -of csv=p=0 ../../out/$id.mp4)s" >> ../../out/log.txt; else echo "$n: FALLO render" >> ../../out/log.txt; fi
  cd ../..
done
echo "RENDER_FIN $*" >> out/log.txt
