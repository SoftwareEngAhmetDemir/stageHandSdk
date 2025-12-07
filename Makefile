.PHONY: create list edit clean install help

# Set your custom directory here
MODEL_DIR = ./llm/models

# Install Python dependencies
install:
	@echo "Installing Python dependencies from requirements.txt..."
	@if [ ! -f "requirements.txt" ]; then \
		echo "Error: requirements.txt not found!"; \
		exit 1; \
	fi
	@pip install -r requirements.txt
	@echo "✓ Dependencies installed successfully!"

# Create a Modelfile with custom name in MODEL_DIR
create:
	@if [ "$(word 2,$(MAKECMDGOALS))" = "" ]; then \
		echo "Usage: make create <modelfile-name>"; \
		echo "Example: make create my_firstModel"; \
		exit 1; \
	fi
	@mkdir -p $(MODEL_DIR)
	@if [ -f "$(MODEL_DIR)/$(word 2,$(MAKECMDGOALS))" ]; then \
		echo "File '$(word 2,$(MAKECMDGOALS))' already exists in $(MODEL_DIR)!"; \
		echo "Use 'make edit $(word 2,$(MAKECMDGOALS))' to modify it or 'make clean $(word 2,$(MAKECMDGOALS))' to remove it."; \
		exit 1; \
	fi
	@echo "Creating modelfile '$(word 2,$(MAKECMDGOALS))' in $(MODEL_DIR)..."; \
	echo "FROM $(word 2,$(MAKECMDGOALS))" > "$(MODEL_DIR)/$(word 2,$(MAKECMDGOALS))"; \
	echo "" >> "$(MODEL_DIR)/$(word 2,$(MAKECMDGOALS))"; \
	echo "SYSTEM You are a mathematics teacher who explains multiplication by breaking it into addition." >> "$(MODEL_DIR)/$(word 2,$(MAKECMDGOALS))"; \
	echo "" >> "$(MODEL_DIR)/$(word 2,$(MAKECMDGOALS))"; \
	echo "MESSAGE user Why is 5*3 equal to 15?" >> "$(MODEL_DIR)/$(word 2,$(MAKECMDGOALS))"; \
	echo "MESSAGE assistant Because it comes from 5+5+5 = 15" >> "$(MODEL_DIR)/$(word 2,$(MAKECMDGOALS))"; \
	echo "" >> "$(MODEL_DIR)/$(word 2,$(MAKECMDGOALS))"; \
	echo "MESSAGE user Why is 7*2 equal to 14?" >> "$(MODEL_DIR)/$(word 2,$(MAKECMDGOALS))"; \
	echo "MESSAGE assistant Because it comes from 7+7 = 14" >> "$(MODEL_DIR)/$(word 2,$(MAKECMDGOALS))"; \
	echo "" >> "$(MODEL_DIR)/$(word 2,$(MAKECMDGOALS))"; \
	echo "PARAMETER temperature 0.7" >> "$(MODEL_DIR)/$(word 2,$(MAKECMDGOALS))"; \
	echo "✓ Modelfile '$(word 2,$(MAKECMDGOALS))' created in $(MODEL_DIR)!"

# List all modelfiles in MODEL_DIR
list:
	@echo "Modelfiles in $(MODEL_DIR):"
	@ls -1 $(MODEL_DIR) 2>/dev/null || echo "No modelfiles found (directory may not exist yet)"

# Edit a modelfile
edit:
	@if [ "$(word 2,$(MAKECMDGOALS))" = "" ]; then \
		echo "Usage: make edit <modelfile-name>"; \
		exit 1; \
	fi
	@if [ ! -f "$(MODEL_DIR)/$(word 2,$(MAKECMDGOALS))" ]; then \
		echo "File '$(word 2,$(MAKECMDGOALS))' doesn't exist in $(MODEL_DIR)!"; \
		echo "Run 'make create $(word 2,$(MAKECMDGOALS))' first."; \
		exit 1; \
	fi
	@code "$(MODEL_DIR)/$(word 2,$(MAKECMDGOALS))" || nano "$(MODEL_DIR)/$(word 2,$(MAKECMDGOALS))" || vi "$(MODEL_DIR)/$(word 2,$(MAKECMDGOALS))"

# Remove a modelfile
clean:
	@if [ "$(word 2,$(MAKECMDGOALS))" = "" ]; then \
		echo "Usage: make clean <modelfile-name>"; \
		exit 1; \
	fi
	@if [ -f "$(MODEL_DIR)/$(word 2,$(MAKECMDGOALS))" ]; then \
		echo "Removing '$(word 2,$(MAKECMDGOALS))' from $(MODEL_DIR)..."; \
		rm -f "$(MODEL_DIR)/$(word 2,$(MAKECMDGOALS))"; \
		echo "✓ File removed!"; \
	else \
		echo "File '$(word 2,$(MAKECMDGOALS))' doesn't exist in $(MODEL_DIR)."; \
	fi

help:
	@echo "Available commands:"
	@echo "  make install        - Install Python dependencies from requirements.txt"
	@echo "  make create <name>  - Create a new modelfile in $(MODEL_DIR)"
	@echo "  make edit <name>    - Edit an existing modelfile"
	@echo "  make list           - List all modelfiles in $(MODEL_DIR)"
	@echo "  make clean <name>   - Remove a modelfile"
	@echo ""
	@echo "Current directory: $(MODEL_DIR)"
	@echo ""
	@echo "Examples:"
	@echo "  make install"
	@echo "  make create my_firstModel"
	@echo "  make edit my_firstModel"
	@echo "  make clean my_firstModel"

# Catch-all target
%:
	@:



#make create my_firstModel
#make edit my_firstModel
#make list
#make clean my_firstModel
#make help
#make install