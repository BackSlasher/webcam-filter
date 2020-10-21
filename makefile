.PHONY: run setup

setup:
	virtualenv . --system-site-packages
	bin/pip install -r requirements.txt

run:
	bin/python webcamfilter
