.DEFAULT_GOAL ?= create-url
.PHONY: create-url

.PHONY: default
default: create-url ;

help:
	@echo "Name: ${Product}-${Project}"
	@echo "Description: ${Description}"
	@echo ""
	@echo "Available commands:"
	@echo "	build - build ${Product} for ${Project}"
	@echo "	deploy - deploy ${Product} for ${Project} - deploy also run 'build' command"
	@echo "	url - create a shorten url using: make url https://google.com"
	@echo "	---"
	@echo "	delete - delete ${Product} for ${Project}"
	@echo "	clean - clean the build folder and artifacts"

###################### Parameters ######################
Product := url-shortener
Project := asd
Description := ${Product} - ${Project} - zoph.io - ${Env}
CreateUrl := https://s.zoph.io/create/
AppUrl := https://s.zoph.io/t/
AWSRegion := eu-west-1
Env := dev
AlertsRecipient := victor@zoph.io
MinChar := 3
MaxChar := 3
#######################################################

build: clean
	sam build

url:
	@echo '{"long_url": "$(filter-out $@,$(MAKECMDGOALS))"}' | http POST ${CreateUrl}

%:
	@:

deploy: build
	sam deploy \
		-t .aws-sam/build/template.yaml \
		--region ${AWSRegion} \
		--stack-name "${Project}-${Env}" \
		--capabilities CAPABILITY_IAM \
		--resolve-s3 \
		--force-upload \
		--parameter-overrides \
			pAppUrl=${AppUrl} \
			pEnv=${Env} \
			pAWSRegion=${AWSRegion} \
			pMinChar=${MinChar} \
			pMaxChar=${MaxChar} \
			pProjectName=${Project} \
			pDescription='${Description}' \
			pAlertsRecipient='${AlertsRecipient}' \
		--no-fail-on-empty-changeset

delete:
	sam delete --stack-name "${Project}-${Env}"

clean:
	@rm -fr build/
	@rm -fr dist/
	@rm -fr htmlcov/
	@rm -fr site/
	@rm -fr .eggs/
	@rm -fr .tox/
	@rm -fr .aws-sam/
	@find . -name '*.egg-info' -exec rm -fr {} +
	@find . -name '.DS_Store' -exec rm -fr {} +
	@find . -name '*.egg' -exec rm -f {} +
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +
