.PHONY: all download

all: download

GITHUB_HOST ?= github.com

coco.names:
	wget "https://huggingface.co/spaces/zhiqwang/assets/resolve/main/coco.names"

yolov5s.pt:
	wget 'https://${GITHUB_HOST}/ultralytics/yolov5/releases/download/v6.0/yolov5s.pt'

download: coco.names yolov5s.pt

clean:
	rm -rf *.pt *.names
