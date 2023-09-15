json-generator = poetry run python src/generate_base_json.py

shell :
	poetry shell

oki-dict :
	$(json-generator) o2y

yamato-dict :
	$(json-generator) y2o

katsuyou-dict:
	poetry run python src/uchinaaguchi_katsuyou_jiten/generate_dictionary.py --format json

build :
	poetry build
