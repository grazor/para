clean:
	find -name "index.md" -delete

index:
	python ./.bin/para-index.py
