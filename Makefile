format:
	# Lint all files in the current directory, and fix any fixable errors.
	# Format all files in the current directory.
	ruff check --fix . && ruff format .