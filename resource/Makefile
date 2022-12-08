.PHONY: all download clean

PATHS := ./yolort

all: download

download:
	for p in ${PATHS}; do \
  		$(MAKE) -C $$p download; \
  	 done

clean:
	for p in ${PATHS}; do \
		$(MAKE) -C $$p clean \
  	done
