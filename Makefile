STACK_NAME=ppp-sba-etran-v2
S3_BUCKET=ppbfs-dm-repo
S3_PREFIX=chalice_packages/ppp-sba-etran-v2
CFN_DIR=./.cfn/packages
TEMPLATE_JSON_FILE="${CFN_DIR}/sam.json"
TEMPLATE_YAML_FILE="${CFN_DIR}/packaged.yaml"
TIMESTAMP=$(shell date +%s)

DM_PIPE_BUCKET_NAME=ppbfs-dm-internal-data-pipeline
DM_PIPE_BUCKET_PREFIX=/prod/PPPOrigination

RED=\033[0;31m
GREEN=\033[0;32m
CYAN=\033[0;36m
CHECK=\xE2\x9C\x94
NC=\033[0m # No Color

.PHONY: start-server stop-server
start-server:
	@echo "${CYAN}Starting Local Docker-Compose w/ MSSQL${NC}"
	@docker-compose up -d
	@echo "${GREEN}Ready.....${CHECK}${NC}"

stop-server:
	@echo "${CYAN}Stopping Local Docker-Compose${NC}"
	@docker-compose down
	@echo "${GREEN}DONE${CHECK}${NC}\n"

.PHONY: generate-models
generate-models:
	@echo "${CYAN}Generating Python Models from MSSQL Tables${NC}"
	@./generate-models.sh
	@echo "${GREEN}DONE${CHECK}${NC}\n"

.PHONY: update-package package-chalice package-cloudformation package deploy
update-package:
	@echo "${CYAN}Removing botocore from package${NC}"
	zip -d $(shell ls -Art ./.cfn/packages/*.zip | head -n 1) "botocore*/*"
	@echo "${GREEN}DONE${CHECK}${NC}\n"

package-chalice:
	@echo "${CYAN}Packaging Lambda Code${NC}"
	pyenv exec chalice package ${CFN_DIR}
	@echo "${GREEN}DONE${CHECK}${NC}\n"

package-cloudformation: 
	@echo "${CYAN}Packaging Cloudformation Config${NC}"
	aws cloudformation package \
		--template-file ${TEMPLATE_JSON_FILE} \
		--s3-bucket ${S3_BUCKET} \
		--s3-prefix ${S3_PREFIX} \
		--output-template-file ${TEMPLATE_YAML_FILE}
	@echo "${GREEN}DONE${CHECK}${NC}\n"

package: package-chalice update-package package-cloudformation
	git tag $(TIMESTAMP)-package

deploy:
	@echo "${CYAN}Deploying Cloudformation & Lambda Code${NC}"
	aws cloudformation deploy \
		--template-file ${TEMPLATE_YAML_FILE} \
		--stack-name ${STACK_NAME} \
		--capabilities CAPABILITY_IAM
	git tag $(TIMESTAMP)-deploy
	@echo "${GREEN}DONE${CHECK}${NC}\n"

update: package deploy gp
	
.PHONY: lint test test-cov test-cov-report test-cov-html
test: test-unit test-int

test-unit:
	@echo "${CYAN}### Excuting UNIT Tests ###${NC}"
	POWERTOOLS_TRACE_DISABLED=1 \
	IS_LOCAL=true \
		pyenv exec pytest \
			--cov=. \
			--cov-report html \
			--cov-report xml \
			./tests/unit/
	@echo "${GREEN}DONE${CHECK}${NC}\n"

test-int:
	@echo "${CYAN}### Excuting Integration Tests ###${NC}"
	POWERTOOLS_TRACE_DISABLED=1 \
	IS_LOCAL=true \
		pyenv exec pytest --cov=. ./tests/integration/
	@echo "${GREEN}DONE${CHECK}${NC}\n"

lint:
	pyenv exec black . 
	pyenv exec pyre
	pyenv exec pyflakes .
	

gp:
	@echo "${CYAN}Updating Bitbucket${NC}"
	@git push origin master
	@git push origin --tags
	@echo "${GREEN}Sent code & tags to Bitbucket${CHECK}${NC}\n"

	@echo "${CYAN}Updating Github${NC}"
	@git push github master
	@git push github --tags
	@echo "${GREEN}Sent code & tags to Github${CHECK}${NC}\n"
