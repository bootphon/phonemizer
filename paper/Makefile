build: paper.pdf

paper.pdf: paper.md paper.bib
	docker run --rm --volume $(shell readlink -f .):/data --user $(shell id -u):$(shell id -g) --env JOURNAL=joss openjournals/paperdraft

clean:
	rm -rf paper.pdf auto
