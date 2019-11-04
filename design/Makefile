IMAGES := subscription_erd.png

all: design.html

design.html: design.md ${IMAGES}
	pandoc $< --template github-template.css -o $@

%.png: %.dot
	twopi -Tpng $< -o $@

.PHONY: clean
clean:
	@rm -rf design.html ${IMAGES}
	
