.DEFAULT_GOAL ?= url
.PHONY: url

.PHONY: default
default: help ;

help:
	@echo "Name: ${Product}-${Project}"
	@echo "Description: ${Description}"
	@echo "Credits: zoph.io - https://zoph.io"
	@echo ""
	@echo "Available commands:"
	@echo "	build - build artifacts ${Product} for ${Project}"
	@echo "	deploy - deploy ${Product} for ${Project} - deploy also run 'build' command"
	@echo "	setup_front - setup the frontend static website for ${Product} for ${Project}"
	@echo "	url - create a shorten url using: make url 'https://google.com'"
	@echo "	---"
	@echo "	delete - delete ${Product} for ${Project}"
	@echo "	clean - clean the build folder and artifacts"

###################### Parameters ######################
Product := url-shortener
Project := <REPLACE_ME>
Environment := prod
Description := ${Product} - ${Project} - ${Environment}

# Shortener Configuration
MinChar := 3
MaxChar := 3

# DNS
Domain := <REPLACE_ME>
SubDomain := <REPLACE_ME>
# Existing Route53 ZoneId
HostedZoneId := <REPLACE_ME>
FallbackUrl := https://zoph.io # <REPLACE_ME>

# Certificate (wildcard in us-east-1)
CertificateArn := <REPLACE_ME>

# Shortener region
AWSRegion := eu-west-1

# Monitoring
AlertsRecipient := <REPLACE_ME>
#######################################################
DistributionId := $(shell aws cloudfront list-distributions --query 'DistributionList.Items[?Origins.Items[0].DomainName==`short.${Domain}.s3.${AWSRegion}.amazonaws.com`].Id | [0]' --output text)

build: clean
	sam build

url:
	@echo '{"long_url": "$(filter-out $@,$(MAKECMDGOALS))"}' | http POST https://${SubDomain}.${Domain}/create


# Used to pass parameters directly with makefile (ie: make url)
%:
	@:

deploy: build
	sam deploy \
		-t .aws-sam/build/template.yaml \
		--region ${AWSRegion} \
		--stack-name "${Project}-${Product}-${Environment}" \
		--capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND \
		--resolve-s3 \
		--force-upload \
		--parameter-overrides \
			pDomain=${Domain} \
			pSubDomain=${SubDomain} \
			pEnv=${Environment} \
			pAWSRegion=${AWSRegion} \
			pMinChar=${MinChar} \
			pMaxChar=${MaxChar} \
			pProjectName=${Project} \
			pProductName=${Product} \
			pDescription='${Description}' \
			pAlertsRecipient='${AlertsRecipient}' \
			pHostedZoneId=${HostedZoneId} \
			pCertificateArn='${CertificateArn}' \
			pFallbackUrl='${FallbackUrl}' \
		--no-fail-on-empty-changeset
	
setup_front:
	@sed -e "s/\__PLACEHOLDER__/${SubDomain}.${Domain}/" ./frontend/js.js > ./frontend/script.js
	@aws s3 cp ./frontend/index.htm s3://short.${Domain}/
	@aws s3 cp ./frontend/styles.css s3://short.${Domain}/
	@aws s3 cp ./frontend/script.js s3://short.${Domain}/
	@aws s3 cp ./frontend/favicon.ico s3://short.${Domain}/
	@aws cloudfront create-invalidation --distribution-id '${DistributionId}' --path "/*"

delete:
	sam delete --stack-name "${Project}-${Product}-${Environment}"

get_distribution_id:
	@aws cloudfront list-distributions --query 'DistributionList.Items[?Origins.Items[0].DomainName==`short.${Domain}.s3.${AWSRegion}.amazonaws.com`].Id | [0]' --output text

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
