STACK_NAME=ppp-bangalore-chalice-demo
S3_BUCKET=alapinski-development-bucket
S3_PREFIX=chalice_packages/chalice-demo
CFN_DIR=./.cfn/packages
TEMPLATE_JSON_FILE="${CFN_DIR}/sam.json"
TEMPLATE_YAML_FILE="${CFN_DIR}/packaged.yaml"
TIMESTAMP=$(shell date +%s)

RED=\033[0;31m
GREEN=\033[0;32m
CYAN=\033[0;36m
CHECK=\xE2\x9C\x94
NC=\033[0m # No Color

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: update-package package-chalice package-cloudformation package deploy

update-package: ## Update chalice package (removing botocore)
	@echo "${CYAN}Removing botocore from package${NC}"
	@zip -d $(shell ls -Art ./.cfn/packages/*.zip | head -n 1) "botocore*/*"
	@echo "${GREEN}DONE${CHECK}${NC}\n"

package-chalice: ## Package project via Chalice
	@echo "${CYAN}Packaging Lambda Code${NC}"
	@pyenv exec chalice package ${CFN_DIR}
	@echo "${GREEN}DONE${CHECK}${NC}\n"

package-cloudformation: ## Package Project via CloudFormation (Last Step)
	@echo "${CYAN}Packaging Cloudformation Config${NC}"
	@aws cloudformation package \
		--template-file ${TEMPLATE_JSON_FILE} \
		--s3-bucket ${S3_BUCKET} \
		--s3-prefix ${S3_PREFIX} \
		--output-template-file ${TEMPLATE_YAML_FILE}
	@echo "${GREEN}DONE${CHECK}${NC}\n"

package: package-chalice update-package package-cloudformation ## Meta-task to complete all packaging
	git tag $(TIMESTAMP)-package

deploy: ## Deploy a completed cloudformation & chalice package to AWS
	@echo "${CYAN}Deploying Cloudformation & Lambda Code${NC}"
	@aws cloudformation deploy \
		--template-file ${TEMPLATE_YAML_FILE} \
		--stack-name ${STACK_NAME} \
		--capabilities CAPABILITY_IAM
	@git tag $(TIMESTAMP)-deploy
	@echo "${GREEN}DONE${CHECK}${NC}\n"

update: package deploy gp ## Meta-task for package, deploy & update git
	
.PHONY: lint test test-cov test-cov-report test-cov-html
test: test-unit test-int ## Run all tests (unit & integration)

test-unit: ## Run just the isolated unit tests
	@echo "${CYAN}### Excuting UNIT Tests ###${NC}"
	POWERTOOLS_TRACE_DISABLED=1 \
	IS_LOCAL=true \
		pyenv exec pytest \
			--cov=. \
			--cov-report html \
			--cov-report xml \
			./tests/unit/
	@echo "${GREEN}DONE${CHECK}${NC}\n"

test-int: ## Run just the integration tests
	@echo "${CYAN}### Excuting Integration Tests ###${NC}"
	POWERTOOLS_TRACE_DISABLED=1 \
	IS_LOCAL=true \
		pyenv exec pytest --cov=. ./tests/integration/
	@echo "${GREEN}DONE${CHECK}${NC}\n"

lint: ## Run 'black', 'pyre' & 'pyflakes' to lint python code
	@echo "Executing ${CYAN}'black'${NC}"
	@pyenv exec black . 
	@echo "${GREEN}DONE${CHECK}${NC}\n"
	@echo "Executing ${CYAN}'pyre'${NC}"
	@pyenv exec pyre
	@echo "${GREEN}DONE${CHECK}${NC}\n"
	@echo "Executing ${CYAN}'pyflakes'${NC}"
	@pyenv exec pyflakes .
	@echo "${GREEN}DONE${CHECK}${NC}\n"
	

gp: ## Push tags & Code to github remote
	@echo "${CYAN}Updating Github${NC}"
	@git push origin main
	@git push origin --tags
	@echo "${GREEN}Sent code & tags to Github${CHECK}${NC}\n"



