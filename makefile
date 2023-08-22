json-generator = poetry run python src/generate_base_json.py

shell :
	poetry shell

oki-dict :
	$(json-generator) o2y

yamato-dict :
	$(json-generator) y2o

build :
	poetry build
