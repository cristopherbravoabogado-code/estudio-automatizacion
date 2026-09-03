# motor/

Codigo de generacion de video. Ver `docs/ARQUITECTURA.md`.

## Archivos esperados

```
arte.py            ilustracion plana (personas, objetos)
escenas.py         composicion de las 5 escenas
render5.py         motor ilustrado v5
render6.py         motor hibrido (cine + ilustracion)
musica.py          sintetizador clasico (sobrio, lofi)
moderna.py         sintetizador moderno (phonk, trap, reggaeton, pop)
voz2.py            TTS local de respaldo (Piper VITS)
producir_todo.py   orquestador lote 1
producir_lote2.py  orquestador lote 2
tanda.sh           render por tandas en primer plano
requirements.txt   dependencias Python
```

## Entorno

```bash
pip install -r requirements.txt
sudo apt-get install -y ffmpeg fonts-noto-color-emoji
# Poppins: descargar de Google Fonts a ./fonts/
```

## Variables de entorno (nunca en el codigo)

| Variable | Para que |
|---|---|
| `ELEVENLABS_API_KEY` | voz Cristian Cornejo / Catalina |
| `HIGGSFIELD_API_KEY` | clips de gancho (opcional) |

En GitHub Actions se cargan como Secrets. En local, con un `.env` que el
`.gitignore` ya excluye.
